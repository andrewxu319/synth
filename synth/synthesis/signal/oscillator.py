import logging
import numpy as np
from typing import Callable

from .generator import Generator

class Oscillator(Generator):
    def __init__(self, sample_rate: int, frames_per_chunk: int, formula: Callable, name: str="Oscillator", control_tag: str="osc"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
        self.log = logging.getLogger(__name__)
        self._formula = formula
        self.name = name
        self.control_tag = control_tag
        self._frequency = 0.0
        self._phase = 0.0
        self._amplitude = 0.5
        self.parent_component_cannot_set_active = False
        # logging.info(f"new {self.name} created for some reason??? with active {self._active}")

    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self, value):
        try:
            self._frequency = float(value)
        except:
            self.log.error(f"Unable to set with value {value}")
    
    @property
    def phase(self):
        return self._phase
    @phase.setter
    def phase(self, value):
        try:
            self._phase = float(value)
        except:
            self.log.error(f"Unable to set with value {value}")

    def set_phase_degrees(self, degrees):
        try:
            self._phase = degrees / 180 * np.pi
        except:
            self.log.error(f"Unable to set with value {degrees}")

    @property
    def amplitude(self):
        return self._amplitude
    @amplitude.setter
    def amplitude(self, value):
        try:
            float_value = float(value)
            if float_value >= 0.0 and float_value <= 1.0:
                self._amplitude = float(value)
            else:
                raise ValueError
        except:
            self.log.error(f"Unable to set with value {value}")

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        try:
            self._active = value
            self._frequency = 0.0 if not self._active else self._frequency
            self.log.info(f"Oscillator {self.name} active set to {self.active}")
        except:
            self.log.error(f"Unable to set with value {value}")
    
    def __iter__(self):
        self._chunk_duration = self.frames_per_chunk / self.sample_rate
        self._chunk_start_time = 0.0
        self._chunk_end_time = self._chunk_duration
        return self

    def __next__(self):
        # self.log.info(f"Oscillator {self.name} active is {self.active}! See oscillator.py, 79") # ACTIVE CHECK
        if self.active:
            # logging.info(f"{self.name} active!")
            if self.frequency <= 0.0:
                if self.frequency < 0.0:
                    self.log.error("Overriding negative frequency to 0")
                sample = np.zeros(self.frames_per_chunk)

            else:
                # sample = self.amplitude * np.sin(self.phase + (2 * np.pi * self.frequency) * np.linspace(self._chunk_start_time, self._chunk_end_time, num=self.frames_per_chunk, endpoint = False))
                sample = self._formula(self.frequency, self.phase, self.amplitude, np.linspace(self._chunk_start_time, self._chunk_end_time, num=self.frames_per_chunk, endpoint = False))
                # logging.info(list(sample))

            self._chunk_start_time = self._chunk_end_time
            self._chunk_end_time += self._chunk_duration

            return sample.astype(np.float32)

        else:
            return np.zeros(self.frames_per_chunk, dtype=np.float32)

    def __deepcopy__(self, memo):
        # logging.info(f"Deep copying oscillator {self.name} with active {self.active}")
        copy = Oscillator(self.sample_rate, self.frames_per_chunk, self._formula, name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        return copy


"""
frequency
phase
set phase degrees
amplitude
active
"""