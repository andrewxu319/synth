import logging
from time import sleep
import queue
import sys
from optparse import OptionParser

import numpy as np

from . import settings
from .playback.stream_player import StreamPlayer
from synth.synthesis.signal.sine_wave_oscillator import SineWaveOscillator
from synth.synthesis.signal.square_wave_oscillator import SquareWaveOscillator
from synth.synthesis.signal.sawtooth_wave_oscillator import SawtoothWaveOscillator
from synth.synthesis.signal.triangle_wave_oscillator import TriangleWaveOscillator
from synth.synthesis.signal.noise_generator import NoiseGenerator
from synth.synthesis.signal.gain import Gain
from synth.synthesis.signal.mixer import Mixer
import synth.midi as midi
from synth.midi.midi_listener import MidiListener

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="midi_port", default=None, help="MIDI port to listen on", metavar="MIDI PORT") # python -m synth -p "KOMPLETE KONTROL A49 MIDI 0"
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s [%(levelname)s] %(module)s [%(funcName)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    log = logging.getLogger(__name__)
    log.info("toy synth")

    available_ports = midi.get_available_controllers()
    log.info(f"Available MIDI ports: {available_ports}")

    # Defines components
    osc_a = SineWaveOscillator(settings.sample_rate, settings.frames_per_chunk)
    osc_b = SquareWaveOscillator(settings.sample_rate, settings.frames_per_chunk)
    osc_c = SawtoothWaveOscillator(settings.sample_rate, settings.frames_per_chunk)
    osc_d = TriangleWaveOscillator(settings.sample_rate, settings.frames_per_chunk)
    noise = NoiseGenerator(settings.sample_rate, settings.frames_per_chunk)

    gain_a = Gain(settings.sample_rate, settings.frames_per_chunk, subcomponents=[osc_a])
    gain_b = Gain(settings.sample_rate, settings.frames_per_chunk, subcomponents=[osc_b])
    gain_c = Gain(settings.sample_rate, settings.frames_per_chunk, subcomponents=[osc_c])
    gain_d = Gain(settings.sample_rate, settings.frames_per_chunk, subcomponents=[osc_d])
    gain_noise = Gain(settings.sample_rate, settings.frames_per_chunk, subcomponents=[noise])

    mixer = Mixer(settings.sample_rate, settings.frames_per_chunk, subcomponents=[gain_a, gain_b, gain_c, gain_d, gain_noise])

    # PARAMETERS
    osc_a.active = True
    osc_b.active = True
    osc_c.active = True
    osc_d.active = True
    noise.active = False

    gain_a.amp = 1.0
    gain_b.amp = 0.2
    gain_c.amp = 0.6
    gain_d.amp = 0.5
    noise.amp = 0.01

    # Defines a stream player
    stream_player = StreamPlayer(sample_rate=settings.sample_rate, frames_per_chunk=settings.frames_per_chunk, input_delegate=mixer)
    
    listener_mailbox = queue.Queue()
    synth_mailbox = queue.Queue()

    # midi_listen_port = options.midi_port if options.midi_port else settings.auto_attach
    midi_listen_port = available_ports[0]
    log.info(f"Using MIDI port {midi_listen_port}")
    midi_listener = MidiListener(listener_mailbox, synth_mailbox, midi_listen_port)
    
    try:
        stream_player.play()
        midi_listener.start() # The start method starts a new OS thread that then runs the code in that run method.
        current_note = None
        while True:
            if synth_mail := synth_mailbox.get():
                log.info(f"{synth_mail}") # repeat forever. if theres new message from midi controller, log it
                match synth_mail.split(): # only works with mono. make it poly later. maybe make notes_on a list
                    case ["note_on", "-n", note, "-c", channel]:
                        int_note = int(note)
                        freq = midi.frequencies[int_note]
                        osc_a.frequency = float(freq)
                        osc_b.frequency = float(freq)
                        osc_c.frequency = float(freq)
                        osc_d.frequency = float(freq)
                        current_note = note
                    case ["note_off", "-n", note, "-c", channel]:
                        if current_note == note:
                            osc_a.frequency = 0.0
                            osc_b.frequency = 0.0
                            osc_c.frequency = 0.0
                            osc_d.frequency = 0.0
                            current_note = None
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Exiting the program.")
    
    stream_player.stop()
    listener_mailbox.put("exit")
    midi_listener.join() # wait for midi_listener to terminate
    sys.exit(0)