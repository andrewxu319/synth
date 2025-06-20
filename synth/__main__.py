import logging
from time import sleep
import queue
import os
import sys
from optparse import OptionParser
import threading
from PyQt6 import QtWidgets

import numpy as np

from . import settings
from .synthesizer import Synthesizer
import synth.midi as midi
from synth.midi.midi_listener import MidiListener
from synth.ui.ui_listener import UiListener
from .ui.main_window import Ui, MainWindow
from .ui.preset_handler import PresetHandler

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="midi_port", default=None, help="MIDI port to listen on", metavar="MIDI PORT") # python -m synth -p "KOMPLETE KONTROL A49 MIDI 0"
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.INFO,  # warning
                        format='%(asctime)s [%(levelname)s] %(module)s [%(funcName)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    log = logging.getLogger(__name__)
    log.info("toy synth")

    # # catching errors https://www.reddit.com/r/learnpython/comments/7or35q/questionpyqt5threading_my_gui_crash_whit_no_error/
    # sys._excepthook = sys.excepthook 
    # def exception_hook(exctype, value, traceback):
    #     log.error(exctype, value, traceback)
    #     sys._excepthook(exctype, value, traceback) 
    #     sys.exit(1)
    # sys.excepthook = exception_hook

    available_ports = midi.get_available_controllers()
    log.info(f"Available MIDI ports: {available_ports}")

    thread_mailbox = queue.Queue()
    ui_listener_mailbox = queue.Queue()
    synth_mailbox = queue.Queue()

    midi_listen_port = options.midi_port if options.midi_port else settings.auto_attach
    # midi_listen_port = available_ports[0] # !!!!!!!!!!!
    log.info(f"Using MIDI port {midi_listen_port}")

    midi_listener = MidiListener(thread_mailbox, synth_mailbox, midi_listen_port)

    synthesizer = Synthesizer(settings.sample_rate, settings.buffer_size, synth_mailbox, settings.voices, settings.output_device)

    ui_listener = UiListener(thread_mailbox, ui_listener_mailbox, synth_mailbox)
    
    preset_handler = PresetHandler(synthesizer)

#
    ui = Ui(ui_listener_mailbox, midi_listener, synthesizer, ui_listener, preset_handler)


#

    # synthesizer.ui = ui # fix this later---make synthesizer not require ui. make ui pass osc focus messages

    try:
        current_threads = 0 # temp---logging thing

        # midi_listener.start()
        # ui_listener.start()
        # synthesizer.start()
        # ui.start()
        # while True:
        #     thread_count = threading.active_count()
        #     if current_threads != thread_count:
        #         log.info(f"Thread count changed to: {thread_count}")
        #     sleep(1)
    except KeyboardInterrupt:
        preset_handler.autosave()      
        log.info("Caught keyboard interrupt. Exiting the program.")
        os._exit(1)
    
    # listener_mailbox.put("exit")
    # synth_mailbox.put("exit")
    # midi_listener.join() # wait for midi_listener to terminate
    # synthesizer.join()
    # sys.exit(0)