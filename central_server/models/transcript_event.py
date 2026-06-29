from pydantic import BaseModel
from datetime import datetime


class TranscriptEvent(BaseModel):

    speaker: str
    transcript: str

    timestamp_start: datetime
    timestamp_end: datetime

    latency: float
    audio_duration: float
    rtf: float

    language: str
    language_confidence: float

    model: str