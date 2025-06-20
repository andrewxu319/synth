from copy import deepcopy
from typing import List

import numpy as np

from .component import Component

class Mixer(Component):
    def __init__(self, sample_rate: int, buffer_size: int, subcomponents: List["Component"] = [], name: str="Mixer"):
        super().__init__(sample_rate, buffer_size, subcomponents, name)
    
    def __iter__(self):
        self.source_iters = [iter(component) for component in self.subcomponents]
        return self
    
    def __next__(self):
        # if self.active:
        input_signals = [next(source_iter) for source_iter in self.source_iters]
        mixed_signal = np.mean(input_signals, axis=0)
        mixed_signal = np.clip(mixed_signal, -1.0, 1.0)
        return mixed_signal.astype(np.float32)
        # else:
        #     return np.zeros(self.buffer_size, dtype=np.float32)

    def __deepcopy__(self, memo):
        copy = Mixer(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(component, memo) for component in self.subcomponents], name=self.name)
        copy.active = self.active
        return copy

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
    