# formal version of the stuff we did in __main__.py

import threading
import logging
from queue import Queue
from copy import deepcopy

import numpy as np
from PyQt6 import QtCore

from . import midi
from . import settings
from .midi.implementation import Implementation
from .synthesis.voice import Voice
from .synthesis.signal.chain import Chain
from .synthesis.signal.oscillator_library import OscillatorLibrary
from .synthesis.signal.oscillator import Oscillator
from .synthesis.signal.fx.gain import OscillatorGain, VelocityGain
from .synthesis.signal.fx.filter import Hpf, Lpf
from .synthesis.signal.mixer import Mixer
from .synthesis.signal.modulators.envelope import Envelope
from .synthesis.signal.fx.delay import Delay
from .synthesis.signal.modulators.lfo import Lfo
from .playback.stream_player import StreamPlayer

class Synthesizer(QtCore.QObject): # each synth in separate thread??
    def __init__(self, sample_rate: int, buffer_size: int, mailbox: Queue, num_voices: int, output_device) -> None: # mailbox = synth_mailbox
        super().__init__()
        threading.current_thread().name = "Synthesizer Thread"
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.mailbox = mailbox
        self.num_voices = num_voices
        self.should_run = True
    
        # Set up the voices
        signal_prototype = self.set_up_signal_chain()
        self.voices = [Voice(deepcopy(signal_prototype)) for _ in range(num_voices)]

        self.lfo = Lfo(self.sample_rate, self.buffer_size, self.voices)
        self.lfo.formula = self.oscillator_library[3]["formula"]
        self.lfo.parameter = ()
        self.lfo.frequency = 1.0
        self.lfo.amount = 0.3
        self.lfo.start()

        # Set up the stream player
        self.stream_player = StreamPlayer(self.sample_rate, self.buffer_size, self.generator(), output_device)

    def run(self):
        self.stream_player.play()
        while self.should_run and self.stream_player.is_active():
            if message := self.mailbox.get():
                self.message_handler(message)
        return
    
    def set_up_signal_chain(self) -> Chain:
        # Defines components
        self.oscillator_library = OscillatorLibrary(self.sample_rate, self.buffer_size).oscillators
        self.oscillators = [Oscillator(self.sample_rate, self.buffer_size, oscillator["formula"], oscillator["name"], oscillator["control_tag"]) for oscillator in self.oscillator_library]
        oscillator_gains = [OscillatorGain(self.sample_rate, self.buffer_size, subcomponents=[self.oscillators[i]], control_tag=f"oscillator_gain_{i}") for i in range(len(self.oscillators))]
        hpfs = [Hpf(self.sample_rate, self.buffer_size, subcomponents=[oscillator_gains[i]], control_tag=f"hpf_{i}") for i in range(len(oscillator_gains))]
        lpfs = [Lpf(self.sample_rate, self.buffer_size, subcomponents=[hpfs[i]], control_tag=f"lpf_{i}") for i in range(len(oscillator_gains))]
        mixer = Mixer(self.sample_rate, self.buffer_size, subcomponents=lpfs)
        velocity_gain = VelocityGain(self.sample_rate, self.buffer_size, subcomponents=[mixer])
        envelope = Envelope(self.sample_rate, self.buffer_size, subcomponents=[velocity_gain])
        delay = Delay(self.sample_rate, self.buffer_size, subcomponents=[envelope])

        # Defines parameters
        # RLY DONT NEED THIS PART LOWK
        self.oscillator_active_status = [True, True, True, True, True]
        self.gain_amplitude_status = [1.0, 1.0, 1.0, 1.0, 1.0] # initial condition. implement settings saving later
        self.hpf_active_status = [True, True, True, True, True]
        self.hpf_cutoff_status = [200, 200, 200, 200, 200]
        self.lpf_active_status = [True, True, True, True, True]
        self.lpf_cutoff_status = [20000, 20000, 20000, 20000, 20000]
        self.velocity_gain_amplitude_status = 1.0
        self.delay_active_status = False
        self.delay_time_status = 0.5
        self.delay_feedback_status = 0.5
        self.delay_wet_status = 0.5

        for i in range(len(self.oscillators)):
            self.oscillators[i].active = self.oscillator_active_status[i]
            # print("woah!")
            # logging.info(f"{self.oscillators[i].name} active is {self.oscillators[i].active}! Executed from synthesizers.py, 106") # ACTIVE CHECK
        for i in range(len(oscillator_gains)):
            oscillator_gains[i].amplitude = self.gain_amplitude_status[i] # gain only has one subcomponent
        for i in range(len(hpfs)):
            hpfs[i].active = self.hpf_active_status[i]
            hpfs[i].cutoff = self.hpf_cutoff_status[i]
            logging.info(f"hpf FREQ active {hpfs[i].active} frequency {hpfs[i].cutoff}")
        for i in range(len(lpfs)):
            lpfs[i].active = self.lpf_active_status[i]
            lpfs[i].cutoff = self.lpf_cutoff_status[i]
            logging.info(f"lpf FREQ active {lpfs[i].active} frequency {lpfs[i].cutoff}")
        velocity_gain.amplitude = self.velocity_gain_amplitude_status

        delay.active = self.delay_active_status
        delay.delay_time = self.delay_time_status
        delay.feedback = self.delay_feedback_status
        delay.wet = self.delay_wet_status

        return Chain(delay) # top most component in the chain is mixer

    def message_handler(self, message: str):
        match message.split(): # receiving message as a STRING from midi_listener.py
            case ["exit"]:
                self.log.info("Got exit command.")
                self.stream_player.stop()
                self.should_run = False
            case [sender, "note_on", "-c", channel, "-n", note, "-e", velocity]:
                int_note = int(note)
                int_channel = int(channel)
                int_velocity = int(velocity)
                note_name = midi.note_names[int_note]
                self.note_on(sender, int_channel, int_note, int_velocity)
                self.log.info(f"Note on {note_name} ({int_note}), vel {velocity}, chan {int_channel}")
            case [sender, "note_off", "-c", channel, "-n", note]:
                int_note = int(note)
                int_channel = int(channel)
                note_name = midi.note_names[int_note]
                self.note_off(sender, int_channel, int_note)
                self.log.info(f"Note off {note_name} ({int_note}), chan {int_channel}")
            case [sender, "control_change", "-c", channel, "-o", component, "-n", cc_number, "-v", value]:
                int_channel = int(channel)
                try:
                    int_cc_number = int(cc_number)
                except ValueError:
                    int_cc_number = cc_number
                int_value = int(value)
                self.control_change_handler(sender, int_channel, component, int_cc_number, int_value)
            case [sender, "ui_message", "-n", name, "-c", channel, "-o", component, "-v", value]:
                match name:
                    case "set_active":
                        self.set_active(sender, int(channel), component, value=="True")
                    case "lfo_parameter":
                        self.set_lfo_parameter(sender, int(channel), component, value)
            case _:
                self.log.info(f"Unknown MIDI message: {message}")
    
    def control_change_handler(self, sender: str, channel: int, component: str, cc_number: int, value: int): # prob j change the volume? go to Chain, search by gain, multiply by value
        self.log.info(f"Control Change: sender {sender}, channel {channel}, CC {cc_number}, value {value}")
        match cc_number:
            # case Implementation.OSC_AMP.value:
            #     self.set_gain(sender, self.window.osc_tab.focused_osc.number, value)
            #     self.log.info(f"Gain {self.window.osc_tab.focused_osc.number + 1} set: {value}")

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
                if sender != "ui":
                    osc_number = self.window.osc_tab.focused_osc.number
                if sender == "ui":
                    osc_number = int(component.split("_")[1])
                self.set_hpf_cutoff(sender, osc_number, value)
                self.log.info(f"hpf {osc_number + 1} cutoff set: {value}")
            case Implementation.HPF_WET.value:
                if sender != "ui":
                    osc_number = self.window.osc_tab.focused_osc.number
                if sender == "ui":
                    osc_number = int(component.split("_")[1])
                self.set_hpf_wet(sender, osc_number, value)
                self.log.info(f"hpf {osc_number + 1} wet set: {value}")
            case Implementation.LPF_CUTOFF.value:
                if sender != "ui":
                    osc_number = self.window.osc_tab.focused_osc.number
                if sender == "ui":
                    osc_number = int(component.split("_")[1])
                self.set_lpf_cutoff(sender, osc_number, value)
                self.log.info(f"lpf {osc_number + 1} cutoff set: {value}")
            case Implementation.LPF_WET.value:
                if sender != "ui":
                    osc_number = self.window.osc_tab.focused_osc.number
                if sender == "ui":
                    osc_number = int(component.split("_")[1])
                self.set_lpf_wet(sender, osc_number, value)
                self.log.info(f"lpf {osc_number + 1} wet set: {value}")
            
            case Implementation.DELAY_TIME.value:
                self.set_delay_time(sender, value)
                self.log.info(f"Delay time set: {value}")
            case Implementation.DELAY_FEEDBACK.value:
                self.set_delay_feedback(sender, value)
                self.log.info(f"Delay feedback set: {value}")
            case Implementation.DELAY_WET.value:
                self.set_delay_wet(sender, value)
                self.log.info(f"Delay wet set: {value}")
            
            case Implementation.ENV_ATTACK.value:
                self.set_envelope_attack(sender, value)
                self.log.info(f"Envelope attack set: {value}")
            case Implementation.ENV_DECAY.value:
                self.set_envelope_decay(sender, value)
                self.log.info(f"Envelope decay set: {value}")
            case Implementation.ENV_SUSTAIN.value:
                self.set_envelope_sustain(sender, value)
                self.log.info(f"Envelope sustain set: {value}")
            case Implementation.ENV_RELEASE.value:
                self.set_envelope_release(sender, value)
                self.log.info(f"Envelope release set: {value}")

            case Implementation.LFO_SHAPE.value:
                self.set_lfo_shape(sender, value)
                self.log.info(f"LFO shape set: {value}")
            case Implementation.LFO_PARAMETER.value:
                self.set_lfo_parameter(sender, value)
                self.log.info(f"LFO parameter set: {value}")
            case Implementation.LFO_FREQUENCY.value:
                self.set_lfo_frequency(sender, value)
                self.log.info(f"LFO frequency set: {value}")
            case Implementation.LFO_AMOUNT.value:
                self.set_lfo_amount(sender, value)
                self.log.info(f"LFO amount set: {value}")
            
            case Implementation.VEL_SENSITIVITY.value:
                self.set_velocity_sensitivity(sender, value)
                self.log.info(f"Velocity sensitivity set: {value}")
    
    def generator(self):
        """
        Generate the signal by mixing the voice outputs
        """
        mixed_next_chunk = np.zeros(self.buffer_size, np.float32)
        num_active_voices = 0
        while True:
            # print(f"active voices: {num_active_voices}")
            for voice in self.voices:
                mixed_next_chunk += next(voice.signal_chain)
                if voice.active:
                    num_active_voices += 1

            mixed_next_chunk = np.clip(mixed_next_chunk, -1.0, 1.0)

            yield mixed_next_chunk
            mixed_next_chunk = np.zeros(self.buffer_size, np.float32)
            num_active_voices = 0
    
    def note_on(self, sender: str, channel: int, note: int, velocity: int):
        """
        Set a voice on with the given note.
        If there are no unused voices, drop the voice that has been on for the longest and use that voice
        """
        note_id = self.get_note_id(note, channel)
        freq = midi.frequencies[note]

        for i in range(len(self.voices)):
            voice = self.voices[i]
            if not voice.active:
                component = voice.signal_chain.get_components_by_class(VelocityGain)[0]
                component.amplitude = component.amp_values[velocity]

                voice.note_on(freq, note_id)
                self.voices.append(self.voices.pop(i))
                break
        
            if i == len(self.voices) - 1:
                self.log.warning("No unused voices! Dropped the voice in use for the longest.")
                self.voices[0].terminate() # force end release
                component = voice.signal_chain.get_components_by_class(VelocityGain)[0]
                component.amplitude = component.amp_values[velocity]

                self.voices[0].note_on(freq, note_id)
                self.voices.append(self.voices.pop(0))
    
    def note_off(self, sender: str, channel: int, note: int):
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

    def set_active(self, sender, channel, component, value):
        self.log.info(f"{component} active set to {value}")
        match component.split("_"):
            case ["osc", number]:
                for voice in self.voices:
                    components = voice.signal_chain.get_components_by_control_tag(f"osc_{number}")
                    for component in components:
                        component.active = value
            case ["delay"]:
                for voice in self.voices:
                    components = voice.signal_chain.get_components_by_control_tag(f"delay")
                    for component in components:
                        component.active = value
            case _:
                raise "Unknown component '{component}'"
    
    def set_velocity_sensitivity(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.performance_section.velocity_sensitivity_dial.setValue(cc_value)
        for voice in self.voices:
            component = voice.signal_chain.get_components_by_class(VelocityGain)[0]
            component.velocity_sensitivity = cc_value

    def set_gain(self, sender: str, number: int, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.osc_list[number].gain_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"oscillator_gain_{number}")
            for component in components:
                component.amplitude = settings.amp_values[cc_value]
    
    def set_hpf_cutoff(self, sender: str, number: int, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.osc_list[number].hpf_cutoff_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"hpf_{number}")
            for component in components:
                component.cutoff = settings.filter_cutoff_values[cc_value]
    
    def set_hpf_wet(self, sender: str, number: int, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.osc_list[number].hpf_wet_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"hpf_{number}")
            for component in components:
                component.wet = settings.filter_wet_values[cc_value]

    def set_lpf_cutoff(self, sender: str, number: int, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.osc_list[number].lpf_cutoff_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"lpf_{number}")
            for component in components:
                component.cutoff = settings.filter_cutoff_values[cc_value]
    
    def set_lpf_wet(self, sender: str, number: int, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.osc_list[number].lpf_wet_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"lpf_{number}")
            for component in components:
                component.wet = settings.filter_wet_values[cc_value]
    
    def set_delay_time(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.fx_tab.delay_fx.delay_time_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.delay_time = settings.delay_time_values[cc_value]

    def set_delay_feedback(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.fx_tab.delay_fx.delay_feedback_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.feedback = settings.delay_feedback_values[cc_value]
    
    def set_delay_wet(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.fx_tab.delay_fx.delay_wet_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"delay")
            for component in components:
                component.wet = settings.delay_wet_values[cc_value]
    
    def set_envelope_attack(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.envelope_section.attack_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"envelope")
            for component in components:
                component.attack = settings.envelope_attack_values[cc_value]

    def set_envelope_decay(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.envelope_section.decay_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"envelope")
            for component in components:
                component.decay = settings.envelope_decay_values[cc_value]
    
    def set_envelope_sustain(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.envelope_section.sustain_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"envelope")
            for component in components:
                component.sustain = settings.envelope_sustain_values[cc_value]

    def set_envelope_release(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.envelope_section.release_dial.setValue(cc_value)
        for voice in self.voices:
            components = voice.signal_chain.get_components_by_control_tag(f"envelope")
            for component in components:
                component.release = settings.envelope_release_values[cc_value]

    def set_lfo_shape(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.lfo_section.shape_dropdown.setCurrentIndex(cc_value)
        self.lfo.formula = self.oscillator_library[cc_value]["formula"]
    
    def set_lfo_parameter(self, sender: str, channel: int, component: str, value: str):
        parameter_tuple = tuple(value.split("."))
        # if sender != "ui":
        #     self.window.osc_tab.lfo_section.parameter_dropdown.setCurrentText(tuple[0]) FIXFIXFIX
        self.lfo.parameter = parameter_tuple
    
    def set_lfo_frequency(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.lfo_section.frequency_dial.setValue(cc_value)
        self.lfo.frequency = settings.lfo_frequency_values[cc_value]
    
    def set_lfo_amount(self, sender: str, cc_value: int):
        if sender != "ui":
            self.window.osc_tab.lfo_section.amount_dial.setValue(cc_value)
        self.lfo.amount = settings.lfo_amount_values[cc_value] # A PERCENTAGE