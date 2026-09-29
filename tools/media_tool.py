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

    # =========================================================
    # YOUTUBE URL
    # =========================================================

    if input_source.startswith(
        (
            "https://www.youtube.com/",
            "https://youtu.be/",
            "https://m.youtube.com/"
        )
    ):

        output_template = os.path.join(
            audio_dir,
            "youtube.%(ext)s"
        )

        ydl_opts = {

            # -------------------------------------------------
            # AUDIO FORMAT
            # -------------------------------------------------

            "format": (
                "bestaudio[ext=m4a]/"
                "bestaudio[ext=webm]/"
                "bestaudio/best"
            ),

            "outtmpl": output_template,

            "noplaylist": True,

            # -------------------------------------------------
            # YOUTUBE REQUEST SETTINGS
            # -------------------------------------------------

            "quiet": False,

            "no_warnings": False,

            "retries": 5,

            "fragment_retries": 5,

            "file_access_retries": 3,

            "extractor_retries": 3,

            "socket_timeout": 30,

            # -------------------------------------------------
            # IMPORTANT
            # Use a browser-like User-Agent
            # -------------------------------------------------

            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0.0.0 "
                    "Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },

            # -------------------------------------------------
            # EJS / JAVASCRIPT RUNTIME
            #
            # Deno must be installed in Streamlit Cloud.
            # -------------------------------------------------

            "js_runtimes": {
                "deno": {}
            },

            # -------------------------------------------------
            # POST PROCESSING
            # -------------------------------------------------

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192"
                }
            ],

            # -------------------------------------------------
            # KEEP TEMPORARY FILES CLEAN
            # -------------------------------------------------

            "keepvideo": False,

            "overwrites": True,
        }

        try:

            print()
            print("=" * 60)
            print("YOUTUBE AUDIO EXTRACTION")
            print("=" * 60)

            print(
                f"URL: {input_source}"
            )

            print(
                "Using yt-dlp + EJS/Deno..."
            )

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

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

            # -------------------------------------------------
            # VERIFY FILE
            # -------------------------------------------------

            if not os.path.exists(
                wav_path
            ):

                raise FileNotFoundError(
                    "YouTube audio was downloaded "
                    "but WAV conversion failed. "
                    "Make sure FFmpeg is installed."
                )

            print()
            print(
                "Audio extraction completed."
            )

            print(
                f"Audio: {wav_path}"
            )

            return Source(
                source_id=source_id,
                source_name=title,
                audio_path=wav_path,
                source_type="youtube"
            )

        except yt_dlp.utils.DownloadError as e:

            error_message = str(e)

            print()
            print(
                "YouTube download failed:"
            )

            print(error_message)

            if (
                "403" in error_message
                or "Forbidden" in error_message
            ):

                raise RuntimeError(
                    "YouTube returned HTTP 403 Forbidden. "
                    "This usually means YouTube rejected "
                    "the selected media request. "
                    "Make sure yt-dlp, Deno/EJS dependencies "
                    "and FFmpeg are installed and updated."
                ) from e

            raise RuntimeError(
                f"YouTube download failed: "
                f"{error_message}"
            ) from e

        except Exception as e:

            raise RuntimeError(
                f"Audio extraction failed: {e}"
            ) from e

    # =========================================================
    # LOCAL AUDIO / VIDEO FILE
    # =========================================================

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

        try:

            subprocess.run(
                command,
                check=True
            )

        except FileNotFoundError as e:

            raise RuntimeError(
                "FFmpeg was not found. "
                "Install FFmpeg and make sure it is "
                "available in PATH."
            ) from e

        if not os.path.exists(
            output_path
        ):

            raise RuntimeError(
                "FFmpeg did not create the WAV file."
            )

        return Source(
            source_id=source_id,
            source_name=source_name,
            audio_path=output_path,
            source_type="file"
        )

    # =========================================================
    # INVALID INPUT
    # =========================================================

    raise ValueError(
        "Invalid YouTube URL or file path."
    )
