import logging
from functools import partial

import PyQt6.QtCore as QtCore
import PyQt6.QtGui as QtGui
import PyQt6.QtWidgets as QtWidgets

from .widgets.color import Color

# class Dial(QtWidgets.QDial):
#     def __init__(self):
#         super().__init__()
    
#     def paintEvent(self, event):
#         opt = QtWidgets.QStyleOptionSlider()
#         self.initStyleOption(opt)

#         # construct a QRectF that uses the minimum between width and height, 
#         # and adds some margins for better visual separation
#         # this is partially taken from the fusion style helper source
#         width = opt.rect.width()
#         height = opt.rect.height()
#         r = min(width, height) / 2
#         r -= r / 50
#         d_ = r / 6
#         dx = opt.rect.x() + d_ + (width - 2 * r) / 2 + 1
#         dy = opt.rect.y() + d_ + (height - 2 * r) / 2 + 1
#         br = QtCore.QRectF(dx + .5, dy + .5, 
#             int(r * 2 - 2 * d_ - 2), 
#             int(r * 2 - 2 * d_ - 2))

#         penColor = self.palette().dark().color()
#         qp = QtGui.QPainter(self)
#         qp.setRenderHints(qp.RenderHint.Antialiasing)
#         qp.setPen(QtGui.QPen(penColor, 4))
#         qp.drawEllipse(br)

#         # find the "real" value ratio between minimum and maximum
#         realValue = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
#         # compute the angle at which the dial handle should be placed, assuming
#         # a range between 240° and 300° (moving clockwise)
#         angle = 240 - 300 * realValue
#         # create a polar line for the position of the handle; this can also
#         # be done using the math module with some performance improvement
#         line = QtCore.QLineF.fromPolar(r * .6, angle)
#         line.translate(br.center())
#         ds = r / 5
#         # create the handle rect and position it at the end of the polar line
#         handleRect = QtCore.QRectF(0, 0, ds, ds)
#         handleRect.moveCenter(line.p2())
#         qp.setPen(QtGui.QPen(penColor, 2))
#         qp.drawEllipse(handleRect)

class OscillatorSection(QtWidgets.QWidget):
    # (later type), active, gain, low pass, high pass
    def __init__(self, number, ui_listener_mailbox):
        super().__init__()
        self.number = number
        self.ui_listener_mailbox = ui_listener_mailbox
        self.focus = False
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QHBoxLayout()

        active_checkbox = QtWidgets.QCheckBox()
        active_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        active_checkbox.stateChanged.connect(self.set_active)

        self.gain_dial = QtWidgets.QDial()
        self.gain_dial.setRange(0, 127)
        self.gain_dial.setSingleStep(1)
        self.gain_dial.setMinimumSize(1,1)
        self.gain_dial.sliderMoved.connect(self.set_gain)

        self.hpf_dial = QtWidgets.QDial()
        self.hpf_dial.setRange(0, 127)
        self.hpf_dial.setSingleStep(1)
        self.hpf_dial.setMinimumSize(1,1)
        self.hpf_dial.sliderMoved.connect(self.set_hpf)

        self.lpf_dial = QtWidgets.QDial()
        self.lpf_dial.setRange(0, 127)
        self.lpf_dial.setSingleStep(1)
        self.lpf_dial.setMinimumSize(1,1)
        self.lpf_dial.sliderMoved.connect(self.set_lpf)

        layout.addWidget(QtWidgets.QLabel(text=f"Osc {number + 1}"))
        layout.addWidget(active_checkbox)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Gain:"))
        layout.addWidget(self.gain_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"HPF Freq:"))
        layout.addWidget(self.hpf_dial)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"LPF Freq:"))
        layout.addWidget(self.lpf_dial)

        self.setLayout(layout)

    def set_active(self, state):
        self.ui_listener_mailbox.put({
            "type": "ui_message",
            "channel": 0,
            "number": self.number,
            "value": state == 2 # use midi cc instead?
        })

    def set_gain(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "control_implementation": f"OSC_{self.number + 1}_AMP",
            "value": value
        })
    
    def set_hpf(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "control_implementation": f"HPF_CUTOFF",
            "value": value
        })

    def set_lpf(self, value):
        self.ui_listener_mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "control_implementation": f"LPF_CUTOFF",
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


    