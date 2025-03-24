import numpy as np

def sine_wave_oscillator(amplitude, phase, frequency, t):
    return amplitude * np.sin(phase + (2 * np.pi * frequency * t))

print(sine_wave_oscillator(1, 0, 440, np.linspace(0, np.pi * 2, 100)))