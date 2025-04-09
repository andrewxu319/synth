import logging
from copy import deepcopy

import numpy as np

from .generator import Generator

class NoiseGenerator(Generator):
    def __init__(self, sample_rate: int, buffer_size: int, name: str="NoiseGenerator"):
        super().__init__(sample_rate, buffer_size, name=name)
        self.log = logging.getLogger(__name__)
        self.amplitude = 0.1

    def __iter__(self):
        self.rng = np.random.default_rng()
        # print(super().__iter__())
        return super().__iter__() # returns itself

    def __next__(self):
        if self.active:
            noise = self.amplitude * self.rng.uniform(-1.0, 1.0, self.buffer_size)
            return noise.astype(np.float32)
        else:
            return np.zeros(self.buffer_size, dtype=np.float32)

    def __deepcopy__(self, memo):
        copy = NoiseGenerator(self.sample_rate, self.buffer_size)
        copy.active = self.active
        return copy