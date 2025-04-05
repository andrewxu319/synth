import threading

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
    def __init__(self, number, mailbox):
        super().__init__()
        self.number = number
        self.mailbox = mailbox

        layout = QtWidgets.QHBoxLayout()

        active_checkbox = QtWidgets.QCheckBox()
        active_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)

        gain_dial = QtWidgets.QDial()
        gain_dial.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        gain_dial.setRange(0, 127)
        gain_dial.setSingleStep(1)
        gain_dial.setMinimumSize(1,1)
        gain_dial.valueChanged.connect(self.set_gain)

        layout.addWidget(QtWidgets.QLabel(text=f"Osc {number}"))
        layout.addWidget(active_checkbox)
        layout.addStretch()
        layout.addWidget(QtWidgets.QLabel(text=f"Gain:"))
        layout.addWidget(gain_dial)

        self.setLayout(layout)
        # (later type), active, gain, low pass, high pass
    
    def set_gain(self, value):
        self.mailbox.put({
            "type": "control_change",
            "channel": 0, # doesnt rly matter
            "control_implementation": f"OSC_{self.number}_AMP",
            "value": value
        })

class OscTab(QtWidgets.QWidget):
    def __init__(self, mailbox):
        super().__init__()
        self.mailbox = mailbox

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)

        # Top section
        top_section = QtWidgets.QHBoxLayout()

        ## Osc section
        osc_section = QtWidgets.QGridLayout()

        osc_section.addWidget(OscillatorSection("1", self.mailbox), 0, 0)
        osc_section.addWidget(OscillatorSection("2", self.mailbox), 1, 0)
        osc_section.addWidget(OscillatorSection("3", self.mailbox), 2, 0)
        osc_section.addWidget(OscillatorSection("4", self.mailbox), 3, 0)
        osc_section.addWidget(OscillatorSection("5", self.mailbox), 4, 0)

        top_section.addLayout(osc_section, 3)

        filter_section = Color("Yellow")
        top_section.addWidget(filter_section, 2)

        layout.addLayout(top_section, 3)

        # Bottom section
        bottom_section = Color("blue")
        layout.addWidget(bottom_section, 2)

        # Central widget
        self.setLayout(layout)