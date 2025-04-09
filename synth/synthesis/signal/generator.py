import logging

from .component import Component

class Generator(Component): # child class of Component---type of Component
    def __init__(self, sample_rate: int, buffer_size: int, name: str="Generator"):
        """
            The base class for any signal component that can generate signal.
            Generators should be leaf nodes on the signal tree. That means they have no subcomponents.
        """
        super().__init__(sample_rate, buffer_size, [], name=name)
        self.log = logging.getLogger(__name__)
    
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        try:
            bool_val = bool(value)
            self._active = bool_val
            for subcomponent in self.subcomponents: # !!!!!!!!!!
                subcomponent.active = bool_val
        except ValueError:
            self.log.error(f"Couldn't set active with value {value}")