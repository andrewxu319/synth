import logging

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .widgets.color import Color

class OscillatorSection(QtWidgets.QWidget):
    # (later type), active, gain, low pass, high pass
    def __init__(self, number, ui_listener_mailbox):
        super().__init__()
        self.number = number
        self.ui_listener_mailbox = ui_listener_mailbox
        self.focus = False
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QHBoxLayout()

        self.active_checkbox = QtWidgets.QCheckBox()
        self.active_checkbox.stateChanged.connect(self.set_active)

        self.gain_dial = QtWidgets.QDial()
        self.gain_dial.setRange(0, 127)
        self.gain_dial.setSingleStep(1)
        self.gain_dial.setMinimumSize(1,1)
        self.gain_dial.valueChanged.connect(self.set_gain)

        self.hpf_cutoff_dial = QtWidgets.QDial()
        self.hpf_cutoff_dial.setRange(0, 127)
        self.hpf_cutoff_dial.setSingleStep(1)
        self.hpf_cutoff_dial.setMinimumSize(1,1)
        self.hpf_cutoff_dial.valueChanged.connect(self.set_hpf_cutoff)

        self.hpf_wet_dial = QtWidgets.QDial()
        self.hpf_wet_dial.setRange(0, 127)
        self.hpf_wet_dial.setSingleStep(1)
        self.hpf_wet_dial.setMinimumSize(1,1)
        self.hpf_wet_dial.valueChanged.connect(self.set_hpf_wet)


        self.lpf_cutoff_dial = QtWidgets.QDial()
        self.lpf_cutoff_dial.setRange(0, 127)
        self.lpf_cutoff_dial.setSingleStep(1)
        self.lpf_cutoff_dial.setMinimumSize(1,1)
        self.lpf_cutoff_dial.valueChanged.connect(self.set_lpf_cutoff)

        self.lpf_wet_dial = QtWidgets.QDial()
        self.lpf_wet_dial.setRange(0, 127)
        self.lpf_wet_dial.setSingleStep(1)
        self.lpf_wet_dial.setMinimumSize(1,1)
        self.lpf_wet_dial.valueChanged.connect(self.set_lpf_wet)

        layout.addWidget(QtWidgets.QLabel(text=f"Osc {number + 1}"))
        layout.addWidget(self.active_checkbox)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Gain:"))
        layout.addWidget(self.gain_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"HPF Freq:"))
        layout.addWidget(self.hpf_cutoff_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"HPF Wet:"))
        layout.addWidget(self.hpf_wet_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"LPF Freq:"))
        layout.addWidget(self.lpf_cutoff_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"LPF Wet:"))
        layout.addWidget(self.lpf_wet_dial)

        self.setLayout(layout)

        # Initial conditions
        self.active_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        self.gain_dial.setValue(127)
        self.hpf_cutoff_dial.setValue(0)
        self.lpf_cutoff_dial.setValue(127)

    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "set_active",
            "channel": 0,
            "component": f"osc_{self.number}",
            "value": state == 2 # use midi cc instead?
        })

    def set_gain(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": f"osc_{self.number}",
            "control_implementation": f"OSC_{self.number + 1}_AMP",
            "value": value
        })
    
    def set_hpf_cutoff(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": f"osc_{self.number}",
            "control_implementation": f"HPF_CUTOFF",
            "value": value
        })
    
    def set_hpf_wet(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": f"osc_{self.number}",
            "control_implementation": f"HPF_WET",
            "value": value
        })

    def set_lpf_cutoff(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": f"osc_{self.number}",
            "control_implementation": f"LPF_CUTOFF",
            "value": value
        })
    
    def set_lpf_wet(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": f"osc_{self.number}",
            "control_implementation": f"LPF_WET",
            "value": value
        })

class OscTab(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)

        # Top section
        top_section = QtWidgets.QHBoxLayout()

        ## Osc section
        osc_section = QtWidgets.QGridLayout()

        self.osc_list = []
        for i in range(5):
            self.osc_list.append(OscillatorSection(i, self.ui_listener_mailbox))
            osc_section.addWidget(self.osc_list[i], i, 0)

        self.osc_list[0].mouseReleaseEvent = lambda _: self.focus(0) # loop doesnt work??
        self.osc_list[1].mouseReleaseEvent = lambda _: self.focus(1)
        self.osc_list[2].mouseReleaseEvent = lambda _: self.focus(2)
        self.osc_list[3].mouseReleaseEvent = lambda _: self.focus(3)
        self.osc_list[4].mouseReleaseEvent = lambda _: self.focus(4)
        self.focus(0)
                
        top_section.addLayout(osc_section, 3)

        filter_section = Color("Yellow")
        top_section.addWidget(filter_section, 2)

        layout.addLayout(top_section, 3)

        # Bottom section
        bottom_section = Color("blue")
        layout.addWidget(bottom_section, 2)

        # Central widget
        self.setLayout(layout)

    def focus(self, number):
        self.focused_osc = self.osc_list[number]
        self.focused_osc.focus = True
        self.focused_osc.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.focused_osc.setStyleSheet('background-color: #fcf6cc')

        remaining_numbers = list(range(5))
        remaining_numbers.pop(number)
        for i in remaining_numbers:
            self.osc_list[i].setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, False)
            self.osc_list[i].setStyleSheet('background-color: #ffffff')


    