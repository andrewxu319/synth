import logging

import numpy as np

from .sawtooth_wave_oscillator import SawtoothWaveOscillator

class TriangleWaveOscillator(SawtoothWaveOscillator):
    def __init__(self, sample_rate: int, frames_per_chunk: int, name: str="TriangleWaveOscillator"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
        self.log = logging.getLogger(__name__)
    
    def __next__(self):
        sawtooth_wave = super().__next__()
        triangle_wave = (abs(sawtooth_wave) - 0.5) * 2
        return triangle_wave.astype(np.float32)
    
    def __deepcopy__(self, memo):
        return TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk, name="TriangleWaveOscillator")