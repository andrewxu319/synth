from .signal.chain import Chain

class Voice:
    def __init__(self, signal_chain: Chain):
        self.signal_chain = iter(signal_chain) # j turns it into an iterator
        self.note_id = None
    
    @property
    def active(self):
        return self.signal_chain.active
    
    @active.setter
    def active(self, value):
        self.signal_chain.active = value
        # print(f"Voice {self} active is {value}! Executed from voice.py, 14") # ACTIVE CHECK
    
    def note_on(self, frequency, note_id):
        self.note_id = note_id
        self.signal_chain.note_on(frequency)
    
    def note_off(self):
        self.signal_chain.note_off()