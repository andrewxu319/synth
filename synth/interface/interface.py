import tkinter as tk

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

window = tk.Tk()

window.geometry("800x500")
window.title("Synthesizer")

label = tk.Label(window, text="Synthesizer", font=("Calibri", 18))
label.pack(padx=20, pady=20)

textbox = tk.Text(window, height=3, font=("Calibri", 16))
textbox.pack(padx=20, pady=20)

button_frame = tk.Frame(window)
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)

button_1 = tk.Button(button_frame, text="Button 1", font=("Calibri", 18))
button_1.grid(row=0, column=0, sticky=tk.W+tk.E)

button_2 = tk.Button(button_frame, text="Button 2", font=("Calibri", 18))
button_2.grid(row=0, column=1, sticky=tk.W+tk.E)

button_3 = tk.Button(button_frame, text="Button 3", font=("Calibri", 18))
button_3.grid(row=0, column=2, sticky=tk.W+tk.E)

button_4 = tk.Button(button_frame, text="Button 4", font=("Calibri", 18))
button_4.grid(row=1, column=0, sticky=tk.W+tk.E)

button_5 = tk.Button(button_frame, text="Button 5", font=("Calibri", 18))
button_5.grid(row=1, column=1, sticky=tk.W+tk.E)

button_6 = tk.Button(button_frame, text="Button 6", font=("Calibri", 18))
button_6.grid(row=1, column=2, sticky=tk.W+tk.E)

button_frame.pack(fill="x")

# entry = tk.Entry(window, font=("Calibri", 30))
# entry.pack(padx=20, pady=20)

# button = tk.Button(window, text="Button", font=("Calibri", 18))
# button.pack(padx=50, pady=50)

window.mainloop()