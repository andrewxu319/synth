# formal version of the stuff we did in __main__.py

import threading
import logging
from queue import Queue
from copy import deepcopy

import numpy as np

from . import midi
from .synthesis.voice import Voice
from .synthesis.signal.chain import Chain
from .synthesis.signal.sine_wave_oscillator import SineWaveOscillator
from .synthesis.signal.square_wave_oscillator import SquareWaveOscillator
from .synthesis.signal.sawtooth_wave_oscillator import SawtoothWaveOscillator
from .synthesis.signal.triangle_wave_oscillator import TriangleWaveOscillator
from .synthesis.signal.noise_generator import NoiseGenerator
from .synthesis.signal.gain import Gain
from .synthesis.signal.mixer import Mixer
from .playback.stream_player import StreamPlayer

class Synthesizer(threading.Thread): # each synth in separate thread??
    def __init__(self, sample_rate: int, frames_per_chunk: int, mailbox: Queue, num_voices: int=4) -> None: # mailbox = synth_mailbox
        super().__init__(name="Synthesizer Thread")
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.mailbox = mailbox
        self.num_voices = num_voices
        self.should_run = True
    
        # Set up the voices
        signal_prototype = self.set_up_signal_chain()
        self.log.info(f"Signal chain Prototype:\n{str(signal_prototype)}")
        self.voices = [Voice(deepcopy(signal_prototype)) for _ in range(self.num_voices)]

        # Set up the stream player
        self.stream_player = StreamPlayer(self.sample_rate, self.frames_per_chunk, self.generator())
    
    def run(self):
        self.stream_player.play()
        while self.should_run and self.stream_player.is_active():
            if message := self.mailbox.get():
                self.message_handler(message)
        return
    
    def message_handler(self, message: str):
        match message.split(): # receiving message as a STRING from midi_listener.py
            case ["exit"]:
                self.log.info("Got exit command.")
                self.stream_player.stop()
                self.should_run = False
            case ["note_on", "-n", note, "-c", channel]:
                int_note = int(note)
                int_channel = int(channel)
                note_name = midi.note_names[int_note]
                self.note_on(int_note, int_channel)
                self.log.info(f"Note on {note_name} ({int_note}), chan {int_channel}")
            case ["note_off", "-n", note, "-c", channel]:
                int_note = int(note)
                int_channel = int(channel)
                note_name = midi.note_names[int_note]
                self.note_off(int_note, int_channel)
                self.log.info(f"Note off {note_name} ({int_note}), chan {int_channel}")
            case ["control_change", "-c", channel, "-n", cc_number, "-v", value]:
                int_channel = int(channel)
                int_cc_number = int(cc_number)
                int_value = int(value)
                self.control_change_handler(int_channel, int_cc_number, int_value)
            case _:
                self.log.info(f"Unknown MIDI message: {message}")
    
    def control_change_handler(self, channel: int, cc_number: int, value: int): # prob j change the volume? go to Chain, search by gain, multiply by value
        self.log.info(f"Control Change: channel {channel}, CC {cc_number}, value {value}")
        # ADD MORE LATER
    
    def set_up_signal_chain(self) -> Chain:
        # Defines components
        osc_a = SineWaveOscillator(self.sample_rate, self.frames_per_chunk)
        osc_b = SquareWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # osc_c = SawtoothWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # osc_d = TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # noise = NoiseGenerator(self.sample_rate, self.frames_per_chunk)

        gain_a = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[osc_a], control_tag="gain_a")
        gain_b = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[osc_b], control_tag="gain_b")
        # gain_c = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[osc_c], control_tag="gain_c")
        # gain_d = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[osc_d], control_tag="gain_d")
        # gain_noise = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[noise], control_tag="gain_noise")

        mixer = Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=[gain_a]) # ouch. shld have all gains
        # parameters aren't defined here. PROBABLY taken elsewhere "synthesizer.signal_prototype.gain_b.amp = 0.8"

        # print(osc_a.active)
        # osc_b.active = False
        # osc_c.active = False
        # osc_d.active = False
        # noise.active = False

        # gain_a.amp = 0.0
        # gain_b.amp = 0.2
        # gain_c.amp = 0.6
        # gain_d.amp = 0.5
        # noise.amp = 0.01

        return Chain(mixer) # top most component in the chain is mixer

    def generator(self):
        """
        Generate the signal by mixing the voice outputs
        """
        mixed_next_chunk = np.zeros(self.frames_per_chunk, np.float32)
        num_active_voices = 0
        while True:
            for i in range(self.num_voices):
                voice = self.voices[i]
                mixed_next_chunk += next(voice.signal_chain)
                if voice.active:
                    num_active_voices += 1
            
            mixed_next_chunk = np.clip(mixed_next_chunk, -1.0, 1.0)

            yield mixed_next_chunk
            mixed_next_chunk = np.zeros(self.frames_per_chunk, np.float32)
            num_active_voices = 0
    
    def note_on(self, note: int, channel: int):
        """
        Set a voice on with the given note.
        If there are no unused voices, drop the voice that has been on for the longest and use that voice
        """
        note_id = self.get_note_id(note, channel)
        freq = midi.frequencies[note]
        for i in range(len(self.voices)):
            voice = self.voices[i]
            if not voice.active:
                voice.note_on(freq, note_id)
                self.voices.append(self.voices.pop(i))
                break
        
            if i == len(self.voices) - 1:
                self.log.info("No unused voices! Dropped the voice in use for the longest.")
                self.voices[0].note_off()
                self.voices[0].note_on(freq, note_id)
                self.voices.append(self.voices.pop(0))
    
    def note_off(self, note: int, channel: int):
        """
        Find the voice playing the given note and turn it off.
        """
        note_id = self.get_note_id(note, channel)
        for voice in self.voices:
            if voice.active and voice.note_id == note_id:
                voice.note_off()
    
    def get_note_id(self, note: int, channel: int):
        """
        Generate an id for a given note and channel
        By hashing the note and channel we can ensure that we are turning off the exact note
        that was turned on
        """
        return hash(f"{note}{channel}")