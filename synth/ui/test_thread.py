from time import sleep

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

class TestWorker(QtCore.QObject):
    def __init__(self):
        super().__init__()
    
    def run(self, word):
        while True:
            print(word)
            sleep(2)