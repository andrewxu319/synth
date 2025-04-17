from PyQt6.QtWidgets import QMainWindow, QCheckBox, QApplication
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        widget = QCheckBox()

        widget.stateChanged.connect(self.show_state)
        widget.setChecked(False) # This prints nothing. I want it to print 0.
        widget.setChecked(True) # This prints 2

        self.setCentralWidget(widget)

    def show_state(self, state):
        print(state)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()