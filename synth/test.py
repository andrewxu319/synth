import numpy as np

# class BaseIter():
#     def __init__():
#         pass

#     def __iter__(self):
#         return self

def base_iter(max_value):
    chunk_index = 0
    while chunk_index < max_value:
        yield chunk_index * 6.0 + np.arange(6, dtype=np.float32)
        chunk_index += 1

class Delay():
    def __init__(self, sample_rate, frames_per_chunk, name="Delay", control_tag="delay") -> None: # initialization parameters = instance of a "delay plugin". cant be changed. the actual delay time etc is changed thru setting "delay.delay_time"
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        # self.subcomponents = subcomponents
        # self.delay_buffer_length = 4.0 # in seconds. think of this buffer as our recording. It acts like a loop of tape, with the write head constantly overwriting the oldest sound with the new audio signal.
        self.delay_time = 0.0
        self.chunks_elapsed = 0
        self.base_iter_instance = base_iter(10)

    
    def __iter__(self):
        # self.subcomponent_iter = iter(self.subcomponents[0])
        self.base_iter_instance = base_iter(10)
        return self
    
    def __next__(self):
        mix = next(self.base_iter_instance)
        start_index = self.chunks_elapsed * self.frames_per_chunk

        if self.delay_time > 0:
            if self.chunks_elapsed < self.chunks_to_wait: # havent reached point to start delay signal yet
                # start_index = self.chunks_elapsed * self.frames_per_chunk
                self.delay_buffer[start_index: start_index + self.frames_per_chunk] = mix
                self.chunks_elapsed += 1
            else:
                print(f"Delay buffer: {self.delay_buffer}")
                mix[:self.frames_into_chunk] += self.next_chunk_start_addition
                # print(mix[:self.frames_into_chunk])
                # print(self.next_chunk_start_addition)
                mix[self.frames_into_chunk:] += self.delay_buffer[:self.frames_into_chunk]
                self.delay_buffer[start_index:] = mix[:self.frames_into_chunk]
                self.next_chunk_start_addition = self.delay_buffer[self.frames_into_chunk : self.frames_per_chunk]

                self.delay_buffer = np.roll(self.delay_buffer, -self.frames_per_chunk)
                # print(self.delay_buffer[self.delay_frames - self.frames_per_chunk : self.chunks_elapsed * self.frames_per_chunk])
                # print(mix[self.frames_into_chunk:])
                self.delay_buffer[self.delay_frames - self.frames_per_chunk : self.chunks_elapsed * self.frames_per_chunk] = mix[self.frames_into_chunk:] # complete rest of chunk
                # self.chunks_elapsed += 1
        
        return mix
    
    @property
    def delay_time(self):
        return self._delay_time
    
    @delay_time.setter
    def delay_time(self, value):
        self._delay_time = value
        self.delay_frames = int(self.delay_time * self.sample_rate)
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.frames_into_chunk = self.delay_frames % self.frames_per_chunk
        self.next_chunk_start_addition = np.zeros(self.frames_into_chunk, np.float32)
        self.chunks_to_wait = self.delay_frames // self.frames_per_chunk
# base_iter_instance = base_iter(10)
delay = Delay(12, 6)
delay.delay_time = 0.75
print(next(delay)) # 1
print(next(delay)) # 2
print(next(delay)) # 3
print(next(delay)) # 4
print(next(delay)) # 5
print(next(delay)) # 6


"""
0 1 2 3 4 5
6 7 8 9 11 13
15 17 19 21 23 25
27 30 33 36 39 42
45 48 51 54 58 62

"""


import tkinter as tk
from tkinter import messagebox

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

class GUI:
    def __init__(self):
        self.window = tk.Tk()

        self.window.geometry("800x500")
        self.window.title("Synthesizer")

        self.menubar = tk.Menu(self.window)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Close", command=self.on_closing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close 2", command=self.on_closing)

        self.actionmenu = tk.Menu(self.menubar, tearoff=0)
        self.actionmenu.add_command(label="Hi", command=self.show_message)

        self.menubar.add_cascade(menu=self.filemenu, label="File")
        self.menubar.add_cascade(menu=self.actionmenu, label="Action")
        self.window.config(menu=self.menubar)

        self.label = tk.Label(self.window, text="Message", font=("Calibri", 18))
        self.label.pack(padx=10, pady=10)

        self.textbox = tk.Text(self.window, height=5, font=("Calibri", 16))
        self.textbox.bind("<KeyPress>", self.shortcut)
        self.textbox.pack(padx=10, pady=10)

        self.checkbox_state = tk.IntVar()        
        self.checkbox = tk.Checkbutton(self.window, text="Show messagebox", font=("Calibri", 16), variable=self.checkbox_state)
        self.checkbox.pack(padx=10, pady=10)

        self.button = tk.Button(self.window, text="Show Message", font=("Calibri", 16), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        # self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
    
    def show_message(self):
        if self.checkbox_state.get() == 0:
            print(self.textbox.get("1.0", tk.END))
        else:
            messagebox.showinfo(title="Message", message=self.textbox.get("1.0", tk.END))
    
    def shortcut(self, event):
        if event.keysym == "Return" and event.state==4:
            self.show_message()
    
    def on_closing(self):
        if messagebox.askyesno(title="Quit?", message="Quit?"):
            self.window.destroy()

GUI()