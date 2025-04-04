import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

class Menu(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super(Menu, self).__init__(parent)

        file_menu = self.addMenu("&File")

        test_action = QtGui.QAction(QtGui.QIcon("bug.png"), "Test", self)
        test_action.triggered.connect(self.test_action_triggered)
        file_menu.addAction(test_action)
    
    def test_action_triggered(self):
        print("Test")
