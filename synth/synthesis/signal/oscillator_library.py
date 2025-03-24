import logging
import numpy as np

from .oscillator import Oscillator
from .sine_wave_oscillator import SineWaveOscillator

class OscillatorLibrary():
    def __init__(self, sample_rate: int, frames_per_chunk: int):
        self.oscillators = {
            "sine_wave_oscillator": Oscillator(sample_rate, frames_per_chunk,
                                                lambda frequency, phase, amplitude, t:
                                                amplitude * np.sin(phase + (2 * np.pi * frequency * t)),
                                                "SineWaveOscillator"),
            # "sine_wave_oscillator": SineWaveOscillator(sample_rate, frames_per_chunk),
            "square_wave_oscillator": Oscillator(sample_rate, frames_per_chunk,
                                                    lambda frequency, phase, amplitude, t:
                                                    np.sign(amplitude * np.sin(phase + (2 * np.pi * frequency * t))),
                                                    "SquareWaveOscillator"),
            "sawtooth_wave_oscillator": Oscillator(sample_rate, frames_per_chunk,
                                                    lambda frequency, phase, amplitude, t:
                                                    amplitude * (t / (1 / frequency) - np.floor(t / (1 / frequency) + 0.5)),
                                                    "SawtoothWaveOscillator"),
            "triangle_wave_oscillator": Oscillator(sample_rate, frames_per_chunk,
                                                    lambda frequency, phase, amplitude, t:
                                                    (abs(amplitude * (t / (1 / frequency) - np.floor(t / (1 / frequency) + 0.5))) - 0.5) * 2,
                                                    "TriangleWaveOscillator"),
            "noise_oscillator": Oscillator(sample_rate, frames_per_chunk,
                                            lambda frequency, phase, amplitude, t:
                                            amplitude * np.random.default_rng().uniform(-1.0, 1.0, frames_per_chunk),
                                            "NoiseOscillator")
        }
        
        self.log = logging.getLogger(__name__)
        self.log.info(f"Oscillators created:\n{self.oscillators.keys()}")
    