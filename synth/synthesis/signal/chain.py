# chain = signal chain = the order in which audio signals from oscillators pass through various effects

import logging
from copy import deepcopy

from .component import Component
from .oscillator import Oscillator

class Chain:
    def __init__(self, root_component: Component): # only takes in root most component. all child components will be accessible under the root component anyway
        self.log = logging.getLogger(__name__)
        self._root_component = root_component
    
    def __iter__(self):
        self.root_iter = iter(self._root_component)
        return self
        
    def __next__(self):
        chunk = next(self.root_iter)
        return chunk
    
    def __deepcopy__(self, memo):
        # print(f"Deep copying chain!")
        return Chain(deepcopy(self._root_component, memo))
    
    def __str__(self):
        string = "--- Signal Chain ---\n"
        string += str(self._root_component)
        return string
    
    @property
    def active(self):
        """
        The active status.
        The chain is considered active when the root component is active
        """
        return self._root_component.active
    
    @active.setter
    def active(self, value):
        self._root_component.active = value
        # print(f"Chain {self._root_component} active is {value}! Executed from chain.py, 40") # ACTIVE CHECK
    
    def get_components_by_class(self, cls): # cls = class
        components = []

        def search_subcomponents(component):
            if isinstance(component, cls):
                components.append(component)
            if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)
        
        search_subcomponents(self._root_component)
        return components

    def get_components_by_control_tag(self, control_tag):
        components = []

        def search_subcomponents(component):
            if hasattr(component, "control_tag") and component.control_tag == control_tag:
                components.append(component)
            if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)
        
        search_subcomponents(self._root_component)
        return components

    def note_on(self, frequency):
        for osc in self.get_components_by_class(Oscillator):
            osc.frequency = frequency
        self.active = True

    def note_off(self):
        # Setting the root component active status should propagate down the tree
        self.active = False # cuz only single voice