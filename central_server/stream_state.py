from collections import deque
import numpy as np


class StreamState:

    def __init__(self, sample_rate=16000, buffer_seconds=8):

        self.sample_rate = sample_rate
        self.buffer_samples = sample_rate * buffer_seconds

        self.buffer = deque(maxlen=self.buffer_samples)

        self.audio_offset = 0.0
        self.previous_text = ""

    def update_buffer(self, audio):

        self.buffer.extend(audio)

        self.audio_offset += len(audio) / self.sample_rate

    def get_buffer_audio(self):

        return np.array(self.buffer, dtype=np.float32)