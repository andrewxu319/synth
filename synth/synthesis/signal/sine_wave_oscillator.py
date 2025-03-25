import logging

import numpy as np

from .oscillator import Oscillator

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
        # if self.active:
        if self.frequency <= 0.0:
            if self.frequency < 0.0:
                self.log.error("Overriding negative frequency to 0")
            sample = np.zeros(self.frames_per_chunk)

        else:
            sample = self.amplitude * np.sin(self.phase + (2 * np.pi * self.frequency) * np.linspace(self._chunk_start_time, self._chunk_end_time, num=self.frames_per_chunk, endpoint = False))

        self._chunk_start_time = self._chunk_end_time
        self._chunk_end_time += self._chunk_duration

        return sample.astype(np.float32)

        # else:
        #     return np.zeros(self.frames_per_chunk, dtype=np.float32)

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