from PyQt6.QtWidgets import QCheckBox

class CheckBox(QCheckBox):
    def __init__(self):
        super().__init__()

    def setChecked(self, value: bool):
        if self.isChecked() == value:
            super().setChecked(not value)
        super().setChecked(value)