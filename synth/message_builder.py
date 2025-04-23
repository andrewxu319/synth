import logging

def builder():
    return CommandBuilder()

class MessageBuilder():
    """
    Base class for constructing messages to send to the controller.
    """ 

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self._message = ""
    
    @property
    def message(self):
        return self._message
    
    @message.setter
    def message(self, value):
        self._message = value
    
    def build(self) -> str:
        return str(self.message).strip()

class CommandBuilder(MessageBuilder):
    """
    The main class for starting a command message to the controller.
    Messages should be constructed by calling builder() and then chaining
    the methods to build the message. When the message is complete, call .build()
    """

    """
    For example, if you called

    my_msg = builder().note_on()
    Python
    you would get back an instance of NoteParameterBuilder with its message initialized to " note_on". Let's see how these builder classes can add to the message.
    """
    def __init__(self, message="") -> None:
        super().__init__()
        self.message = message

    def sender(self, value):
        if value == "midi":
            self.message += "midi"
        elif value == "ui":
            self.message += "ui"
        else:
            self.log.error(f"Unable to set sender: {value}")
            raise ValueError

        return CommandBuilder(self.message)
    
    def note_on(self):
        self.message += " note_on"
        return NoteParameterBuilder(self.message)
    
    def note_off(self):
        self.message += " note_off"
        return NoteParameterBuilder(self.message)
    
    def control_change(self):
        self.message += " control_change"
        return CCParameterBuilder(self.message)
    
    def set_active(self):
        self.message += " set_active"
        return UIParameterBuilder(self.message)

class NoteParameterBuilder(MessageBuilder):
    """
    Note messages currently need to specify note and channel in that order.
    """
    def __init__(self, message_base: str) -> None: # message_base is what's before it in the message. rest of the message
        super().__init__()
        self.message = message_base

    def with_note(self, note):
        try:
            int_val = int(note)
            if int_val < 0 or int_val > 127:
                raise ValueError
            self.message += f" -n {int_val}"
        except ValueError:
            self.log.error(f"Unable to set note: {note}")
            raise
        
        return NoteParameterBuilder(self.message)
        # print(builder().note_on().with_note(30).message) => " note_on -n 30"
    
    def with_velocity(self, value):
        try:
            int_val = int(value)
            if int_val < 0 or int_val > 127:
                raise ValueError
            self.message += f" -e {int_val}"
        except ValueError:
            self.log.error(f"Unable to set velocity: {value}")
            raise

        return NoteParameterBuilder(self.message)
    
    def on_channel(self, channel):
        try:
            int_val = int(channel)
            if int_val < 0 or int_val > 15:
                raise ValueError
            self.message += f" -c {int_val}"
        except ValueError:
            self.log.error(f"Unable to set channel: {channel}")
            raise
    
        return NoteParameterBuilder(self.message)
        # print(builder().note_on().with_note(30).on_channel(5)._message) => " note_on -n 30 -c 5"
        # notice how this is j a note_on command
        # NoteParameterBuilder just returns to the part of the interface that asks u what attribute u want to add

class CCParameterBuilder(MessageBuilder):
    """
    Control Changes messages currently need to specify channel, control number, and value in that order.
    """
    def __init__(self, message_base: str) -> None:
        super().__init__()
        self.message = message_base
    
    def on_channel(self, channel):
        try:
            int_val = int(channel)
            if int_val < 0 or int_val > 15:
                raise ValueError
            self.message += f" -c {int_val}"
        except ValueError:
            self.log.error(f"Unable to set channel: {channel}")
            raise

        return CCParameterBuilder(self.message)

    def with_component(self, value):
        self.message += f" -o {value}"
        return CCParameterBuilder(self.message)

    def with_cc_number(self, value):
        self.message += f" -n {value}"
        # doesnt need to be number
        return CCParameterBuilder(self.message)

    def with_value(self, value):
        try:
            int_val = int(value)
            if int_val < 0 or int_val > 127:
                raise ValueError
            self.message += f" -v {int_val}"
        except ValueError:
            self.log.error(f"Unable to set CC value {value}! MIDI values are from 0-127")
            raise

        return CCParameterBuilder(self.message)

class UIParameterBuilder(MessageBuilder):
    def __init__(self, message_base: str) -> None:
        super().__init__()
        self.message = message_base
  
    def on_channel(self, channel):
        try:
            int_val = int(channel)
            if int_val < 0 or int_val > 15:
                raise ValueError
            self.message += f" -c {int_val}"
        except ValueError:
            self.log.error(f"Unable to set channel: {channel}")
            raise
    
        return UIParameterBuilder(self.message)
    
    def with_component(self, value):
        self.message += f" -o {value}"
            
        return UIParameterBuilder(self.message)

    def with_value(self, value):
        self.message += f" -v {value}"

        return UIParameterBuilder(self.message)