import logging
from copy import deepcopy
from typing import List

import numpy as np

from .component import Component

class Gain(Component):
    """
    The gain component multiplies the amplitude of the signal by a constant factor.
    """
    def __init__(self, sample_rate: int, frames_per_chunk: int, subcomponents: List["Component"] = [], name: str="Gain", control_tag: str="gain"):
        super().__init__(sample_rate, frames_per_chunk, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self._amplitude = 1.0
        self.control_tag = control_tag
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # i think this means oscillators being amplified is its subcomponent. this line creates an iter out of its subcomponent
        return self
    
    def __next__(self):
        chunk = next(self.subcomponent_iter)
        return chunk * self.amplitude 

    def __deepcopy__(self, memo):
        # print(f"Gain {self.name} being deep copied!")
        copy = Gain(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.amplitude = self.amplitude 
        return copy

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, value):
        try:
            float_value = float(value)
            if float_value >= 0 and float_value <= 1.9:
                self._amplitude = float_value
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
            bool_val = bool(value)
            self._active = bool_val
            # for subcomponent in self.subcomponents: # !!!!!!!!!!
            #     subcomponent.active = bool_val
        except ValueError:
            self.log.error(f"Couldn't set active with value {value}")