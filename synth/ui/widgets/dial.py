from PyQt6.QtWidgets import QDial

class Dial(QDial):
    def __init__(self):
        super().__init__()
    
    def setValue(self, value: int):
        if self.value() == value:
            if self.value() == self.maximum():
                super().setValue(value - 1)
            else:
                super().setValue(value + 1)
        super().setValue(value)