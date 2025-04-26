from PyQt6 import QtWidgets
from PyQt6 import QtGui
from threading import Thread
import sys

class Color(QtWidgets.QWidget):
    def __init__(self, color):
        super().__init__()

        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)

class Ui(Thread):
    def __init__(self):
        super().__init__()
        app = QtWidgets.QApplication([])

        window = Color("red")
        window.show()

        app.exec()

ui = Ui()
ui.start()