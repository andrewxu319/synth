import sys

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

class Color(QtWidgets.QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Synth")
        self.resize(800, 500)

        # Top Section
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)

        top_section = QtWidgets.QHBoxLayout()

        osc_section = Color("Red")
        top_section.addWidget(osc_section, 3)

        filter_section = Color("Yellow")
        top_section.addWidget(filter_section, 2)

        layout.addLayout(top_section, 3)

        # Bottom Section
        bottom_section = Color("blue")
        layout.addWidget(bottom_section, 2)

        # Central widget
        osc_tab = QtWidgets.QWidget()
        osc_tab.setLayout(layout)

        # Tabs
        tabs = QtWidgets.QTabWidget()
        tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

        tabs.addTab(osc_tab, "Osc")
        tabs.addTab(Color("orange"), "FX")

        self.setCentralWidget(tabs)
        ###
    
app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()