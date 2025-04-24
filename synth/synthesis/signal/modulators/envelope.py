# TO DO: ACTIVE

import logging
from typing import List
from copy import deepcopy
import time
import sys

import numpy as np

from ..component import Component
from ..oscillator import Oscillator

class Envelope(Component):
    def __init__(self, sample_rate, buffer_size, subcomponents: List["Component"] = [], name="Envelope", control_tag="envelope"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.refresh_time = 1 / self.sample_rate * self.buffer_size
        self.oscillators = self.get_oscillators()
        # change later
        self.attack = 0.3
        self._decay = 0.6
        self._sustain = 0.1
        self.release = 0.5
        self.wet = 1.0

        # self.ads_on = False
        # self.r_on = False

    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        return next(self.subcomponent_iter)
    
    @property
    def attack(self):
        return self._attack

    @attack.setter
    def attack(self, value):
        self._attack = value
        self.attack_values = np.linspace(0.0, 1.0, np.int32(np.floor(self.attack / self.refresh_time)))
        # self.attack_slope = 1.0 / value # to avoid division
    
    @property
    def decay(self):
        return self._decay
    
    @decay.setter
    def decay(self, value):
        self._decay = value
        self.decay_values = np.linspace(1.0, self.sustain, np.int32(np.floor(self.decay / self.refresh_time)))
        # self.decay_slope = (1.0 - self.sustain) / self.decay
    
    @property
    def sustain(self):
        return self._sustain

    @sustain.setter
    def sustain(self, value):
        self._sustain = value
        self.decay_values = np.linspace(1.0, self.sustain, np.int32(np.floor(self.decay / self.refresh_time)))
        # self.decay_slope = (1.0 - self.sustain) / self.decay
    
    def note_on(self):
        # self.ads_on = True
        
        # Attack
        # attack_start_time = time.time()
        # while (float(time.time()) <= (float(attack_start_time) + float(self.attack))) and (self.ads_on): # delete last two floats? test to see if it works
        #     # print(float(attack_start_time) + float(self.attack) - float(time.time()))
        #     for oscillator in self.oscillators:
        #         oscillator.amplitude = min(1, self.attack_slope * (time.time() - attack_start_time)) # precalculate division
        #         # print(oscillator.amplitude)
    #         time.sleep(self.refresh_time)
        for value in self.attack_values:
            for oscillator in self.oscillators:
                oscillator.amplitude = value # precalculate division
            time.sleep(self.refresh_time)

        # Decay
        # decay_start_time = time.time()
        # while (float(time.time()) <= (float(decay_start_time) + float(self.decay)) and (self.ads_on)):
        #     # print(float(time.time()) - (float(decay_start_time + self.decay)))

        #     for oscillator in self.oscillators:
        #         oscillator.amplitude = 1.0 - (self.decay_slope) * (time.time() - decay_start_time)
        #         # print(oscillator.amplitude)
        #     time.sleep(self.refresh_time)

        for value in self.decay_values:
            for oscillator in self.oscillators:
                oscillator.amplitude = value # precalculate division
            time.sleep(self.refresh_time)

        # for oscillator in self.oscillators:
        #     oscillator.amplitude = self.sustain

        sys.exit()
    
    def note_off(self, chain):
        # self.ads_on = False
        # self.r_on = True

        release_amplitudes = []
        for oscillator in self.oscillators:
            release_amplitudes.append(oscillator.amplitude)
        # print(release_amplitudes)
        release_start_time = time.time()
        while float(time.time()) <= (float(release_start_time) + float(self.release)):
            for i, oscillator in enumerate(self.oscillators):
                oscillator.amplitude = max(0, release_amplitudes[i] - (release_amplitudes[i] / self.release) * (time.time() - release_start_time))
            time.sleep(self.refresh_time)
        # print(float(time.time()) - float(release_start_time))
        # print(self.release)
        # print("release complete!")
        for oscillator in self.oscillators:
            # print(oscillator.amplitude)
            oscillator.amplitude = 0.0

        # self.r_on = False
        chain.active = False

        sys.exit()
    
    def terminate(self, chain):
        # self.ads_on = False
        for oscillator in self.oscillators:
            oscillator.amplitude = 0.0
        chain.active = False
        sys.exit()
    
    def get_oscillators(self): # cls = class
        components = []

        def search_subcomponents(component):
            if isinstance(component, Oscillator):
                components.append(component)
            if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)
        
        search_subcomponents(self)
        return components

    def __deepcopy__(self, memo):
        copy = Envelope(self.sample_rate, self.buffer_size, subcomponents=[deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.refresh_time = self.refresh_time
        # copy.oscillators = self.oscillators
        copy.attack = self.attack
        copy.decay = self.decay
        copy.sustain = self.sustain
        copy.release = self.release
        copy.wet = self.wet
        
        # copy.ads_on = self.ads_on
        # copy.r_on = self.r_on
        self.log.info(f"deep copied envelope {self.name}!")
        return copy