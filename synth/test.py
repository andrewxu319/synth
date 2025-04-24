import numpy as np

amplitude = 0.5
phase = 0.0
frequency = 0.5
t = np.linspace(0, 10)
value_range = [50, 60]

output = (abs(amplitude * (t * frequency - np.floor(t * frequency + 0.5))) - 0.5) * 4 + 1

output = value_range[0] + (value_range[1] - value_range[0]) * (output + 1)

print(output)
print(np.max(output))
print(np.min(output))