import logging

import numpy as np

# from .oscillator import Oscillator
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

class SineWaveOscillator(Oscillator):
    def __init__(self, sample_rate: int, frames_per_chunk: int, name: str="SineWaveOscillator"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        self._chunk_duration = self.frames_per_chunk / self.sample_rate
        self._chunk_start_time = 0.0
        self._chunk_end_time = self._chunk_duration
        return self

    def __next__(self):
        if self.active:
            if self.frequency <= 0.0:
                if self.frequency < 0.0:
                    self.log.error("Overriding negative frequency to 0")
                sample = np.zeros(self.frames_per_chunk)

            else:
                sample = self.amplitude * np.sin(self.phase + (2 * np.pi * self.frequency) * np.linspace(self._chunk_start_time, self._chunk_end_time, num=self.frames_per_chunk, endpoint = False))

            self._chunk_start_time = self._chunk_end_time
            self._chunk_end_time += self._chunk_duration

            return sample.astype(np.float32)

        else:
            return np.zeros(self.frames_per_chunk, dtype=np.float32)

    def __deepcopy__(self, memo):
        return SineWaveOscillator(self.sample_rate, self.frames_per_chunk, name="SineWaveOscillator")

"""
def sin_generator(frequency, amplitude, sample_rate, frames_per_chunk):
    ""
        Generator. Inputs parameters of the sine wave, outputs an array for the next chunk. It's an input to StreamPlayer and doesn't call it.
    ""
    chunk_duration = frames_per_chunk / sample_rate
    chunk_start_time = 0.0
    chunk_end_time = chunk_duration
    phase = 0.0

    while True:
        if frequency <= 0.0:
            if frequency < 0.0:
                log.error("Overriding negative frequency to 0")
            amplitude = 0.0
            wave = np.zeroes(frames_per_chunk)
        
        else:
            wave = amplitude * np.sin(phase + (2 * np.pi * frequency) * np.linspace(chunk_start_time, chunk_end_time, num=frames_per_chunk, endpoint = True))

        chunk_start_time = chunk_end_time
        chunk_end_time += chunk_duration

        yield wave.astype(np.float32)
"""