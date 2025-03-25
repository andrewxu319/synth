import logging
from copy import deepcopy
from typing import List

import numpy as np

from .component import Component

class Gain(Component):
    """
    The gain component multiplies the amplitude of the signal by a constant factor.
    """
    def __init__(self, sample_rate: int, frames_per_chunk: int, amplitude: float, subcomponents: List["Component"] = [], name: str="Gain", control_tag: str="gain"):
        super().__init__(sample_rate, frames_per_chunk, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self._amplitude = amplitude
        self.control_tag = control_tag
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # i think this means oscillators being amplified is its subcomponent. this line creates an iter out of its subcomponent
        return self
    
    def __next__(self):
        chunk = next(self.subcomponent_iter)
        # print(self.amplitude)
        return chunk * self.amplitude

    def __deepcopy__(self, memo):
        # print("Deep copying gain!")
        return Gain(self.sample_rate, self.frames_per_chunk, self.amplitude, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag) # only one subcomponent

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        try:
            float_value = float(value)
            if float_value >= 0.0 and float_value <= 1.0:
                self._amplitude = float_value
                print(self.amplitude)
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
            self._active = bool(value)
            # print(f"Gain active set to {value}!")
        except ValueError:
            self.log.error(f"Couldn't set active with value {value}")