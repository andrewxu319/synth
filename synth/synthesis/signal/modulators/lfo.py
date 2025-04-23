from queue import Queue
import logging
import numpy as np
from typing import Callable
from threading import Thread
import time
import sys

from ..oscillator import Oscillator
from ....midi import message_builder as mb

class Lfo(Oscillator):
    def __init__(self, sample_rate: int, buffer_size: int, formula: Callable, mailbox: Queue, name: str="Lfo", control_tag: str="lfo"):
        super().__init__(sample_rate, buffer_size, formula, name=name, control_tag=control_tag)
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.refresh_time = 1 / self.sample_rate

        self.channel = 0
        self.cc_number = 0
        self.value_range = (0.0, 1.0)
    
    def start(self):
        thread = Thread(target=self.start_thread)
        self.start_time = time.time()
        # breakpoint()
        thread.start()

    def start_thread(self):
        from ..fx.gain import OscillatorGain
        while True:
            try:
                output = self.value_range[0] + (self.value_range[1] - self.value_range[0]) * (self.formula(self.frequency, self.phase, 0.5, time.time() - self.start_time) + 0.5) # frequency in seconds
                # ctrl_msg = mb.builder().sender("midi").control_change().on_channel(self.channel).with_component("global").with_cc_number(self.cc_number).with_value(round(output)).build()
                # self.mailbox.put(ctrl_msg)
                # print(ctrl_msg)
                for voice in self.voices:
                    components = voice.signal_chain.get_components_by_class(OscillatorGain)
                    for component in components:
                        component.amplitude = output
                time.sleep(200 * self.refresh_time)

            except KeyboardInterrupt:
                break
        sys.exit()
            

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, value):
        try:
            self._active = bool(value)
            self._frequency = 0.0 if not self._active else self._frequency
            try:
                self.log.info(f"Lfo {self.name} active set to {self.active}")
            except:
                self.log.info(f"Lfo active set to {self.active}")
        except:
            self.log.error(f"Unable to set with value {value}, type {type(value)}")

    def __deepcopy__(self, memo):
        # logging.info(f"Deep copying oscillator {self.name} with active {self.active}")
        copy = Lfo(self.sample_rate, self.buffer_size, self.formula, name=self.name, control_tag=self.control_tag)
        copy.active = self.active
        copy.target = self.target
        copy.refresh_time = self.refresh_time
        return copy


"""
frequency
phase
set phase degrees
amplitude
active
"""