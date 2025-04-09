import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

class Menu(QtWidgets.QMenuBar):
    def __init__(self, preset_handler, parent=None):
        super(Menu, self).__init__(parent)
        self.preset_handler = preset_handler
        self.parent = parent
        
        file_menu = self.addMenu("&File")

        save_current_preset_action = QtGui.QAction(QtGui.QIcon(), "Save Current Preset", self)
        save_current_preset_action.triggered.connect(self.save_current_preset)

        open_preset_action = QtGui.QAction(QtGui.QIcon(), "Open Preset", self)
        open_preset_action.triggered.connect(self.open_preset)

        save_preset_action = QtGui.QAction(QtGui.QIcon(), "Save Preset", self)
        save_preset_action.triggered.connect(self.save_preset)

        file_menu.addAction(save_current_preset_action)
        file_menu.addAction(open_preset_action)
        file_menu.addAction(save_preset_action)
    
    def save_current_preset(self):
        if self.preset_handler.file_path == "":
            self.save_preset()
            return
        
        self.preset_handler.save(self.preset_handler.file_path, self.parent)

        self.parent.setWindowTitle(f"{self.file_path.split("/")[-1].split(".")[-2]} - Synth")

        message_box = QtWidgets.QMessageBox()
        message_box.setText(f'Succesfully saved preset "{self.preset_handler.file_path.split("/")[-1].split(".")[-2]}"!')
        message_box.exec()

    def open_preset(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setWindowTitle("Open Preset")
        file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        file_path = file_dialog.getOpenFileName(self, self.tr("Open File"), "presets", self.tr("*.json"))[0]

        if file_path != "":
            self.preset_handler.load(file_path, self.parent)
            
            self.parent.setWindowTitle(f"{file_path.split("/")[-1].split(".")[-2]} - Synth")
    
    def save_preset(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setWindowTitle("Save Preset")
        file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        file_path = file_dialog.getSaveFileName(self, self.tr("Save File"), "presets", self.tr("*.json"))[0]

        if file_path != "":
            self.preset_handler.save(file_path, self.parent)
            
            self.parent.setWindowTitle(f"{file_path.split("/")[-1].split(".")[-2]} - Synth")
