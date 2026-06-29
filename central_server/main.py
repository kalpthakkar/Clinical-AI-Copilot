import numpy as np

from fastapi import FastAPI, WebSocket

from central_server.asr.whisper_engine import WhisperEngine
from central_server.models.transcript_event import TranscriptEvent
from central_server.monitoring.logger import (
    log_asr_event,
    log_structured_output
)
from central_server.audio.speech_segmenter import SpeechSegmenter
from central_server.pipeline.transcription_pipeline import TranscriptionPipeline
from central_server.cognition.cognitive_processor import CognitiveProcessor

app = FastAPI()

# -------------------------
# Core Components
# -------------------------
asr_engine = WhisperEngine()
pipeline = TranscriptionPipeline()
cognitive_processor = CognitiveProcessor()

segmenters = {}
audio_clocks = {}


@app.websocket("/stream/{speaker}")
async def audio_stream(websocket: WebSocket, speaker: str):

    await websocket.accept()

    print(f"Connected stream from {speaker}")

    # Create per-speaker state
    segmenters[speaker] = SpeechSegmenter()
    audio_clocks[speaker] = 0.0

    try:
        while True:

            # -------------------------
            # Receive audio chunk
            # -------------------------
            data = await websocket.receive_bytes()
            audio = np.frombuffer(data, dtype=np.float32).copy()

            # -------------------------
            # Track timeline (IMPORTANT)
            # -------------------------
            duration = len(audio) / 16000
            audio_clocks[speaker] += duration

            # -------------------------
            # VAD Segmentation
            # -------------------------
            segment = segmenters[speaker].process(audio)

            if segment is None:
                continue  # wait until full utterance

            # -------------------------
            # ASR on COMPLETE utterance
            # -------------------------
            result = asr_engine.transcribe(segment)

            text = result["text"].strip()

            if not text:
                continue

            # -------------------------
            # Time Alignment
            # -------------------------
            segment_duration = len(segment) / 16000

            end_time = audio_clocks[speaker]
            start_time = end_time - segment_duration

            # -------------------------
            # Create Event
            # -------------------------
            event = TranscriptEvent(
                speaker=speaker,
                transcript=text,

                timestamp_start=start_time,
                timestamp_end=end_time,

                latency=result["latency"],
                audio_duration=segment_duration,
                rtf=result["rtf"],

                language=result["language"],
                language_confidence=result["language_probability"],

                model=result["model"]
            )

            # -------------------------
            # LOG ASR
            # -------------------------
            log_asr_event(event)

            # -------------------------
            # COGNITIVE PROCESSOR
            # -------------------------
            cognitive_processor.on_new_event(event)

            # -------------------------
            # 🔥 PIPELINE EXECUTION
            # -------------------------
            bundle = pipeline.process_event(event)

            # -------------------------
            # LOG STRUCTURED OUTPUT
            # -------------------------
            log_structured_output(bundle)

    except Exception as e:
        print("Stream closed:", e)

    finally:
        print(f"Disconnected {speaker}")
        segmenters.pop(speaker, None)
        audio_clocks.pop(speaker, None)