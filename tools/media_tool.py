import os
import uuid
import shutil
import subprocess

import yt_dlp

try:
    import deno
except ImportError:
    deno = None

from tools.source_model import Source


# ============================================================
# HELPERS
# ============================================================

def find_executable(name: str):
    """
    Find an executable available on the system.
    """

    path = shutil.which(name)

    if path:
        return path

    return None


def get_ffmpeg_location():
    """
    Find FFmpeg installation.

    Streamlit Cloud:
        FFmpeg should be installed through packages.txt.

    Local Windows:
        FFmpeg should be available in PATH.
    """

    ffmpeg = find_executable("ffmpeg")

    if ffmpeg:
        return os.path.dirname(ffmpeg)

    return None


def get_deno_location():
    """
    Find Deno.

    Deno is used by yt-dlp for YouTube EJS support.
    """

    deno = find_executable("deno")

    if deno:
        return deno

    return None


def is_youtube_url(url: str) -> bool:

    return url.startswith(
        (
            "https://www.youtube.com/",
            "https://youtube.com/",
            "https://youtu.be/",
            "https://www.youtube-nocookie.com/"
        )
    )


# ============================================================
# YOUTUBE AUDIO
# ============================================================

def download_youtube_audio(
    input_source: str,
    audio_dir: str
):

    output_template = os.path.join(
        audio_dir,
        "youtube.%(ext)s"
    )

    ffmpeg_location = get_ffmpeg_location()
    deno_location = get_deno_location()

    # --------------------------------------------------------
    # Check FFmpeg
    # --------------------------------------------------------

    if not ffmpeg_location:

        raise RuntimeError(
            "FFmpeg was not found on the server. "
            "Install FFmpeg and make sure it is available "
            "in PATH."
        )

    # --------------------------------------------------------
    # Base yt-dlp configuration
    # --------------------------------------------------------

    ydl_opts = {

        # Try several audio-capable formats.
        "format": (
            "bestaudio/best/"
            "bestvideo+bestaudio/"
            "best"
        ),

        "outtmpl": output_template,

        "noplaylist": True,

        "quiet": False,

        "no_warnings": False,

        "extractor_retries": 3,

        "fragment_retries": 3,

        "retries": 3,

        "file_access_retries": 3,

        "continuedl": True,

        # ----------------------------------------------------
        # Browser-like headers
        # ----------------------------------------------------

        "http_headers": {

            "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 "
                "Safari/537.36",

            "Accept-Language":
                "en-US,en;q=0.9"
        },

        # ----------------------------------------------------
        # Convert downloaded media to WAV
        # ----------------------------------------------------

        "postprocessors": [

            {
                "key": "FFmpegExtractAudio",

                "preferredcodec": "wav",

                "preferredquality": "192"
            }
        ],

        "prefer_ffmpeg": True,

        "ffmpeg_location": ffmpeg_location
    }

    # --------------------------------------------------------
    # Deno / EJS
    # --------------------------------------------------------

    if deno_location:

        print()
        print(
            "Deno detected:"
        )

        print(
            deno_location
        )

        ydl_opts[
            "js_runtimes"
        ] = {
            "deno": {
                "path": deno_location
            }
        }

        # Allow yt-dlp to use the EJS challenge solver.
        ydl_opts[
            "remote_components"
        ] = {
            "ejs:github"
        }

    else:

        print()
        print(
            "WARNING: Deno was not found."
        )

        print(
            "YouTube EJS support may be limited."
        )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    print()
    print(
        "Starting YouTube download..."
    )

    print()
    print(
        "FFmpeg:"
    )

    print(
        ffmpeg_location
    )

    print()
    print(
        "Deno:"
    )

    print(
        deno_location
        if deno_location
        else "Not found"
    )

    print()

    try:

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

    except yt_dlp.utils.DownloadError as e:

        error_message = str(e)

        if (
            "403" in error_message
            or "Forbidden" in error_message
        ):

            raise RuntimeError(
                "YouTube returned HTTP 403 Forbidden.\n\n"
                "The server was able to access the YouTube "
                "page, but YouTube rejected the media download.\n\n"
                "Make sure:\n"
                "1. yt-dlp is updated\n"
                "2. Deno is installed\n"
                "3. yt-dlp EJS components are available\n"
                "4. FFmpeg is installed\n"
                "5. The video is publicly accessible\n\n"
                f"Original error: {error_message}"
            ) from e

        raise

    # --------------------------------------------------------
    # Expected WAV
    # --------------------------------------------------------

    wav_path = os.path.join(
        audio_dir,
        "youtube.wav"
    )

    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    if not os.path.isfile(
        wav_path
    ):

        # Sometimes yt-dlp/FFmpeg can produce a different
        # filename. Search the directory.

        wav_files = [

            filename

            for filename in os.listdir(
                audio_dir
            )

            if filename.lower().endswith(
                ".wav"
            )
        ]

        if wav_files:

            wav_path = os.path.join(
                audio_dir,
                wav_files[0]
            )

        else:

            raise FileNotFoundError(
                "YouTube audio was downloaded, "
                "but the WAV file could not be found."
            )

    return title, wav_path


# ============================================================
# MAIN SOURCE FUNCTION
# ============================================================

def get_audio_source(
    input_source: str
) -> Source:

    # --------------------------------------------------------
    # Create unique session
    # --------------------------------------------------------

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
    # YOUTUBE URL
    # ========================================================

    if is_youtube_url(
        input_source
    ):

        title, wav_path = (
            download_youtube_audio(
                input_source=input_source,
                audio_dir=audio_dir
            )
        )

        return Source(

            source_id=source_id,

            source_name=title,

            audio_path=wav_path,

            source_type="youtube"
        )

    # ========================================================
    # LOCAL AUDIO / VIDEO FILE
    # ========================================================

    if os.path.isfile(
        input_source
    ):

        source_name = os.path.splitext(
            os.path.basename(
                input_source
            )
        )[0]

        output_path = os.path.join(
            audio_dir,
            "input.wav"
        )

        ffmpeg = find_executable(
            "ffmpeg"
        )

        if not ffmpeg:

            raise RuntimeError(
                "FFmpeg was not found. "
                "Please install FFmpeg."
            )

        command = [

            ffmpeg,

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

        if not os.path.isfile(
            output_path
        ):

            raise FileNotFoundError(
                "FFmpeg completed but the "
                "audio output file was not created."
            )

        return Source(

            source_id=source_id,

            source_name=source_name,

            audio_path=output_path,

            source_type="file"
        )

    # ========================================================
    # INVALID INPUT
    # ========================================================

    raise ValueError(
        "Invalid YouTube URL or file path."
    )
