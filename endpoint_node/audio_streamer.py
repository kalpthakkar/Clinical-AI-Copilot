import sounddevice as sd
import numpy as np
import queue


class AudioStreamer:

    def __init__(self, sample_rate=16000, chunk_duration=2):

        self.sample_rate = sample_rate
        self.chunk_samples = int(sample_rate * chunk_duration)

        self.q = queue.Queue()

    def callback(self, indata, frames, time_info, status):

        if status:
            print(status)

        self.q.put(indata.copy())

    def start(self):

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self.callback
        )

        self.stream.start()

    def get_chunk(self):

        frames = []

        while len(frames) < self.chunk_samples:

            data = self.q.get()
            frames.extend(data.flatten())

        return np.array(frames[:self.chunk_samples], dtype=np.float32)