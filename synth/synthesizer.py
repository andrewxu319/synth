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
from .synthesis.signal.fx.filter import Filter
from .synthesis.signal.fx.delay import Delay
from .synthesis.signal.mixer import Mixer
from .playback.stream_player import StreamPlayer
from .ui.main_window import Ui

class Synthesizer(threading.Thread): # each synth in separate thread??
    def __init__(self, sample_rate: int, frames_per_chunk: int, mailbox: Queue, ui: Ui, num_voices: int, output_device) -> None: # mailbox = synth_mailbox
        super().__init__(name="Synthesizer Thread")
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.mailbox = mailbox
        self.ui = ui
        self.num_voices = num_voices
        self.should_run = True

        # Preset fx values to avoid doing division every time
        self.amp_values = np.linspace(0, 1, 128)
        self.filter_cutoff_values = np.logspace(4, 14.3, 128, endpoint=True, base=2, dtype=np.float32)
        self.delay_time_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.5 # 0 to about 2 seconds
        self.delay_feedback_values = (np.logspace(0, 1, 128, endpoint=True, base=10) - 1) / 9 # 0 to 1
        self.delay_wet_values = np.linspace(0, 1, 128)
    
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
            case [sender, "note_on", "-n", note, "-c", channel]:
                int_note = int(note)
                int_channel = int(channel)
                note_name = midi.note_names[int_note]
                self.note_on(sender, int_note, int_channel)
                self.log.info(f"Note on {note_name} ({int_note}), chan {int_channel}")
            case [sender, "note_off", "-n", note, "-c", channel]:
                int_note = int(note)
                int_channel = int(channel)
                note_name = midi.note_names[int_note]
                self.note_off(sender, int_note, int_channel)
                self.log.info(f"Note off {note_name} ({int_note}), chan {int_channel}")
            case [sender, "control_change", "-c", channel, "-n", cc_number, "-v", value]:
                int_channel = int(channel)
                int_cc_number = int(cc_number)
                int_value = int(value)
                self.control_change_handler(sender, int_channel, int_cc_number, int_value)
            case [sender, "set_active", "-c", channel, "-o", component, "-v", value]:
                self.set_active(sender, int(channel), component, value=="True")
            case _:
                self.log.info(f"Unknown MIDI message: {message}")
    
    def control_change_handler(self, sender: str, channel: int, cc_number: int, value: int): # prob j change the volume? go to Chain, search by gain, multiply by value
        self.log.info(f"Control Change: sender {sender}, channel {channel}, CC {cc_number}, value {value}")
        match cc_number:
            # case Implementation.OSC_AMP.value:
            #     self.set_gain(sender, self.ui.window.osc_tab.focused_osc.number, value)
            #     self.log.info(f"Gain {self.ui.window.osc_tab.focused_osc.number + 1} set: {value}")

            case Implementation.OSC_1_AMP.value:
                self.set_gain(sender, 0, value)
                self.log.info(f"Gain 1 set: {value}")
            case Implementation.OSC_2_AMP.value:
                self.set_gain(sender, 1, value)
                self.log.info(f"Gain 2 set: {value}")
            case Implementation.OSC_3_AMP.value:
                self.set_gain(sender, 2, value)
                self.log.info(f"Gain 3 set: {value}")
            case Implementation.OSC_4_AMP.value:
                self.set_gain(sender, 3, value)
                self.log.info(f"Gain 4 set: {value}")
            case Implementation.OSC_5_AMP.value:
                self.set_gain(sender, 4, value)
                self.log.info(f"Gain 5 set: {value}")

            case Implementation.HPF_CUTOFF.value:
                self.set_hpf_cutoff(sender, self.ui.window.osc_tab.focused_osc.number, value)
                self.log.info(f"hpf {self.ui.window.osc_tab.focused_osc.number + 1} set: {value}")
            case Implementation.LPF_CUTOFF.value:
                self.set_lpf_cutoff(sender, self.ui.window.osc_tab.focused_osc.number, value)
                self.log.info(f"lpf {self.ui.window.osc_tab.focused_osc.number + 1} set: {value}")
            
            case Implementation.DELAY_TIME.value:
                self.set_delay_time(sender, value)
                self.log.info(f"Delay time set: {value}")
            case Implementation.DELAY_FEEDBACK.value:
                self.set_delay_feedback(sender, value)
                self.log.info(f"Delay feedback set: {value}")
            case Implementation.DELAY_WET.value:
                self.set_delay_wet(sender, value)
                self.log.info(f"Delay wet set: {value}")
    
    def set_up_signal_chain(self) -> Chain:
        # Defines components
        self.oscillator_library = OscillatorLibrary(self.sample_rate, self.frames_per_chunk)
        self.oscillators = self.oscillator_library.oscillators
        gains = [Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[self.oscillators[i]], control_tag=f"gain_{i}") for i in range(len(self.oscillators))]
        hpfs = [Filter(self.sample_rate, self.frames_per_chunk, "highpass", subcomponents=[gains[i]], control_tag=f"hpf_{i}") for i in range(len(gains))]
        lpfs = [Filter(self.sample_rate, self.frames_per_chunk, "lowpass", subcomponents=[hpfs[i]], control_tag=f"lpf_{i}") for i in range(len(gains))]
        mixer = Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=lpfs)
        delay = Delay(self.sample_rate, self.frames_per_chunk, subcomponents=[mixer])

        # Defines parameters
        # RLY DONT NEED THIS PART LOWK
        self.oscillator_active_status = [True, True, True, True, True]
        self.amplitude_status = [0.0, 0.0, 0.0, 1.0, 0.0] # initial condition. implement settings saving later
        self.hpf_active_status = [True, True, True, True, True]
        self.hpf_cutoff_status = [200, 200, 200, 200, 200]
        self.lpf_active_status = [True, True, True, True, True]
        self.lpf_cutoff_status = [20000, 20000, 20000, 20000, 20000]
        self.delay_active_status = True
        self.delay_time_status = 0.5
        self.delay_feedback_status = 0.5
        self.delay_wet_status = 0.5

        for i in range(len(self.oscillators)):
            self.oscillators[i].active = self.oscillator_active_status[i]
            # print("woah!")
            # logging.info(f"{self.oscillators[i].name} active is {self.oscillators[i].active}! Executed from synthesizers.py, 106") # ACTIVE CHECK
        for i in range(len(gains)):
            gains[i].amplitude = self.amplitude_status[i] # gain only has one subcomponent
        for i in range(len(hpfs)):
            hpfs[i].active = self.hpf_active_status[i]
            hpfs[i].cutoff_frequency = self.hpf_cutoff_status[i]
            logging.info(f"hpf FREQ active {hpfs[i].active} frequency {hpfs[i].cutoff_frequency}")
        for i in range(len(lpfs)):
            lpfs[i].active = self.lpf_active_status[i]
            lpfs[i].cutoff_frequency = self.lpf_cutoff_status[i]
            logging.info(f"lpf FREQ active {lpfs[i].active} frequency {lpfs[i].cutoff_frequency}")
        delay.active = self.delay_active_status
        delay.delay_time = self.delay_time_status
        delay.feedback = self.delay_feedback_status
        delay.wet = self.delay_wet_status

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
    
    def note_on(self, sender: str, note: int, channel: int):
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
    
    def note_off(self, sender: str, note: int, channel: int):
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
    
    def set_gain(self, sender: str, number: int, cc_value: int):
        if sender == "midi":
            self.ui.window.osc_tab.osc_list[number].gain_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"gain_{number}")
            for component in components:
                component.amplitude = self.amp_values[cc_value]
    
    def set_hpf_cutoff(self, sender: str, number: int, cc_value: int):
        if sender == "midi":
            self.ui.window.osc_tab.osc_list[number].hpf_cutoff_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"hpf_{number}")
            for component in components:
                component.cutoff_frequency = self.filter_cutoff_values[cc_value]

    def set_lpf_cutoff(self, sender: str, number: int, cc_value: int):
        if sender == "midi":
            self.ui.window.osc_tab.osc_list[number].lpf_cutoff_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"lpf_{number}")
            for component in components:
                component.cutoff_frequency = self.filter_cutoff_values[cc_value]
    
    def set_delay_time(self, sender: str, cc_value: int):
        if sender == "midi":
            self.ui.window.fx_tab.delay_fx.delay_time_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.delay_time = self.delay_time_values[cc_value]

    def set_delay_feedback(self, sender: str, cc_value: int):
        if sender == "midi":
            self.ui.window.fx_tab.delay_fx.delay_feedback_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.feedback = self.delay_feedback_values[cc_value]
    
    def set_delay_wet(self, sender: str, cc_value: int):
        if sender == "midi":
            self.ui.window.fx_tab.delay_fx.delay_wet_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.wet = self.delay_wet_values[cc_value]
    
    def set_active(self, sender, channel, component, value):
        match component.split("_"):
            case ["osc", number]:
                for voice in self.voices:
                    gain_components = voice.signal_chain.get_components_by_control_tag(f"gain_{number}")
                    for gain_component in gain_components:
                        gain_component.subcomponents[0].active = value
            case ["delay"]:
                for voice in self.voices:
                    components = voice.signal_chain.get_components_by_control_tag(f"delay")
                    for component in components:
                        component.active = value
            case _:
                raise "Unknown component '{component}'"