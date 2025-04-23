import logging
import numpy as np

from .oscillator import Oscillator

class OscillatorLibrary():
    def __init__(self, sample_rate: int, buffer_size: int):
        self.log = logging.getLogger(__name__)

        self.oscillators = [
            {
                "name": "SineWaveOscillator",
                "control_tag": "osc_0",
                "formula": (lambda frequency, phase, amplitude, t: # t can be either a an array or a number
                            amplitude * np.sin(phase + (2 * np.pi * frequency * t)))
            },
            {
                "name": "SquareWaveOscillator",
                "control_tag": "osc_1",
                "formula": (lambda frequency, phase, amplitude, t:
                            amplitude * np.sign(np.sin(phase + (2 * np.pi * frequency * t))))
            },
            {
                "name": "SawtoothWaveOscillator",
                "control_tag": "osc_2",
                "formula": (lambda frequency, phase, amplitude, t:
                            amplitude * (t / (1 / frequency) - np.floor(t / (1 / frequency) + 0.5)))
            },
            {
                "name": "TriangleWaveOscillator",
                "control_tag": "osc_3",
                "formula": (lambda frequency, phase, amplitude, t:
                            (abs(amplitude * (t / (1 / frequency) - np.floor(t / (1 / frequency) + 0.5))) - 0.5) * 2)
            },
            {
                "name": "NoiseOscillator",
                "control_tag": "osc_4",
                "formula": (lambda frequency, phase, amplitude, t:
                            amplitude * np.random.default_rng().uniform(-1.0, 1.0, buffer_size))
            }
        ]
        
        self.log.info(f"Oscillators created:\n{self.oscillators}")
    