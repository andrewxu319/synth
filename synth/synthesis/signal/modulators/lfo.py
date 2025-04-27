import logging
import numpy as np
from typing import Callable
from threading import Thread
import time
import sys

from ..oscillator import Oscillator
from ..fx.gain import OscillatorGain, VelocityGain
from ..fx.filter import Hpf, Lpf
from ..mixer import Mixer
from ..modulators.envelope import Envelope
from ..fx.delay import Delay

class Lfo(Oscillator):
    def __init__(self, sample_rate: int, buffer_size: int, voices: list, name: str="Lfo", control_tag: str="lfo"):
        super().__init__(sample_rate, buffer_size, lambda frequency, phase, amplitude, t: 0.0, name=name, control_tag=control_tag)
        self.log = logging.getLogger(__name__)
        self.voices = voices
        self.refresh_time = 1 / self.sample_rate

        self.channel = 0
        self.parameter = ()
        self.amount = 0.0

        # # do ts later if needed, standardize between midi cc controls and lfo controls
        # self.parameters = {
        #     "oscillators": {
        #         "oscillator_gain": (OscillatorGain, lambda component, value: setattr),
        #         "hpf_cutoff": (Hpf, lambda component, value: component.cutoff),
        #         "hpf_wet": (Hpf, lambda component, value: component.wet),
        #         "lpf_cutoff": (Lpf, lambda component, value: component.cutoff),
        #         "lpf_wet": (Lpf, lambda component, value: component.wet)
        #     },
        #     "fx": {
        #         "delay": {
        #             "time": delay.delay_time,
        #             "feedback": delay.feedback,
        #             "wet": delay.wet
        #         }
        #     },
        #     "modulators": {
        #         "envelope": {
        #             "attack": [float(envelope.attack)], # multiple envelopes in the future
        #             "decay": [float(envelope.decay)],
        #             "sustain": [float(envelope.sustain)],
        #             "release": [float(envelope.release)]
        #         }
        #     },
        #     "performance": {
        #         "velocity_sensitivity": chain.get_components_by_class(VelocityGain)[0].velocity_sensitivity
        #     }
        # }
    
    def start(self):
        self.thread = Thread(target=self.start_thread)
        self.start_time = time.time()
        # breakpoint()
        self.thread.start()

    def start_thread(self):
        while True:
            try:
                if self.parameter == ():
                    continue
                self.amplitude = self.amount * 1.0 # 1.0. FIGURE THIS OUT
                # print(self.starting_value)
                value_change = self.formula(self.frequency, self.phase, self.amplitude, time.time() - self.start_time) # frequency in seconds
                # print(value_change)
                for voice in self.voices:
                    component = voice.signal_chain.get_components_by_control_tag(self.parameter[0])[0]
                    setattr(component, "modulated_" + self.parameter[1], np.clip(self.parameter[1] + value_change, 0.0, 1.0)) # change 0.0 and 1.0
                    # print(component.modulated_amplitude)

            except KeyboardInterrupt:
                break
            time.sleep(200 * self.refresh_time)
        sys.exit()
    
    def update_starting_value(self):
        if self.parameter != ():
            component = self.voices[0].signal_chain.get_components_by_control_tag(self.parameter[0])[0]
            self.starting_value = getattr(component, self.parameter[1])
            print(self.voices[0].signal_chain.get_components_by_control_tag("oscillator_gain_0")[0].amplitude)
            print(self.parameter) # EVERYTHING BREAKS AAAAAAAAAa
            import time
            time.sleep(1)
            print(self.voices[0].signal_chain.get_components_by_control_tag("oscillator_gain_0")[0].amplitude)


    # def set_parameter(self, parameter: list, value):
    #     for voice in self.voices:
    #         components = voice.signal_chain.get_components_by_class(OscillatorGain)
    #         for component in components:
    #             component.amplitude = output
            
    #         match parameter:
    #             case ["oscillators", *sublevels, i]:
    #                 components = voice.signal_chain.get_components_by_class(OscillatorGain)

    #             case ["fx", *sublevels]:
    #                 match sublevels:
    #                     case ["delay", *sublevels]:
    #                         delay = window.fx_tab.delay_fx

    #                     case _:
    #                         log.warning(f"Attempted to change nonexistent parameter {sublevels} in fx!")

    #             case ["modulators", *sublevels]:
    #                 match sublevels:
    #                     case ["envelope", *sublevels, i]:
    #                         envelope = window.osc_tab.envelope_section # make it numbered later
    #                         match sublevels:
    #                             case ["attack"]:
    #                                 envelope.attack_dial.setValue(find_nearest(settings.envelope_attack_values, value))
    #                             case ["decay"]:
    #                                 envelope.decay_dial.setValue(find_nearest(settings.envelope_decay_values, value))
    #                             case ["sustain"]:
    #                                 envelope.sustain_dial.setValue(find_nearest(settings.envelope_sustain_values, value))
    #                             case ["release"]:
    #                                 envelope.release_dial.setValue(find_nearest(settings.envelope_release_values, value))
    #                             case _:
    #                                 log.warning(f"Attempted to change nonexistent parameter {sublevels} in modulators -> envelope!")

    #                     case _:
    #                         log.warning(f"Attempted to change nonexistent parameter {sublevels} in modulators!")

    #             case ["performance", *sublevels]:
    #                 performance = window.osc_tab.performance_section

    #                 match sublevels:
    #                     case ["velocity_sensitivity"]:
    #                         performance.velocity_sensitivity_dial.setValue(value)

    #                     case _:
    #                         log.warning(f"Attempted to change nonexistent parameter {sublevels} in performance!")

    # def get_parameter_value(self, dictionary, path):
    #     dictionary_copy = dictionary.copy()
    #     for key in path:
    #         dictionary = dictionary[key]
    #     return dictionary

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        try:
            self._active = bool(value)
            self._frequency = 0.0 if not self._active else self._frequency
            try:
                self.log.info(f"Lfo {self.name} active set to {self.active}")
            except:
                self.log.info(f"Lfo active set to {self.active}")
        except:
            self.log.error(f"Unable to set with value {value}, type {type(value)}")
    
    @property
    def shape(self):
        return self._shape
    @shape.setter
    def shape(self, value):
        self._shape = value
        self.log.info(f"LFO shape set to {value}")

    @property
    def parameter(self):
        return self._parameter
    @parameter.setter
    def parameter(self, value):
        self._parameter = value
        # self.update_starting_value()
        self.log.info(f"LFO parameter set to {value}")

    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self, value):
        self._frequency = value
        self.log.info(f"LFO frequency set to {value}")
    
    @property
    def amount(self):
        return self._amount
    @amount.setter
    def amount(self, value):
        self._amount = value
        # print(self.amplitude)
        self.log.info(f"LFO amount set to {value}")

    def __deepcopy__(self, memo):
        # logging.info(f"Deep copying oscillator {self.name} with active {self.active}")
        copy = Lfo(self.sample_rate, self.buffer_size, self.formula, name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.voices = self.voices
        copy.refresh_time = self.refresh_time
        copy.channel = self.channel
        copy.parameter = self.parameter
        copy.amount = self.amount
        return copy


"""
frequency
phase
set phase degrees
amplitude
active
"""