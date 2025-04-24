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
        self.value_range = (0.0, 1.0)

        # # do ts later as needed
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
        thread = Thread(target=self.start_thread)
        self.start_time = time.time()
        # breakpoint()
        thread.start()

    def start_thread(self):
        while True:
            try:
                output = self.value_range[0] + (self.value_range[1] - self.value_range[0]) * (self.formula(self.frequency, self.phase, 0.5, time.time() - self.start_time) + 1.0) # frequency in seconds
                # self.set_parameter(self.parameter, output)
                for voice in self.voices:
                    component = voice.signal_chain.get_components_by_class(self.parameter[0])[self.parameter[2] if len(self.parameter) == 3 else 0]
                    setattr(component, self.parameter[1], output)
                time.sleep(200 * self.refresh_time)

            except KeyboardInterrupt:
                break
        sys.exit()
    
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

    def __deepcopy__(self, memo):
        # logging.info(f"Deep copying oscillator {self.name} with active {self.active}")
        copy = Lfo(self.sample_rate, self.buffer_size, self.formula, name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.target = self.target
        copy.refresh_time = self.refresh_time
        return copy


"""
frequency
phase
set phase degrees
amplitude
active
"""