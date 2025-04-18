# Guitar Chorus Effect

import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Parameters
sample_rate = 100  # Sample rate in Hz
duration = 5  # Duration in seconds
frequency = 1  # Frequency of the guitar note (A4)
depth = 0.02  # Depth of the chorus effect
rate = 5  # Rate of modulation in Hz

# Time array
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Original guitar signal (sine wave)
guitar_signal = 0.5 * np.sin(2 * np.pi * frequency * t)

# Chorus effect
modulation = depth * np.sin(2 * np.pi * rate * t)
chorus_signal = guitar_signal + np.interp(t + modulation, t, guitar_signal)

# Normalize the signal
chorus_signal /= np.max(np.abs(chorus_signal))

# Save to a WAV file
write('guitar_chorus_effect.wav', sample_rate, (chorus_signal * 32767).astype(np.int16))

# Plotting the original and chorus signals
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.title('Original Guitar Signal')
plt.plot(t, guitar_signal)
plt.subplot(2, 1, 2)
plt.title('Guitar Signal with Chorus Effect')
plt.plot(t, chorus_signal)
plt.tight_layout()
plt.show()
