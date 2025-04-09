import pyaudio
import logging

class StreamPlayer:
    def __init__(self, sample_rate: int, buffer_size: int, input_delegate, output_device):
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.input_delegate = input_delegate
        self.output_device = output_device
        self.pyaudio_interface = pyaudio.PyAudio()
        self._output_stream = None
    
    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value):
        try:
            int_value = int(value)
            if int_value > 0:
                self._sample_rate = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Couldn't set sample_rate with value {value}")

    @property
    def buffer_size(self):
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        try:
            int_value = int(value)
            if int_value > 0:
                self._buffer_size = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Couldn't set buffer_size with value {value}")

    @property
    def input_delegate(self):
        """
        This should be an iterator which returns the BYTES of an ndarray (aka calling tobytes() on it)
        of size <buffer_size>
        """
        return self._input_delegate

    @input_delegate.setter
    def input_delegate(self, value):
        try:
            _ = iter(value)
            self._input_delegate = value
        except ValueError:
            self.log.error(f"Couldn't set input delegate with value {value}")

    def play(self):
        """
        Start the output stream
        """
        if self._output_stream is None:
            try:
                self._output_stream = self.pyaudio_interface.open(format = pyaudio.paFloat32,
                                                              channels = 1,
                                                              rate = self.sample_rate,
                                                              output = True,
                                                              stream_callback = self.audio_callback,
                                                              output_device_index = self.output_device, # if headphones
                                                              frames_per_buffer = self.buffer_size)  
            except OSError:
                self.log.error(f"Output device {self.output_device} is invalid!")
                self._output_stream = self.pyaudio_interface.open(format = pyaudio.paFloat32,
                channels = 1,
                rate = self.sample_rate,
                output = True,
                stream_callback = self.audio_callback,
                output_device_index = None, # no headphones
                frames_per_buffer = self.buffer_size)  
        self._output_stream.start_stream()
        self.log.info(self.pyaudio_interface.get_default_output_device_info())
        # print(self.output_device)
    
    def stop(self):
        """
        Stop the output stream
        """
        if self._output_stream is None:
            return
        else:
            self._output_stream.stop_stream()
            self._output_stream.close()
            self.pyaudio_interface.terminate()
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        The audio callback is called by the pyaudio interface when it needs more data.
        """
        frames = next(self.input_delegate)
        return (frames, pyaudio.paContinue)
    
    def is_active(self):
        """
        Used to determine if the output stream is currently active.
        """
        if self._output_stream is None:
            return False
        return self._output_stream.is_active()

# stream_player = StreamPlayer(30, 30, 3)
# stream_player.sample_rate = "ij"
# print(stream_player.sample_rate)
