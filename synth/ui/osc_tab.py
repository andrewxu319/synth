import logging

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .widgets.checkbox import CheckBox
from .widgets.dial import Dial
from .widgets.combobox import ComboBox
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

        self.active_checkbox = CheckBox()
        self.active_checkbox.stateChanged.connect(self.set_active)

        self.gain_dial = Dial()
        self.gain_dial.setRange(0, 127)
        self.gain_dial.setSingleStep(1)
        self.gain_dial.setMinimumSize(1,1)
        self.gain_dial.valueChanged.connect(self.set_gain)

        self.hpf_cutoff_dial = Dial()
        self.hpf_cutoff_dial.setRange(0, 127)
        self.hpf_cutoff_dial.setSingleStep(1)
        self.hpf_cutoff_dial.setMinimumSize(1,1)
        self.hpf_cutoff_dial.valueChanged.connect(self.set_hpf_cutoff)

        self.hpf_wet_dial = Dial()
        self.hpf_wet_dial.setRange(0, 127)
        self.hpf_wet_dial.setSingleStep(1)
        self.hpf_wet_dial.setMinimumSize(1,1)
        self.hpf_wet_dial.valueChanged.connect(self.set_hpf_wet)


        self.lpf_cutoff_dial = Dial()
        self.lpf_cutoff_dial.setRange(0, 127)
        self.lpf_cutoff_dial.setSingleStep(1)
        self.lpf_cutoff_dial.setMinimumSize(1,1)
        self.lpf_cutoff_dial.valueChanged.connect(self.set_lpf_cutoff)

        self.lpf_wet_dial = Dial()
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

        # # Initial conditions
        # self.active_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        # self.gain_dial.setValue(127)
        # self.hpf_cutoff_dial.setValue(0)
        # self.lpf_cutoff_dial.setValue(127)

    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "ui_message",
            "name": "set_active",
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

class EnvelopeSection(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QGridLayout()

        self.attack_dial = Dial()
        self.attack_dial.setRange(0, 127)
        self.attack_dial.setSingleStep(1)
        self.attack_dial.setMinimumSize(1,1)
        self.attack_dial.valueChanged.connect(self.set_attack)

        self.decay_dial = Dial()
        self.decay_dial.setRange(0, 127)
        self.decay_dial.setSingleStep(1)
        self.decay_dial.setMinimumSize(1,1)
        self.decay_dial.valueChanged.connect(self.set_decay)

        self.sustain_dial = Dial()
        self.sustain_dial.setRange(0, 127)
        self.sustain_dial.setSingleStep(1)
        self.sustain_dial.setMinimumSize(1,1)
        self.sustain_dial.valueChanged.connect(self.set_sustain)

        self.release_dial = Dial()
        self.release_dial.setRange(0, 127)
        self.release_dial.setSingleStep(1)
        self.release_dial.setMinimumSize(1,1)
        self.release_dial.valueChanged.connect(self.set_release)

        layout.addWidget(QtWidgets.QLabel(text="Envelope"), 0, 0)
        attack_layout = QtWidgets.QHBoxLayout()
        attack_layout.addWidget(QtWidgets.QLabel(text=f"Attack:"))
        attack_layout.addWidget(self.attack_dial)
        layout.addLayout(attack_layout, 1, 0)

        decay_layout = QtWidgets.QHBoxLayout()
        decay_layout.addWidget(QtWidgets.QLabel(text=f"Decay:"))
        decay_layout.addWidget(self.decay_dial)
        layout.addLayout(decay_layout, 1, 1)

        sustain_layout = QtWidgets.QHBoxLayout()
        sustain_layout.addWidget(QtWidgets.QLabel(text=f"Sustain:"))
        sustain_layout.addWidget(self.sustain_dial)
        layout.addLayout(sustain_layout, 2, 0)

        release_layout = QtWidgets.QHBoxLayout()
        release_layout.addWidget(QtWidgets.QLabel(text=f"Release:"))
        release_layout.addWidget(self.release_dial)
        layout.addLayout(release_layout, 2, 1)

        self.setLayout(layout)
    
    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "ui_message",
            "name": "set_active",
            "channel": 0,
            "component": "envelope",
            "value": state == 2 # use midi cc instead?
        })

    def set_attack(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "envelope",
            "control_implementation": "ENV_ATTACK",
            "value": value
        })

    def set_decay(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "envelope",
            "control_implementation": "ENV_DECAY",
            "value": value
        })

    def set_sustain(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "envelope",
            "control_implementation": "ENV_SUSTAIN",
            "value": value
        })

    def set_release(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "envelope",
            "control_implementation": "ENV_RELEASE",
            "value": value
        })

class LfoSection(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox
        self.log = logging.getLogger(__name__)

        self.focused_osc = 0

        self.parameters = {
            "": (), # none
            "Gain (Current Osc)": (f"oscillator_gain_{self.focused_osc}", "amplitude"),
            "HPF Cutoff (Current Osc)": (f"hpf_{self.focused_osc}", "cutoff"),
            "HPF Wet (Current Osc)": (f"hpf_{self.focused_osc}", "wet"),
            "LPF Cutoff (Current Osc)": (f"lpf_{self.focused_osc}", "cutoff"),
            "LPF Wet (Current Osc)": (f"lpf_{self.focused_osc}", "wet"),
            "Delay Time": ("delay", "delay_time"),
            "Delay Feedback": ("delay", "feedback"),
            "Delay Wet": ("delay", "wet"),
            "Attack": ("envelope", "attack"),
            "Decay": ("envelope", "decay"),
            "Sustain": ("envelope", "sustain"),
            "Release": ("envelope", "release"),
            "Velocity Sensitivity": ("velocity_gain", "velocity_sensitivity")
        }

        layout = QtWidgets.QGridLayout()

        # shape, parameter, frequency, amount. ACTIVE CHECKBOX

        self.shape_dropdown = ComboBox()
        self.shape_dropdown.addItems(["Sine", "Square", "Sawtooth", "Triangle"])
        self.shape_dropdown.currentIndexChanged.connect(self.set_shape)

        self.parameter_dropdown = ComboBox()
        self.parameter_dropdown.addItems(self.parameters.keys())
        self.parameter_dropdown.currentTextChanged.connect(self.set_parameter)

        self.frequency_dial = Dial()
        self.frequency_dial.setRange(0, 127)
        self.frequency_dial.setSingleStep(1)
        self.frequency_dial.setMinimumSize(1,1)
        self.frequency_dial.valueChanged.connect(self.set_frequency)

        self.amount_dial = Dial()
        self.amount_dial.setRange(0, 127)
        self.amount_dial.setSingleStep(1)
        self.amount_dial.setMinimumSize(1,1)
        self.amount_dial.valueChanged.connect(self.set_amount)

        layout.addWidget(QtWidgets.QLabel(text="LFO"), 0, 0)
        attack_layout = QtWidgets.QHBoxLayout()
        attack_layout.addWidget(QtWidgets.QLabel(text=f"Shape:"))
        attack_layout.addWidget(self.shape_dropdown)
        layout.addLayout(attack_layout, 1, 0)

        decay_layout = QtWidgets.QHBoxLayout()
        decay_layout.addWidget(QtWidgets.QLabel(text=f"Parameter:"))
        decay_layout.addWidget(self.parameter_dropdown)
        layout.addLayout(decay_layout, 1, 1)

        sustain_layout = QtWidgets.QHBoxLayout()
        sustain_layout.addWidget(QtWidgets.QLabel(text=f"Frequency:"))
        sustain_layout.addWidget(self.frequency_dial)
        layout.addLayout(sustain_layout, 2, 0)

        release_layout = QtWidgets.QHBoxLayout()
        release_layout.addWidget(QtWidgets.QLabel(text=f"Amount:"))
        release_layout.addWidget(self.amount_dial)
        layout.addLayout(release_layout, 2, 1)

        self.setLayout(layout)

    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "ui_message",
            "name": "set_active",
            "channel": 0,
            "component": "lfo",
            "value": state == 2 # use midi cc instead?
        })
    
    def set_shape(self, index):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0,
            "component": "lfo",
            "control_implementation": "LFO_SHAPE",
            "value": index # use midi cc instead?
        })

    def set_parameter(self, text):
        self.ui_listener_mailbox.put({
            "type": "ui_message",
            "name": "lfo_parameter",
            "channel": 0,
            "component": "lfo",
            "value": f"{self.parameters[text][0]}.{self.parameters[text][1]}" # use midi cc instead?
        })

    def set_frequency(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "lfo",
            "control_implementation": "LFO_FREQUENCY",
            "value": value
        })

    def set_amount(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "lfo",
            "control_implementation": "LFO_AMOUNT",
            "value": value
        })

class PerformanceSection(QtWidgets.QWidget):
    def __init__(self, ui_listener_mailbox):
        super().__init__()
        self.ui_listener_mailbox = ui_listener_mailbox
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QVBoxLayout()

        self.velocity_sensitivity_dial = Dial()
        self.velocity_sensitivity_dial.setRange(0, 127)
        self.velocity_sensitivity_dial.setSingleStep(1)
        self.velocity_sensitivity_dial.setMinimumSize(1,1)
        self.velocity_sensitivity_dial.valueChanged.connect(self.set_velocity_sensitivity)

        layout.addWidget(QtWidgets.QLabel(text=f"Velocity Sensitivity:"))
        layout.addWidget(self.velocity_sensitivity_dial)

        self.setLayout(layout)

    def set_velocity_sensitivity(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "component": "global",
            "control_implementation": f"VEL_SENSITIVITY",
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
        bottom_section = QtWidgets.QHBoxLayout()

        self.envelope_section = EnvelopeSection(self.ui_listener_mailbox)
        bottom_section.addWidget(self.envelope_section, 2)

        self.lfo_section = LfoSection(self.ui_listener_mailbox)
        bottom_section.addWidget(self.lfo_section, 2)

        self.performance_section = PerformanceSection(self.ui_listener_mailbox)
        bottom_section.addWidget(self.performance_section, 1)

        layout.addLayout(bottom_section, 2)

        # Central widget
        self.setLayout(layout)

    def focus(self, number):
        self.focused_osc = self.osc_list[number]
        self.focused_osc.focus = True
        self.focused_osc.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.focused_osc.setStyleSheet('background-color: #fcf6cc')
        try:
            self.lfo_section.focused_osc = self.focused_osc
        except AttributeError:
            pass

        remaining_numbers = list(range(5))
        remaining_numbers.pop(number)
        for i in remaining_numbers:
            self.osc_list[i].setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, False)
            self.osc_list[i].setStyleSheet('background-color: #ffffff')


    