import logging
from copy import deepcopy

import numpy as np

from ..component import Component

class Delay(Component):
    def __init__(self, sample_rate, buffer_size, subcomponents, name="Delay", control_tag="delay") -> None: # initialization parameters = instance of a "delay plugin". cant be changed. the actual delay time etc is changed thru setting "delay.delay_time"
        # print(f"FPC {buffer_size}")
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.delay_buffer_length = 4.0
        self.delay_frames = int(self.delay_buffer_length * self.sample_rate)
        self.delay_time = 0.0
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.time_start_index = self.delay_frames - int(self.delay_time * self.sample_rate)
        self.feedback = 0.0
        self.wet = 0.0
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        dry_mix = next(self.subcomponent_iter)
        wet_mix = dry_mix

        if self.active and self.feedback > 0.0 and self.delay_time > 0.0 and self.wet > 0.0:
            delayed_signal = self.delay_buffer[self.time_start_index: self.time_start_index + self.buffer_size]
            # print(delayed_signal)
            while len(delayed_signal) < self.buffer_size:
                delayed_signal = np.concatenate((delayed_signal, self.delay_buffer[:self.buffer_size - len(delayed_signal)]))
            
            delayed_signal *= self.feedback
            wet_mix += delayed_signal
            
            self.delay_buffer = np.roll(self.delay_buffer, -self.buffer_size)
            self.delay_buffer[self.delay_frames - self.buffer_size: self.delay_frames] = wet_mix

            # round down to zero here?

        mix = dry_mix * (1 - self.wet) + wet_mix * self.wet
        return np.astype(mix, np.float32)
    
    def __deepcopy__(self, memo):
        copy = Delay(self.sample_rate, self.buffer_size, [deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], self.name, self.control_tag)
        copy.active = self.active
        copy.delay_time = self.delay_time
        copy.feedback = self.feedback
        copy.delay_buffer = self.delay_buffer
        copy.wet = self.wet
        return copy
    
    @property
    def delay_time(self):
        return self._delay_time

    @delay_time.setter
    def delay_time(self, value):
        self._delay_time = float(value)
        self.time_start_index = self.delay_frames - int(self.delay_time * self.sample_rate)