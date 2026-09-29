import shutil
import yt_dlp


URL = "YOUR_YOUTUBE_URL"


print("=" * 60)
print("SYSTEM CHECK")
print("=" * 60)

print(
    "FFmpeg:",
    shutil.which("ffmpeg")
)

print(
    "Deno:",
    shutil.which("deno")
)

print(
    "yt-dlp:",
    shutil.which("yt-dlp")
)

print(
    "yt-dlp Python version:",
    yt_dlp.version.__version__
)


print()
print("=" * 60)
print("YOUTUBE TEST")
print("=" * 60)


ydl_opts = {

    "format": "bestaudio/best",

    "noplaylist": True,

    "quiet": False,

    "verbose": True,

    "retries": 2,

    "fragment_retries": 2,

    "extractor_retries": 2,
}


deno = shutil.which("deno")

if deno:

    print(
        "Using Deno:",
        deno
    )

    ydl_opts["js_runtimes"] = {
        "deno": {
            "path": deno
        }
    }

    ydl_opts["remote_components"] = {
        "ejs:github"
    }

else:

    print(
        "WARNING: Deno not found."
    )


try:

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            URL,
            download=False
        )

        print()
        print(
            "TITLE:",
            info.get("title")
        )

        print(
            "ID:",
            info.get("id")
        )

        print(
            "EXTRACTED SUCCESSFULLY"
        )

except Exception as e:

    print()
    print(
        "YOUTUBE TEST FAILED"
    )

    print(
        repr(e)
    )
