import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .preset_handler import PresetHandler

class Menu(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super(Menu, self).__init__(parent)
        
        file_menu = self.addMenu("&File")

        open_preset_action = QtGui.QAction(QtGui.QIcon(), "Open Preset", self)
        open_preset_action.triggered.connect(self.open_preset)

        save_preset_action = QtGui.QAction(QtGui.QIcon(), "Save Preset", self)
        save_preset_action.triggered.connect(self.save_preset)

        file_menu.addAction(open_preset_action)
        file_menu.addAction(save_preset_action)
    
    def open_preset(self):
        print("Open preset")
    
    def save_preset(self):
        print("Open preset")
