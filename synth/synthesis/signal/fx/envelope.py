import logging
from typing import List
from copy import deepcopy

import numpy as np

from ..component import Component

class Envelope(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents: List["Component"] = [], name="Envelope", control_tag="envelope"):
        super().__init__(sample_rate, frames_per_chunk, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.attack = 0.0
        self.decay = 0.0
        self.sustain = 4.0
        self.release = 0.0
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        if self.active:
            dry_signal = next(self.subcomponent_iter)
            wet_signal = 0 ####################################################### DO SHIT HERE
            mix = dry_signal * (1 - self.wet) + wet_signal * self.wet
            return mix.astype(np.float32)
        else:
            return next(self.subcomponent_iter)

    def __deepcopy__(self, memo):
        copy = Envelope(self.sample_rate, self.frames_per_chunk, self.type, subcomponents=[deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.attack = self.attack
        copy.decay = self.decay
        copy.sustain = self.sustain
        copy.release = self.release
        copy.wet = self.wet
        self.log.info(f"deep copied filter {self.name} with active {self.active} and freq {self.cutoff}")
        return copy
