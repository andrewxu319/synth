import numpy as np

sample_rate = 44100
buffer_size = 256 # https://www.reddit.com/r/reasoners/comments/ar0pcw/what_is_your_sample_rate_and_buffer_size/
voices = 10

# auto_attach = "KOMPLETE KONTROL A49 MIDI 0"
auto_attach = "loopMIDI Port 0"

# output_device = 4
output_device = None

amp_values = np.linspace(0, 1, 128)
filter_cutoff_values = np.logspace(4, 14.3, 128, endpoint=True, base=2, dtype=np.float32)
filter_wet_values = np.linspace(0, 1, 128)
envelope_attack_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.499 # 0 to about 2 seconds
envelope_decay_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.499 # 0 to about 2 seconds
envelope_sustain_values = np.linspace(0, 1, 128)
envelope_release_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.499 # 0 to about 2 seconds
delay_time_values = 0.5 * np.logspace(0, 2.3, 128, endpoint=True, base=2, dtype=np.float32) - 0.5 # 0 to about 2 seconds
delay_feedback_values = (np.logspace(0, 1, 128, endpoint=True, base=10) - 1) / 9 # 0 to 1
delay_wet_values = np.linspace(0, 1, 128)