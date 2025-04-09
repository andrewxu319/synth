import logging
from typing import List
from copy import deepcopy

import numpy as np

from ..component import Component
from ..oscillator import Oscillator

class Envelope(Component):
    def __init__(self, sample_rate, buffer_size, subcomponents: List["Component"] = [], name="Envelope", control_tag="envelope"):
        super().__init__(sample_rate, buffer_size, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        self.active = True # delete later
        self.oscillators = self.get_oscillators()
        # change later
        self.attack = 1.0
        self.decay = 0.4
        self.sustain = 0.5
        self.release = 0.5
        self.wet = 1.0

        self.attack_frames = round(self.attack * self.sample_rate)
        self.decay_frames = round(self.decay * self.sample_rate)
        self.release_frames = round(self.release * self.sample_rate)

        self.ads_multiplier_array_length = 4 * self.sample_rate # fixed value so changing envelope mid note doesnt break things
        # one_filler = np.full((self.ads_multiplier_array_length), 1.0)
        self.ads_multiplier_array = np.concatenate((np.linspace(0, 1.0, num=self.attack_frames), np.linspace(1.0, self.sustain, num=self.decay_frames)))
        self.ads_multiplier_array = np.pad(self.ads_multiplier_array, (0, self.ads_multiplier_array_length - len(self.ads_multiplier_array)), mode="constant", constant_values=self.sustain)

        self.r_multiplier_array_length = 4 * self.sample_rate
        self.r_multiplier_array = np.linspace(1.0, 0, num=self.release_frames)
        self.r_multiplier_array = np.pad(self.r_multiplier_array, (0, self.r_multiplier_array_length - len(self.r_multiplier_array)), mode="constant", constant_values=0.0)

        self.release_buffer = np.zeros(self.buffer_size) # stores last chunk of subcomponent signal & loops it for release

        self.ads_on = False
        self.r_on = False

    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0]) # one subcomponent. apply to mixer if global
        return self

    def __next__(self):
        if self.active:
            dry_signal = next(self.subcomponent_iter)
            # wet_signal = dry_signal # TEMP

            if self.ads_on:
                # print("ads")
                wet_signal = dry_signal
                self.release_buffer = np.copy(dry_signal)
                print(self.release_buffer[0:5])

            #     # # print(self.ads_multiplier_array[:self.buffer_size])
            #     # wet_signal *= self.ads_multiplier_array[:self.buffer_size]
            #     # self.ads_multiplier_array = np.roll(self.ads_multiplier_array, -self.buffer_size)
            #     # self.ads_multiplier_array[-self.buffer_size:] = self.sustain
            
            elif self.r_on:
                # print("r")
                wet_signal = self.release_buffer
                print(wet_signal[0:5])
                
            #     # if np.max(self.r_multiplier_array) == 0.0: # cant be negative cuz volume
            #     #     self.r_on = False
            #     #     return

            #     # wet_signal *= self.r_multiplier_array[:self.buffer_size]
            #     # self.r_multiplier_array = np.roll(self.r_multiplier_array, -self.buffer_size)
            #     # self.ads_multiplier_array[-self.buffer_size:] = 0.0
            #     # if np.max(wet_signal) != 0.0:
            #     #     print(wet_signal)
            
            else:
                wet_signal = np.zeros(self.buffer_size)

            mix = dry_signal * (1 - self.wet) + wet_signal * self.wet
            return mix.astype(np.float32)
        else:
            return next(self.subcomponent_iter)
    
    def note_on(self):
        print("note on!")
        self.ads_on = True

        for oscillator in self.oscillators:
            oscillator.amplitude = 1
    
    def note_off(self):
        print("note off!")
        self.ads_on = False
        self.r_on = True

        for oscillator in self.oscillators:
            oscillator.amplitude = 0.0
    
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
        copy.active = self.active
        copy.attack = self.attack
        copy.decay = self.decay
        copy.sustain = self.sustain
        copy.release = self.release
        copy.wet = self.wet
        self.log.info(f"deep copied envelope {self.name} with active {self.active}")
        return copy