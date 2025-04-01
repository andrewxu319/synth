import logging
from time import sleep
import queue
import os
import sys
from optparse import OptionParser

import numpy as np

from . import settings
from .synthesizer import Synthesizer
import synth.midi as midi
from synth.midi.midi_listener import MidiListener

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="midi_port", default=None, help="MIDI port to listen on", metavar="MIDI PORT") # python -m synth -p "KOMPLETE KONTROL A49 MIDI 0"
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s [%(levelname)s] %(module)s [%(funcName)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    log = logging.getLogger(__name__)
    log.info("toy synth")

    available_ports = midi.get_available_controllers()
    log.info(f"Available MIDI ports: {available_ports}")

    listener_mailbox = queue.Queue()
    synth_mailbox = queue.Queue()

    midi_listen_port = options.midi_port if options.midi_port else settings.auto_attach
    # midi_listen_port = available_ports[0] # !!!!!!!!!!!
    log.info(f"Using MIDI port {midi_listen_port}")
    midi_listener = MidiListener(listener_mailbox, synth_mailbox, midi_listen_port)
    
    synthesizer = Synthesizer(settings.sample_rate, settings.frames_per_chunk, synth_mailbox, 4, settings.output_device)
    try: # our two threads
        midi_listener.start()
        synthesizer.start()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        log.info("Caught keyboard interrupt. Exiting the program.")
        os._exit(1)
    
    # listener_mailbox.put("exit")
    # synth_mailbox.put("exit")
    # midi_listener.join() # wait for midi_listener to terminate
    # synthesizer.join()
    # sys.exit(0)