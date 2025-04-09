import logging
from typing import List
import random

class Component():
    """
    ---component = a thing that manipulates sound. an oscillator (subcomponent) or a mixer (parent component) etc
    ---"when u call next() on parent component, it calls next() on subcomponents
    ---iterator that returns chunks as arrays

    Represents a base signal component. A signal component is an iterator.
    The iterator should return an ndarray of size <buffer_size> with type numpy.float32

    A component can have a list of subcomponents, which should also be iterators.

    A component must implement
    __iter__
    __next__
    __deepcopy__
    """

    def __init__(self, sample_rate: int, buffer_size: int, subcomponents: List["Component"]=[], name="Component", control_tag: str=""):
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.subcomponents = subcomponents
        self.active = False
        self.name = name + "#" + str(random.randint(0, 9999))
        self.control_tag = control_tag

    def __iter__(self):
        return self
    
    def __next__(self):
        # i think this means to not call Component as an iterator directly but instead call a child class
        self.log.error("Child class should override the __next__ method")
        raise NotImplementedError
    
    def __deepcopy__(self, memo):
        # ignore
        self.log.error("Invoked deepcopy on base class")
        raise NotImplementedError
    
    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value):
        try:
            int_value = int(value)
            if int_value > 0:
                self._sample_rate = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Couldn't set sample_rate with value {value}")

    @property
    def buffer_size(self):
        return self._buffer_size
    
    @buffer_size.setter
    def buffer_size(self, value):
        try:
            int_value = int(value)
            if int_value > 0:
                self._buffer_size = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Couldn't set buffer_size with value {value}")

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        try:
            self._active = value
        except ValueError:
            self.log.error(f"Couldn't set active with value {value}")

    # @property
    # def active(self):
    #     """
    #     The active status.
    #     When a component is active it should perform its function
    #     When it is inactive it should either return zeros or bypass the signal.
    #     If the component is a generator it should generate zeros when inactive.
    #     """
    #     return self._active
    
    # @active.setter
    # def active(self, value):
    #     try:
    #         bool_val = bool(value)
    #         self._active = bool_val
    #         for subcomponent in self.subcomponents: # !!!!!!!!!!
    #             subcomponent.active = bool_val
    #     except ValueError:
    #         self.log.error(f"Couldn't set active with value {value}")
    
    def get_subcomponents_str(self, component, depth):
        """
        Returns an indented string representing the tree of subcomponents
        """
        output = ""
        for _ in range(depth):
            output += "  "
        output += f"{component.name}\n"
        if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
            for subcomponent in component.subcomponents:
                output += self.get_subcomponents_str(subcomponent, depth + 1)
        return output
    
    def __str__(self):
        output = self.get_subcomponents_str(self, 0)
        return output