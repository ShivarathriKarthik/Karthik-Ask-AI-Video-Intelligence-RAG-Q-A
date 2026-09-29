import os
import subprocess


CHUNK_SECONDS = 30


def split_audio(
    audio_path: str,
    source_id: str
) -> list:

    output_dir = os.path.join(
        "storage",
        "sessions",
        source_id,
        "audio_chunks"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_pattern = os.path.join(
        output_dir,
        "chunk_%03d.wav"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        audio_path,

        "-f",
        "segment",

        "-segment_time",
        str(CHUNK_SECONDS),

        "-reset_timestamps",
        "1",

        "-ac",
        "1",

        "-ar",
        "16000",

        "-sample_fmt",
        "s16",

        output_pattern
    ]

    subprocess.run(
        command,
        check=True
    )

    chunks = []

    for filename in sorted(
        os.listdir(output_dir)
    ):

        if filename.endswith(".wav"):

            chunks.append(
                os.path.join(
                    output_dir,
                    filename
                )
            )

    return chunks