# FIX LATER

import logging
import threading
import queue

from .. import message_builder as mb
from ..midi.implementation import Implementation

class UiListener(threading.Thread):
    """
    Listens for MIDI messages on a given port and sends them to the synth mailbox.
    """
    def __init__(self, thread_mailbox: queue.Queue, ui_mailbox: queue.Queue, synth_mailbox: queue.Queue):
        super().__init__(name=f"ui-listener")
        self.log = logging.getLogger(__name__)
        self.thread_mailbox = thread_mailbox # The mailbox that receives commands from the main thread. Namely the 'exit' command to shut down gracefully.
        self.ui_mailbox = ui_mailbox # Mailbox to communicate between ui itself and this listener
        self.synth_mailbox = synth_mailbox # The OUT mailbox where we send the parsed commands to be played by the synth
    
    def run(self): # overrides default run(). alternative for target/arg. this is what happens when it's executed
        should_run = True
        # in_port = None

        # try:
        #     in_port = mido.open_input(self.port_name)
        #     self.log.info(f"Opened port {self.port_name}")
        # except:
        #     self.log.error(f"Failed to open MIDI port at {self.port_name}. Closing the listener thread.")
        #     should_run = False
        
        while should_run:
            # Receive MIDI messages from the port and send them to the synth mailbox
            # receive() stops and waits for a message
            if msg := self.ui_mailbox.get(): # "if inport.receive() returns a value, assign it to a variable named msg".
                match msg["type"]:
                    case "note_on":
                        ctrl_msg = mb.builder().sender("ui").note_on().with_note(msg["note"]).on_channel(msg["channel"]).build() # builder() has its own methods with_note() and on_channel()
                        self.synth_mailbox.put(ctrl_msg)
                    case "note_off":
                        ctrl_msg = mb.builder().sender("ui").note_off().with_note(msg["note"]).on_channel(msg["channel"]).build() # builder() has its own methods with_note() and on_channel()
                        self.synth_mailbox.put(ctrl_msg)
                    case "control_change":
                        control = Implementation[msg["control_implementation"]].value
                        ctrl_msg = mb.builder().sender("ui").control_change().on_channel(msg["channel"]).with_cc_number(control).with_value(msg["value"]).build()
                        self.synth_mailbox.put(ctrl_msg)
                    case "stop":
                        self.log.info("Received midi STOP message")
                    case _:
                        self.log.info(f"Matched unknown MIDI message: {msg}")
                        
            # Receive MIDI messages from thread_mailbox / interface (only exit message)
            # get_nowait raises queue.Empty exception if there is nothing in the queue
            # We don't want to block this thread checking for thread command messages
            try:
                if mail := self.thread_mailbox.get_nowait(): # Return an item if one is immediately available, else raise QueueEmpty.
                    match mail.split():
                        case ["exit"]:
                            self.log.info("Got exit command.")
                            should_run = False
                        case _:
                            self.log.info(f"Matched unknown mailbox message: {mail}")
            except queue.Empty:
                pass
        
        return