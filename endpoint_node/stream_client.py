import asyncio
import websockets
import numpy as np
import librosa

from endpoint_node.audio_streamer import AudioStreamer

SERVER = "ws://localhost:8000/stream"


async def stream_microphone(speaker):

    streamer = AudioStreamer()

    streamer.start()

    uri = f"{SERVER}/{speaker}"

    async with websockets.connect(uri) as ws:

        while True:

            audio = streamer.get_chunk()

            await ws.send(audio.tobytes())


async def stream_audio_file(speaker, file_path):

    SERVER = "ws://localhost:8000/stream"

    audio, sr = librosa.load(str(file_path), sr=16000)

    chunk_size = 32000
    chunk_duration = chunk_size / sr

    uri = f"{SERVER}/{speaker}"

    async with websockets.connect(uri) as ws:

        print(f"{speaker} connected")

        for i in range(0, len(audio), chunk_size):

            chunk = audio[i:i + chunk_size]

            await ws.send(chunk.astype(np.float32).tobytes())

            await asyncio.sleep(chunk_duration)


if __name__ == "__main__":

    mode = "file"

    speaker = "doctor"

    if mode == "mic":

        asyncio.run(stream_microphone(speaker))

    else:

        asyncio.run(
            stream_audio_file(
                speaker,
                "assets/conversations/1/doctor.wav"
            )
        )