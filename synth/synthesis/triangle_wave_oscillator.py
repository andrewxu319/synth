import logging

import numpy as np

from .sawtooth_wave_oscillator import SawtoothWaveOscillator

class TriangleWaveOscillator(SawtoothWaveOscillator):
    def __init__(self, sample_rate: int, buffer_size: int, name: str="TriangleWaveOscillator"):
        super().__init__(sample_rate, buffer_size, name=name)
        self.log = logging.getLogger(__name__)
    
    def __next__(self):
        sawtooth_wave = super().__next__()
        triangle_wave = (abs(sawtooth_wave) - 0.5) * 2
        return triangle_wave.astype(np.float32)
    
    def __deepcopy__(self, memo):
        copy = TriangleWaveOscillator(self.sample_rate, self.buffer_size, name="TriangleWaveOscillator")
        copy.active = self.active
        return copy