import logging
from copy import deepcopy
from typing import List

import numpy as np

from ..component import Component

class Gain(Component):
    """
    The gain component multiplies the amplitude of the signal by a constant factor.
    """
    def __init__(self, sample_rate: int, buffer_size: int, subcomponents: List["Component"] = [], name: str="Gain", control_tag: str="gain"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self._amplitude = 1.0
        self.control_tag = control_tag
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # i think this means oscillators being amplified is its subcomponent. this line creates an iter out of its subcomponent
        return self
    
    def __next__(self):
        chunk = next(self.subcomponent_iter)
        return chunk * self.modulated_amplitude 

    def __deepcopy__(self, memo):
        # print(f"Gain {self.name} being deep copied!")
        copy = Gain(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.amplitude = self.amplitude
        return copy

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        try:
            float_value = float(value)
            if float_value >= 0 and float_value <= 1.9:
                self._amplitude = float_value
                self.modulated_amplitude = float_value
                self.log.info(f"{self.control_tag} set to {float_value}")
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Gain must be between 0.0 and 1.0, got {value}")

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        try:
            self._active = value
            self.log.info(f"gain with osc {self.subcomponents[0].name} active set to {self.active}")
            # for subcomponent in self.subcomponents: # !!!!!!!!!!
            #     subcomponent.active = bool_val
        except ValueError:
            self.log.error(f"Couldn't set active with value {value}")

class OscillatorGain(Gain):
    def __init__(self, sample_rate: int, buffer_size: int, subcomponents: List["Component"] = [], name: str="OscillatorGain", control_tag: str="oscillator_gain"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
    
    def __deepcopy__(self, memo):
        copy = OscillatorGain(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.amplitude = self.amplitude
        return copy
    
class VelocityGain(Gain):
    def __init__(self, sample_rate: int, buffer_size: int, subcomponents: List["Component"] = [], name: str="VelocityGain", control_tag: str="velocity_gain"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.velocity_sensitivity = 127

    def __deepcopy__(self, memo):
        copy = VelocityGain(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.amplitude = self.amplitude
        copy.velocity_sensitivity = self.velocity_sensitivity
        return copy
    
    @property
    def velocity_sensitivity(self):
        return self._velocity_sensitivity

    @velocity_sensitivity.setter
    def velocity_sensitivity(self, value):
        self._velocity_sensitivity = value
        self.amp_values = np.linspace(np.linspace(0, 1, 128)[127 - value], 1, 128)
