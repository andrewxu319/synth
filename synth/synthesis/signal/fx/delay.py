import logging
from copy import deepcopy

import numpy as np

from ...signal.component import Component

class Delay(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents, name="Delay", control_tag="delay") -> None: # initialization parameters = instance of a "delay plugin". cant be changed. the actual delay time etc is changed thru setting "delay.delay_time"
        # print(f"FPC {frames_per_chunk}")
        super().__init__(sample_rate, frames_per_chunk, subcomponents, name, control_tag)
        self.log = logging.getLogger(__name__)
        # self.delay_buffer_length = 4.0 # in seconds. think of this buffer as our recording. It acts like a loop of tape, with the write head constantly overwriting the oldest sound with the new audio signal.
        self.active = False
        self.delay_time = 0.0
        self.chunks_elapsed = 0
        self.feedback = 0.0
    
    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0])
        self.subcomponent_iter.active = True
        return self
    
    def __next__(self):
        mix = next(self.subcomponent_iter)
        start_index = self.chunks_elapsed * self.frames_per_chunk

        if self.active and self.feedback > 0.0 and self.delay_time > 0:
            if self.chunks_elapsed < self.chunks_to_wait: # havent reached point to start delay signal yet
                # start_index = self.chunks_elapsed * self.frames_per_chunk
                # print(start_index)
                # print(self.frames_per_chunk)
                # print(self.delay_buffer[start_index: start_index + self.frames_per_chunk])
                # print(np.shape(mix))
                self.delay_buffer[start_index: start_index + self.frames_per_chunk] = mix
                self.chunks_elapsed += 1
                # print(f"chunks_elapsed = {self.chunks_elapsed}")
            else:
                # print(f"Delay buffer: {self.delay_buffer}")
                # print("FLAG")
                # print(np.shape(mix[:self.frames_into_chunk]))
                # print(np.shape(self.next_chunk_start_addition))
                mix[:self.frames_into_chunk] += self.next_chunk_start_addition * self.feedback #WORK ON THIS TMRW
                # print(mix[:self.frames_into_chunk])
                # print(self.next_chunk_start_addition)
                mix[self.frames_into_chunk:] += self.delay_buffer[:self.frames_per_chunk - self.frames_into_chunk] * self.feedback

                self.delay_buffer[start_index:] = mix[:self.frames_into_chunk]
                self.next_chunk_start_addition = self.delay_buffer[self.frames_per_chunk - self.frames_into_chunk : self.frames_per_chunk]

                self.delay_buffer = np.roll(self.delay_buffer, -self.frames_per_chunk)
                # print(self.delay_buffer[self.delay_frames - self.frames_per_chunk : self.chunks_elapsed * self.frames_per_chunk])
                # print(mix[self.frames_into_chunk:])
                self.delay_buffer[self.delay_frames - self.frames_per_chunk : self.chunks_elapsed * self.frames_per_chunk] = mix[self.frames_into_chunk:] # complete rest of chunk
                # self.chunks_elapsed += 1
                
                """ IDT THIS DOES ANYTHING
                if max(self.delay_buffer) < 0.000005 and max(self.next_chunk_start_addition) < 0.000005:
                    self.delay_buffer *= 0.0
                    self.next_chunk_start_addition *= 0.0
                else:
                    
                    print(f"buffer {max(self.delay_buffer)}")
                    print(f"next {max(self.next_chunk_start_addition)}")
                """
                                
        return np.astype(mix, np.float32)
    
    def __deepcopy__(self, memo):
        copy = Delay(self.sample_rate, self.frames_per_chunk, [deepcopy(subcomponent, memo) for subcomponent in self.subcomponents], name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.delay_time = self.delay_time
        copy.feedback = self.feedback
        copy.chunks_elapsed = self.chunks_elapsed
        copy.next_chunk_start_addition = self.next_chunk_start_addition
        return copy

    @property
    def delay_time(self):
        return self._delay_time

    @delay_time.setter
    def delay_time(self, value):
        self._delay_time = value
        self.delay_frames = int(self.delay_time * self.sample_rate)
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.frames_into_chunk = self.delay_frames % self.frames_per_chunk
        self.next_chunk_start_addition = np.zeros(self.frames_into_chunk, np.float32)
        self.chunks_to_wait = self.delay_frames // self.frames_per_chunk
        # print(f"chunks_to_wait = {self.chunks_to_wait}")
    