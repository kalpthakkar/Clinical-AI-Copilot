import numpy as np


class SpeechSegmenter:

    def __init__(self, sample_rate=16000):

        self.sample_rate = sample_rate

        self.silence_threshold = 0.01
        self.max_silence_seconds = 0.7

        self.buffer = []

        self.silence_time = 0
        self.in_speech = False

    def process(self, audio):

        rms = np.sqrt(np.mean(audio ** 2))

        duration = len(audio) / self.sample_rate

        if rms > self.silence_threshold:

            self.in_speech = True
            self.silence_time = 0

            self.buffer.append(audio)

            return None

        if self.in_speech:

            self.buffer.append(audio)

            self.silence_time += duration

            if self.silence_time > self.max_silence_seconds:

                segment = np.concatenate(self.buffer)

                self.buffer = []
                self.silence_time = 0
                self.in_speech = False

                return segment

        return None