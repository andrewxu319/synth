import logging
import numpy as np

from .generator import Generator

class Oscillator(Generator):
    def __init__(self, sample_rate: int, frames_per_chunk: int, name: str="Oscillator"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
        self.log = logging.getLogger(__name__)
        self._frequency = 0.0
        self._phase = 0.0
        self._amplitude = 0.1

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
        print(f"Oscillator {self.name} active set to {self.active}")
        try:
            self._active = bool(value)
            self._frequency = 0.0 if not self._active else self._frequency
        except:
            self.log.error(f"Unable to set with value {value}")


"""
frequency
phase
set phase degrees
amplitude
active
"""