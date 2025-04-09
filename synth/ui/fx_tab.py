import logging

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .widgets.color import Color

class DelayFx(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox
        self.log = logging.getLogger(__name__)
    
        layout = QtWidgets.QHBoxLayout()

        self.active_checkbox = QtWidgets.QCheckBox()
        self.active_checkbox.stateChanged.connect(self.set_active)

        self.delay_time_dial = QtWidgets.QDial()
        self.delay_time_dial.setRange(0, 127)
        self.delay_time_dial.setSingleStep(1)
        self.delay_time_dial.setMinimumSize(1,1)
        self.delay_time_dial.valueChanged.connect(self.set_delay_time) # might need to change to sliderReleased

        self.delay_feedback_dial = QtWidgets.QDial()
        self.delay_feedback_dial.setRange(0, 127)
        self.delay_feedback_dial.setSingleStep(1)
        self.delay_feedback_dial.setMinimumSize(1,1)
        self.delay_feedback_dial.valueChanged.connect(self.set_delay_feedback)

        self.delay_wet_dial = QtWidgets.QDial()
        self.delay_wet_dial.setRange(0, 127)
        self.delay_wet_dial.setSingleStep(1)
        self.delay_wet_dial.setMinimumSize(1,1)
        self.delay_wet_dial.valueChanged.connect(self.set_delay_wet)

        layout.addWidget(QtWidgets.QLabel(text=f"Delay"))
        layout.addWidget(self.active_checkbox)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Time:"))
        layout.addWidget(self.delay_time_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Feedback:"))
        layout.addWidget(self.delay_feedback_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Wet:"))
        layout.addWidget(self.delay_wet_dial)

        self.setLayout(layout)

        # Initial conditions
        self.active_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.delay_time_dial.setValue(0)
        self.delay_feedback_dial.setValue(0)
        self.delay_wet_dial.setValue(0)

    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "set_active",
            "channel": 0,
            "component": "delay",
            "value": state == 2 # use midi cc instead?
        })

    def set_delay_time(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "delay",
            "control_implementation": "DELAY_TIME",
            "value": value
        })

    def set_delay_feedback(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "delay",
            "control_implementation": "DELAY_FEEDBACK",
            "value": value
        })

    def set_delay_wet(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "delay",
            "control_implementation": "DELAY_WET",
            "value": value
        })

class FxTab(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)

        self.delay_fx = DelayFx(self.ui_listener_mailbox)
        layout.addWidget(self.delay_fx)

        # Central widget
        self.setLayout(layout)
