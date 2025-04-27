from PyQt6.QtWidgets import QComboBox

class ComboBox(QComboBox):
    def __init__(self):
        super().__init__()

    def setCurrentIndex(self, index):
        if index == self.currentIndex:
            if index == 0:
                super().setCurrentIndex(index + 1)
            else:
                super().setCurrentIndex(index - 1)
        super().setCurrentIndex(index)
    
    def setCurrentText(self, text):
        if text == self.currentText:
            super().setCurrentText(text + ".")
        super().setCurrentIndex(text)