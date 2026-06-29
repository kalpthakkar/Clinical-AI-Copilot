import time
from faster_whisper import WhisperModel


class WhisperEngine:

    def __init__(self, model_size="base"):

        print("Loading ASR model...")

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

        self.model_name = f"faster-whisper-{model_size}"

        print("ASR model ready")

    def transcribe(self, audio, sample_rate=16000):

        start = time.time()

        segments, info = self.model.transcribe(
            audio,
            language="en",
            beam_size=1,
            word_timestamps=True
        )

        text = " ".join([s.text for s in segments]).strip()

        latency = time.time() - start
        duration = len(audio) / sample_rate
        rtf = latency / duration

        return {
            "text": text,
            "latency": latency,
            "duration": duration,
            "rtf": rtf,
            "language": info.language,
            "language_probability": info.language_probability,
            "model": self.model_name
        }