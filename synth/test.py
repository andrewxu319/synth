import numpy as np

sample_rate = 20
buffer_size = 4

dry_signal = [1.0, 1.0, 1.0, 1.0]

attack = 1.0
decay = 0.4
sustain = 0.5
release = 0.3
wet = 1.0

attack_frames = round(attack * sample_rate)
decay_frames = round(decay * sample_rate)
release_frames = round(release * sample_rate)

ad_multiplier_array_length = 4 * sample_rate # fixed value so changing envelope mid note doesnt break things
# one_filler = np.full((ad_multiplier_array_length), 1.0)
ad_multiplier_array = np.concatenate((np.linspace(0, 1.0, num=attack_frames), np.linspace(1.0, sustain, num=decay_frames)))
ad_multiplier_array = np.pad(ad_multiplier_array, (0, ad_multiplier_array_length - len(ad_multiplier_array)), mode="constant", constant_values=sustain)

while True:
    wet_signal = dry_signal
    wet_signal *= ad_multiplier_array[:buffer_size]
    print(wet_signal)
    ad_multiplier_array = np.roll(ad_multiplier_array, -buffer_size)
    ad_multiplier_array[-buffer_size:] = sustain