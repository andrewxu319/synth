import logging
from typing import List
from copy import deepcopy

import numpy as np

from ..component import Component

class Envelope(Component):
    def __init__(self, sample_rate, buffer_size, subcomponents: List["Component"] = [], name="Envelope", control_tag="envelope"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.active = True # delete later
        # change later
        self.attack = 1.0
        self.decay = 0.4
        self.sustain = 0.5
        self.release = 0.3
        self.wet = 1.0

        self.attack_frames = round(self.attack * self.sample_rate)
        self.decay_frames = round(self.decay * self.sample_rate)
        self.release_frames = round(self.release * self.sample_rate)

        self.ad_multiplier_array_length = 4 * self.sample_rate # fixed value so changing envelope mid note doesnt break things
        # one_filler = np.full((self.ad_multiplier_array_length), 1.0)
        self.ad_multiplier_array = np.concatenate((np.linspace(0, 1.0, num=self.attack_frames), np.linspace(1.0, self.sustain, num=self.decay_frames)))
        self.ad_multiplier_array = np.pad(self.ad_multiplier_array, (0, self.ad_multiplier_array_length - len(self.ad_multiplier_array)), mode="constant", constant_values=self.sustain)

        self.ad_on = False
        self.s_on = False

    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        if self.active:
            dry_signal = next(self.subcomponent_iter)
            wet_signal = dry_signal ####################################################### DO SHIT HERE
            # if np.amax(dry_signal) != 0.0:
            #     print(dry_signal)
            if self.ad_on:
                print(self.ad_multiplier_array[:self.buffer_size])
                wet_signal *= self.ad_multiplier_array[:self.buffer_size]
                self.ad_multiplier_array = np.roll(self.ad_multiplier_array, -self.buffer_size)
                self.ad_multiplier_array[-self.buffer_size:] = self.sustain

            mix = dry_signal * (1 - self.wet) + wet_signal * self.wet
            return mix.astype(np.float32)
        else:
            return next(self.subcomponent_iter)
    
    def note_on(self):
        self.ad_on = True
    
    def note_off(self):
        self.ad_on = False
        self.r_on = True

    def __deepcopy__(self, memo):
        copy = Envelope(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.attack = self.attack
        copy.decay = self.decay
        copy.sustain = self.sustain
        copy.release = self.release
        copy.wet = self.wet
        self.log.info(f"deep copied envelope {self.name} with active {self.active}")
        return copy
