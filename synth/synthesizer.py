# formal version of the stuff we did in __main__.py

import threading
import logging
from queue import Queue
from copy import deepcopy

import numpy as np

from . import midi
from .midi.implementation import Implementation
from .synthesis.voice import Voice
from .synthesis.signal.chain import Chain
from .synthesis.signal.oscillator_library import OscillatorLibrary
# from .synthesis.signal.sine_wave_oscillator import SineWaveOscillator
# from .synthesis.signal.square_wave_oscillator import SquareWaveOscillator
# from .synthesis.signal.sawtooth_wave_oscillator import SawtoothWaveOscillator
# from .synthesis.signal.triangle_wave_oscillator import TriangleWaveOscillator
# from .synthesis.signal.noise_generator import NoiseGenerator
from .synthesis.signal.gain import Gain
from .synthesis.signal.mixer import Mixer
from .playback.stream_player import StreamPlayer

class Synthesizer(threading.Thread): # each synth in separate thread??
    def __init__(self, sample_rate: int, frames_per_chunk: int, mailbox: Queue, num_voices: int=4, device=None) -> None: # mailbox = synth_mailbox
        super().__init__(name="Synthesizer Thread")
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.mailbox = mailbox
        self.num_voices = num_voices
        self.device = device
        self.osc_amp_vals = np.linspace(0, 1, 128)
        self.should_run = True
    
        # Set up the voices
        signal_prototype = self.set_up_signal_chain()
        # self.log.info(f"Signal chain Prototype:\n{str(signal_prototype)}")
        self.voices = [Voice(deepcopy(signal_prototype)) for _ in range(num_voices)]

        # Set up the stream player
        self.stream_player = StreamPlayer(self.sample_rate, self.frames_per_chunk, self.generator(), device=self.device)
    
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
        # match cc_number:
        #     case Implementation.OSC_A_AMP:
        #         self.set_gain(self, "a", gain)
    
    def set_up_signal_chain(self) -> Chain:
        # Defines components
        self.oscillator_library = OscillatorLibrary(self.sample_rate, self.frames_per_chunk)
        self.oscillators = self.oscillator_library.oscillators
        gains = [Gain(self.sample_rate, self.frames_per_chunk, 0.0, subcomponents=[oscillator], control_tag=f"gain_{name}") for name, oscillator in self.oscillators.items()]
        mixer = Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=gains)
        
        # Defines parameters
        self.active_status = {
            "sine_wave_oscillator": False,
            "square_wave_oscillator": False,
            "sawtooth_wave_oscillator": True,
            "triangle_wave_oscillator": False,
            "noise_oscillator": False
        }
        self.amplitude_status = {
            "sine_wave_oscillator": 1.0,
            "square_wave_oscillator": 1.0,
            "sawtooth_wave_oscillator": 0.01,
            "triangle_wave_oscillator": 1.0,
            "noise_oscillator": 1.0
        }

        # self.oscillator_library.oscillators["sine_wave_oscillator"].active = True
        # print("HIHIHIHIHI" + str(self.oscillator_library.oscillators["sine_wave_oscillator"].active))

        for name, oscillator in self.oscillators.items():
            oscillator.active = self.active_status[name]
            print(f"{oscillator.name} active is {oscillator.active}! Executed from synthesizers.py, 106") # ACTIVE CHECK
        for i in range(len(gains)):
            gains[i].amplitude = self.amplitude_status[list(self.amplitude_status)[i]] # gain only has one subcomponent

        # print(self.oscillators)
        # for subcomp in mixer.subcomponents:
        #     print(subcomp.subcomponents[0].active)

        return Chain(mixer) # top most component in the chain is mixer

    def generator(self):
        """
        Generate the signal by mixing the voice outputs
        """
        mixed_next_chunk = np.zeros(self.frames_per_chunk, np.float32)
        num_active_voices = 0
        while True:
            for voice in self.voices:
                if voice.active:
                    mixed_next_chunk += next(voice.signal_chain)
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
        # print([voice if voice.active else "" for voice in self.voices]) # number of active voices
    
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