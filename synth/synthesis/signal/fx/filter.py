import logging
from typing import List
from copy import deepcopy

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi # type: ignore

from ..component import Component

class Filter(Component):
    def __init__(self, sample_rate, buffer_size, type, subcomponents: List["Component"] = [], name="filter", control_tag="filter"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.type = type
        self.filter_order = 2
        self.cutoff = 20000.0
        self.wet = 1.0
        self.b, self.a = self.compute_coefficients()
        self.zi = self.compute_initial_conditions()
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        if self.active:
            dry_signal = next(self.subcomponent_iter)
            wet_signal, self.zi = lfilter(self.b, self.a, dry_signal, zi=self.zi)
            # return np.zeros(self.buffer_size, dtype=np.float32)
            mix = dry_signal * (1 - self.wet) + wet_signal * self.wet
            return mix.astype(np.float32)
        else:
            return next(self.subcomponent_iter)
    
    def __deepcopy__(self, memo):
        copy = Filter(self.sample_rate, self.buffer_size, self.type, subcomponents=[deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.cutoff = self.cutoff
        copy.wet = self.wet
        self.log.info(f"deep copied filter {self.name} with active {self.active} and freq {self.cutoff}")
        return copy

    # @property
    # def active(self):
    #     return self._active

    # @active.setter
    # def active(self, value):
    #     try:
    #         self._active = value
    #         logging.info(f"filter active set to {value}!")
    #     except ValueError:
    #         self.log.error(f"Couldn't set active with value {value}")

    @property
    def cutoff(self):
        return self._cutoff
    
    @cutoff.setter
    def cutoff(self, value):
        try:
            float_value = float(value)
            if float_value < 0.0:
                raise ValueError("Cutoff frequency must be positive!")
            else:
                self._cutoff = float_value
                logging.info(f"Cutoff frequency set to {self.cutoff}!")
                self.b, self.a = self.compute_coefficients()
        except ValueError:
            logging.error(f"Couldn't set cutoff frequency with value {float_value}")
    
    @property
    def wet(self):
        return self._wet

    @wet.setter
    def wet(self, value):
        try:
            float_value = float(value)
            if float_value < 0.0 or float_value > 1.0:
                raise ValueError("Filter wet must be between 0 and 1!")
            else:
                self._wet = float_value
                logging.info(f"Filter wet set to {self.wet}!")
        except ValueError:
            logging.error(f"Couldn't set wet frequency with value {float_value}")

    def compute_coefficients(self): # make sure this isnt called constantly
        nyquist = self.sample_rate * 0.5
        normalized_cutoff = self.cutoff / nyquist
        b, a = butter(self.filter_order, normalized_cutoff, btype=self.type, analog=False) # {‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’}
        return b, a

    def compute_initial_conditions(self):
        zi = lfilter_zi(self.b, self.a)
        return zi