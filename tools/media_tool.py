import os
import uuid
import subprocess
import yt_dlp

from tools.source_model import Source


def get_audio_source(input_source: str) -> Source:

    source_id = uuid.uuid4().hex

    session_dir = os.path.join(
        "storage",
        "sessions",
        source_id
    )

    audio_dir = os.path.join(
        session_dir,
        "audio"
    )

    os.makedirs(
        audio_dir,
        exist_ok=True
    )

    # ========================================================
    # YOUTUBE URL HANDLING
    # ========================================================
    if input_source.startswith(
        (
            "https://www.youtube.com/",
            "https://youtu.be/"
        )
    ):

        output_template = os.path.join(
            audio_dir,
            "youtube.%(ext)s"
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192"
                }
            ],
            "quiet": False,
            
            # --- NEW: ANTI-BOT BYPASS FOR STREAMLIT CLOUD ---
            # These arguments force YouTube to treat the request 
            # like an Android mobile device, bypassing web bot checks.
            "extractor_args": {
                "youtube": [
                    "player_client=android",
                    "player_skip=web"
                ]
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            # ------------------------------------------------
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                input_source,
                download=True
            )

            title = info.get(
                "title",
                "YouTube Audio"
            )

        wav_path = os.path.join(
            audio_dir,
            "youtube.wav"
        )

        return Source(
            source_id=source_id,
            source_name=title,
            audio_path=wav_path,
            source_type="youtube"
        )

    # ========================================================
    # LOCAL FILE HANDLING
    # ========================================================
    if os.path.isfile(input_source):

        source_name = os.path.splitext(
            os.path.basename(input_source)
        )[0]

        output_path = os.path.join(
            audio_dir,
            "input.wav"
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            input_source,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            output_path
        ]

        subprocess.run(
            command,
            check=True
        )

        return Source(
            source_id=source_id,
            source_name=source_name,
            audio_path=output_path,
            source_type="file"
        )

    raise ValueError(
        "Invalid YouTube URL or file path."
    )
