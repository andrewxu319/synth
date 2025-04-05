from enum import Enum

class Implementation(Enum):
    OSC_1_AMP = 14
    OSC_2_AMP = 15
    OSC_3_AMP = 16
    OSC_4_AMP = 17
    OSC_5_AMP = 18
    HPF_CUTOFF = 19
    LPF_CUTOFF = 20
    # lpf_1_CUTOFF = 19
    # lpf_2_CUTOFF = 20
    # lpf_3_CUTOFF = 21
    # lpf_4_CUTOFF = 22
    # lpf_5_CUTOFF = 23
    DELAY_TIME = 21
    DELAY_FEEDBACK = 22
    DELAY_WET = 23