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
from .synthesis.signal.gain import Gain
from .synthesis.signal.fx.low_pass_filter import LowPassFilter
from .synthesis.signal.fx.delay import Delay
from .synthesis.signal.mixer import Mixer
from .playback.stream_player import StreamPlayer

class Synthesizer(threading.Thread): # each synth in separate thread??
    def __init__(self, sample_rate: int, frames_per_chunk: int, mailbox: Queue, num_voices: int, output_device) -> None: # mailbox = synth_mailbox
        super().__init__(name="Synthesizer Thread")
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.mailbox = mailbox
        self.num_voices = num_voices
        self.should_run = True

        # Preset fx values to avoid doing division every time
        self.amp_values = np.linspace(0, 1, 128)
        self.lpf_cutoff_values = np.logspace(4, 14.3, 128, endpoint=True, base=2, dtype=np.float32)
        self.delay_time_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.5 # 0 to about 2 seconds
        self.delay_feedback_values = (np.logspace(0, 1, 128, endpoint=True, base=10) - 1) / 9 # 0 to 1
    
        # Set up the voices
        signal_prototype = self.set_up_signal_chain()
        self.voices = [Voice(deepcopy(signal_prototype)) for _ in range(num_voices)]

        # Set up the stream player
        self.stream_player = StreamPlayer(self.sample_rate, self.frames_per_chunk, self.generator(), output_device)
    
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
        logging.info(Implementation.OSC_1_AMP.value + 1)
        match cc_number:
            case Implementation.OSC_1_AMP.value:
                self.set_gain(0, value)
                self.log.info(f"Gain 1 set: {value}")
            case Implementation.OSC_2_AMP.value:
                self.set_gain(1, value)
                self.log.info(f"Gain 2 set: {value}")
            case Implementation.OSC_3_AMP.value:
                self.set_gain(2, value)
                self.log.info(f"Gain 3 set: {value}")
            case Implementation.OSC_4_AMP.value:
                self.set_gain(3, value)
                self.log.info(f"Gain 4 set: {value}")
            case Implementation.OSC_5_AMP.value:
                self.set_gain(4, value)
                self.log.info(f"Gain 5 set: {value}")

            case Implementation.LPF_1_CUTOFF.value:
                self.set_lpf_cutoff(0, value)
                self.log.info(f"LPF 1 set: {value}")
            case Implementation.LPF_2_CUTOFF.value:
                self.set_lpf_cutoff(1, value)
                self.log.info(f"LPF 2 set: {value}")
            case Implementation.LPF_3_CUTOFF.value:
                self.set_lpf_cutoff(2, value)
                self.log.info(f"LPF 3 set: {value}")
            case Implementation.LPF_4_CUTOFF.value:
                self.set_lpf_cutoff(3, value)
                self.log.info(f"LPF 4 set: {value}")
            case Implementation.LPF_5_CUTOFF.value:
                self.set_lpf_cutoff(4, value)
                self.log.info(f"LPF 5 set: {value}")
            
            case Implementation.DELAY_TIME.value:
                self.set_delay_time(value)
                self.log.info(f"Delay time set: {value}")
            case Implementation.DELAY_FEEDBACK.value:
                self.set_delay_feedback(value)
                self.log.info(f"Delay feedback set: {value}")
    
    def set_up_signal_chain(self) -> Chain:
        # Defines components
        self.oscillator_library = OscillatorLibrary(self.sample_rate, self.frames_per_chunk)
        self.oscillators = self.oscillator_library.oscillators
        gains = [Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[self.oscillators[i]], control_tag=f"gain_{i}") for i in range(len(self.oscillators))]
        lpfs = [LowPassFilter(self.sample_rate, self.frames_per_chunk, subcomponents=[gains[i]], control_tag=f"lpf_{i}") for i in range(len(gains))]
        mixer = Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=lpfs)
        delay = Delay(self.sample_rate, self.frames_per_chunk, subcomponents=[mixer])

        # Defines parameters
        self.oscillator_active_status = [True, True, True, True, True]
        self.amplitude_status = [0.0, 0.0, 0.0, 1.0, 0.0] # initial condition. implement settings saving later
        self.lpf_active_status = [True, True, True, True, True]
        self.lpf_cutoff_status = [20000, 20000, 20000, 20000, 20000]
        self.delay_active_status = True
        self.delay_time_status = 0.5
        self.delay_feedback_status = 0.5

        for i in range(len(self.oscillators)):
            self.oscillators[i].active = self.oscillator_active_status[i]
            # print("woah!")
            # logging.info(f"{self.oscillators[i].name} active is {self.oscillators[i].active}! Executed from synthesizers.py, 106") # ACTIVE CHECK
        for i in range(len(gains)):
            gains[i].amplitude = self.amplitude_status[i] # gain only has one subcomponent
        for i in range(len(lpfs)):
            lpfs[i].active = self.lpf_active_status[i]
            lpfs[i].cutoff_frequency = self.lpf_cutoff_status[i]
            logging.info(f"LPF FREQ active {lpfs[i].active} frequency {lpfs[i].cutoff_frequency}")
        delay.active = self.delay_active_status
        delay.delay_time = self.delay_time_status
        delay.feedback = self.delay_feedback_status

        return Chain(delay) # top most component in the chain is mixer

    def generator(self):
        """
        Generate the signal by mixing the voice outputs
        """
        mixed_next_chunk = np.zeros(self.frames_per_chunk, np.float32)
        num_active_voices = 0
        while True:
            for voice in self.voices:
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
    
    def set_gain(self, number: int, cc_value: int):
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"gain_{number}")
            for component in components:
                component.amplitude = self.amp_values[cc_value]
    
    def set_lpf_cutoff(self, number: int, cc_value: int):
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"lpf_{number}")
            for component in components:
                component.cutoff_frequency = self.lpf_cutoff_values[cc_value]
    
    def set_delay_time(self, cc_value: int):
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.delay_time = self.delay_time_values[cc_value]

    def set_delay_feedback(self, cc_value: int):
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.feedback = self.delay_feedback_values[cc_value]