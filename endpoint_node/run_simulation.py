import asyncio
from pathlib import Path

from endpoint_node.stream_client import stream_audio_file


BASE_DIR = Path(__file__).resolve().parent.parent

DOCTOR_FILE = BASE_DIR / "assets" / "conversations" / "1" / "doctor.wav"
PATIENT_FILE = BASE_DIR / "assets" / "conversations" / "1" / "patient.wav"


async def main():

    print("Starting doctor + patient simulation")

    doctor_task = asyncio.create_task(
        stream_audio_file("doctor", DOCTOR_FILE)
    )

    patient_task = asyncio.create_task(
        stream_audio_file("patient", PATIENT_FILE)
    )

    await asyncio.gather(
        doctor_task,
        patient_task
    )


if __name__ == "__main__":

    asyncio.run(main())