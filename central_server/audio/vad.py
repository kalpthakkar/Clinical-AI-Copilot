import torch
from silero_vad import load_silero_vad, get_speech_timestamps


class VoiceActivityDetector:

    def __init__(self, sample_rate=16000):

        self.sample_rate = sample_rate

        self.model = load_silero_vad()

    def has_speech(self, audio):

        audio_tensor = torch.from_numpy(audio)

        timestamps = get_speech_timestamps(
            audio_tensor,
            self.model,
            sampling_rate=self.sample_rate
        )

        # return len(timestamps) > 0
        return any((ts["end"] - ts["start"]) > 0.3 for ts in timestamps)