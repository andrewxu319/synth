import threading
import logging
import os

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .osc_tab import OscTab
from .fx_tab import FxTab
from .menu import Menu

class Color(QtWidgets.QWidget):
    def __init__(self, color):
        super().__init__()

        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox
        self.log = logging.getLogger(__name__)

        self.setWindowTitle("Synth")
        self.resize(800, 500)

        # Tabs
        tabs = QtWidgets.QTabWidget()
        tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

        self.osc_tab = OscTab(self.ui_listener_mailbox)
        self.fx_tab = FxTab(self.ui_listener_mailbox)

        tabs.addTab(self.osc_tab, "Osc")
        tabs.addTab(self.fx_tab, "FX")

        self.setCentralWidget(tabs)
        
        # Menu
        menu = Menu(self)
        self.setMenuBar(menu)
    
    def closeEvent(self, event):
        event.accept()
        self.log.info("UI closed. Exiting the program.")
        os._exit(1)

class Ui(threading.Thread):
    def __init__(self, ui_listener_mailbox):
        super().__init__(name="UI Thread")
        self.ui_listener_mailbox = ui_listener_mailbox
    
    def run(self):
        app = QtWidgets.QApplication([])

        self.window = MainWindow(self.ui_listener_mailbox)
        self.window.show()

        app.exec()

        return
