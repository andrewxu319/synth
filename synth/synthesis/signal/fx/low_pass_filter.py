import logging
from typing import List
from copy import deepcopy

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi # type: ignore

from ...signal.component import Component

class LowPassFilter(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents: List["Component"] = [], name="LowPassFilter", control_tag="lpf"):
        super().__init__(sample_rate, frames_per_chunk, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.filter_order = 2
        self.cutoff_frequency = 20000.0
        self.b, self.a = self.compute_coefficients()
        self.zi = self.compute_initial_conditions()
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        if self.active:
            input_signal = next(self.subcomponent_iter)
            output_signal, self.zi = lfilter(self.b, self.a, input_signal, zi=self.zi)
            # return np.zeros(self.frames_per_chunk, dtype=np.float32)
            return output_signal.astype(np.float32)
        else:
            return next(self.subcomponent_iter)
    
    def __deepcopy__(self, memo):
        copy = LowPassFilter(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.cutoff_frequency = self.cutoff_frequency
        self.log.info(f"deep copied lpf {self.name} with active {self.active} and freq {self.cutoff_frequency}")
        return copy

    # @property
    # def active(self):
    #     return self._active

    # @active.setter
    # def active(self, value):
    #     try:
    #         self._active = value
    #         logging.info(f"LPF active set to {value}!")
    #     except ValueError:
    #         self.log.error(f"Couldn't set active with value {value}")

    @property
    def cutoff_frequency(self):
        return self._cutoff_frequency
    
    @cutoff_frequency.setter
    def cutoff_frequency(self, value):
        try:
            float_value = float(value)
            if float_value < 0.0:
                raise ValueError("Cutoff frequency must be positive!")
            else:
                self._cutoff_frequency = float_value
                logging.info(f"Cutoff frequency set to {self.cutoff_frequency}!")
                self.b, self.a = self.compute_coefficients()
        except ValueError:
            logging.error(f"Couldn't set cutoff frequency with value {float_value}")

    def compute_coefficients(self):
        nyquist = self.sample_rate * 0.5
        normalized_cutoff = self.cutoff_frequency / nyquist
        b, a = butter(self.filter_order, normalized_cutoff, btype="low", analog=False)
        return b, a

    def compute_initial_conditions(self):
        zi = lfilter_zi(self.b, self.a)
        return zi