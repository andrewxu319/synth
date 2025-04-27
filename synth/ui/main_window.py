import threading
import logging
import os
from time import sleep

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
    def __init__(self, ui_listener_mailbox, midi_listener, synthesizer, ui_listener, preset_handler):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.ui_listener_mailbox = ui_listener_mailbox
        # self.midi_listener = midi_listener
        # self.synthesizer = synthesizer
        # self.synthesizer.window = self
        self.ui_listener = ui_listener
        self.preset_handler = preset_handler

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
        menu = Menu(preset_handler, parent=self)
        self.setMenuBar(menu)

        # Load autosave
        try:
            self.preset_handler.load("presets/autosave.json", self)
        except Exception as e: # GIVE AN EXCEPTION LATER
            self.log.error(e)

        self.show()

    def closeEvent(self, event):
        event.accept()
        self.preset_handler.autosave()
        self.log.info("UI closed. Exiting the program.")
        os._exit(1)

class Ui(threading.Thread):
    def __init__(self, ui_listener_mailbox, midi_listener, synthesizer, ui_listener, preset_handler):
        super().__init__(name="UI Thread")
        self.ui_listener_mailbox = ui_listener_mailbox
        self.preset_handler = preset_handler

        app = QtWidgets.QApplication([])

        window = MainWindow(ui_listener_mailbox, midi_listener, synthesizer, ui_listener, preset_handler)
        window.show()

        # Creating threads for various processes
        self.midi_listener_thread = QtCore.QThread()
        self.midi_listener = midi_listener
        self.midi_listener.moveToThread(self.midi_listener_thread)
        self.midi_listener_thread.started.connect(self.midi_listener.run)
        self.midi_listener_thread.finished.connect(app.exit)
        self.midi_listener_thread.start()

        self.ui_listener_thread = QtCore.QThread()
        self.ui_listener = ui_listener
        self.ui_listener.moveToThread(self.ui_listener_thread)
        self.ui_listener_thread.started.connect(self.ui_listener.run)
        self.ui_listener_thread.finished.connect(app.exit)
        self.ui_listener_thread.start()

        self.synthesizer_thread = QtCore.QThread()
        self.synthesizer = synthesizer
        self.synthesizer.window = window
        self.synthesizer.moveToThread(self.synthesizer_thread)
        self.synthesizer_thread.started.connect(self.synthesizer.run)
        self.synthesizer_thread.finished.connect(app.exit)
        self.synthesizer_thread.start()

        app.exec()