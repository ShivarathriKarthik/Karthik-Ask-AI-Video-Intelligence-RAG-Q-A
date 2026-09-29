import os
import json

from dotenv import load_dotenv
from sarvamai import SarvamAI

from tools.source_model import Source


load_dotenv()


SARVAM_API_KEY = os.getenv(
    "SARVAM_API_KEY"
)

SARVAM_STT_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v3"
)

SARVAM_STT_MODE = os.getenv(
    "SARVAM_STT_MODE",
    "transcribe"
)


LANGUAGE_CODES = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "telugu": "te-IN",

    "en": "en-IN",
    "hi": "hi-IN",
    "te": "te-IN"
}


def transcribe_audio_chunks(
    source: Source,
    audio_chunks: list,
    language: str = "english"
) -> dict:

    if not SARVAM_API_KEY:

        raise ValueError(
            "SARVAM_API_KEY not found in .env"
        )

    language = language.lower()

    if language not in LANGUAGE_CODES:

        raise ValueError(
            "Supported languages: "
            "english, hindi, telugu"
        )

    language_code = LANGUAGE_CODES[
        language
    ]

    client = SarvamAI(
        api_subscription_key=SARVAM_API_KEY
    )

    transcript_dir = os.path.join(
        "storage",
        "sessions",
        source.source_id,
        "transcript"
    )

    os.makedirs(
        transcript_dir,
        exist_ok=True
    )

    transcripts = []

    print()
    print("=" * 60)
    print("SARVAM AI TRANSCRIPTION")
    print("=" * 60)

    print(
        f"Source: {source.source_name}"
    )

    print(
        f"Language: {language}"
    )

    print(
        f"Model: {SARVAM_STT_MODEL}"
    )

    print(
        f"Chunks: {len(audio_chunks)}"
    )

    for index, chunk_path in enumerate(
        audio_chunks
    ):

        print()
        print(
            f"Transcribing chunk "
            f"{index + 1}/{len(audio_chunks)}..."
        )

        try:

            with open(
                chunk_path,
                "rb"
            ) as audio_file:

                response = (
                    client.speech_to_text.transcribe(
                        file=audio_file,
                        model=SARVAM_STT_MODEL,
                        mode=SARVAM_STT_MODE,
                        language_code=language_code
                    )
                )

            text = getattr(
                response,
                "transcript",
                ""
            )

            if not text:

                if isinstance(
                    response,
                    dict
                ):

                    text = response.get(
                        "transcript",
                        ""
                    )

            text = text.strip()

        except Exception as e:

            print(
                f"Chunk {index + 1} failed: {e}"
            )

            text = ""

        transcript_file = os.path.join(
            transcript_dir,
            f"transcript_{index:03d}.txt"
        )

        with open(
            transcript_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        transcripts.append(
            {
                "chunk_id": index,
                "audio_path": chunk_path,
                "transcript_path": transcript_file,
                "text": text
            }
        )

        print(
            f"Chunk {index + 1} completed."
        )

    full_transcript = "\n\n".join(
        item["text"]
        for item in transcripts
        if item["text"]
    )

    full_transcript_path = os.path.join(
        transcript_dir,
        "full_transcript.txt"
    )

    with open(
        full_transcript_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(full_transcript)

    result = {
        "source_id": source.source_id,
        "source_name": source.source_name,
        "language": language,
        "language_code": language_code,
        "model": SARVAM_STT_MODEL,
        "transcript": full_transcript,
        "chunks": transcripts,
        "transcript_path": full_transcript_path
    }

    json_output = os.path.join(
        transcript_dir,
        "transcription.json"
    )

    with open(
        json_output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print("=" * 60)
    print("TRANSCRIPTION COMPLETED")
    print("=" * 60)

    print(
        f"Transcript saved to:"
    )

    print(
        full_transcript_path
    )

    return result