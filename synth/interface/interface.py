from PyQt6.QtCore import Qt
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synth")
        self.resize(1200, 800)

        #################
        self.label = qtw.QLabel("Hi")

        self.input = qtw.QLineEdit()
        # self.input.textChanged.connect(self.label.setText)

        layout = qtw.QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)

        container = qtw.QWidget()
        container.setLayout(layout)
        #################

        self.setCentralWidget(container)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.label.setText("mouseMoveEvent")
    
    def contextMenuEvent(self, event):
        context_menu = qtw.QMenu(self)
        action_1 = qtg.QAction("item 1", self)
        action_1.triggered.connect(lambda: print("hi"))
        context_menu.addAction(action_1) # parent = self = MainWindow
        context_menu.addAction(qtg.QAction("item 2", self))
        context_menu.addAction(qtg.QAction("item 2", self))
        context_menu.exec(event.globalPos())
    
app = qtw.QApplication([])

window = MainWindow()
window.show()

app.exec()














# import tkinter as tk
# from tkinter import ttk
# from tkinter import messagebox
# from tkdial import Jogwheel

# from ctypes import windll
# windll.shcore.SetProcessDpiAwareness(1)

# class GUI:
#     def __init__(self):
#         self.window = tk.Tk()
#         self.window.geometry("800x500")
#         self.window.title("Synthesizer")

#         # Notebook widget
#         self.notebook = ttk.Notebook(self.window)

#         # Tab Osc
#         self.tab_osc = ttk.Frame(self.notebook)

#         self.top_half = tk.Frame(self.tab_osc, background="red")
        
#         self.osc_panel = tk.Frame(self.top_half, background="blue")
#         self.osc_panel_label = tk.Label(self.osc_panel, text="Oscillators", justify=tk.LEFT).pack(padx=10, pady=10)
#         self.osc_grid = tk.Grid()
#         self.osc_panel.pack(side=tk.LEFT, fill=tk.X, expand=1)

#         self.osc_panel = tk.Frame(self.top_half, background="green")
#         self.osc_panel_label = tk.Label(self.osc_panel, text="Filter", justify=tk.LEFT).pack(padx=10, pady=10)
#         self.osc_panel.pack(side=tk.RIGHT, fill=tk.X, expand=1)

#         self.top_half.pack(fill=tk.X, expand=0)

#         self.tab_fx = ttk.Frame(self.notebook)

#         self.notebook.add(self.tab_osc, text="Osc")
#         self.notebook.add(self.tab_fx, text="FX")
#         self.notebook.pack(fill=tk.BOTH, expand=1)
        
#         self.window.mainloop()
    
#     def show_message(self):
#         if self.checkbox_state.get() == 0:
#             print(self.textbox.get("1.0", tk.END))
#         else:
#             messagebox.showinfo(title="Message", message=self.textbox.get("1.0", tk.END))
    
#     def shortcut(self, event):
#         if event.keysym == "Return" and event.state==4:
#             self.show_message()
    
#     def on_closing(self):
#         self.window.destroy()

# GUI()

