import os
import json
import time
import random

import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.source_model import Source


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

def get_config_value(key: str, default=None):

    # First try environment variable
    value = os.getenv(key)

    if value:
        return value

    # Then try Streamlit Secrets
    try:

        value = st.secrets.get(key)

        if value:
            return value

    except Exception:

        pass

    return default


GEMINI_API_KEY = get_config_value(
    "GEMINI_API_KEY"
)

# Also support GOOGLE_API_KEY
# if that is the name used in Streamlit Secrets.
if not GEMINI_API_KEY:

    GEMINI_API_KEY = get_config_value(
        "GOOGLE_API_KEY"
    )


GEMINI_MODEL = get_config_value(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


MAX_RETRIES = int(
    get_config_value(
        "GEMINI_MAX_RETRIES",
        "5"
    )
)


INITIAL_BACKOFF = float(
    get_config_value(
        "GEMINI_INITIAL_BACKOFF",
        "2"
    )
)


MAX_BACKOFF = float(
    get_config_value(
        "GEMINI_MAX_BACKOFF",
        "30"
    )
)


if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY or GOOGLE_API_KEY "
        "not found. Add it to .env locally or "
        "Streamlit Cloud → Manage app → Settings → Secrets."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# SAFE GEMINI CALL
# ============================================================

def call_gemini(
    prompt: str,
    temperature: float = 0.2
) -> str:

    last_error = None

    for attempt in range(
        MAX_RETRIES + 1
    ):

        try:

            response = client.models.generate_content(

                model=GEMINI_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(
                    temperature=temperature
                )
            )

            if not response.text:

                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as e:

            last_error = e

            error_text = str(e).lower()

            # ------------------------------------------------
            # Retry only temporary/rate-limit/server failures
            # ------------------------------------------------

            retryable = any(
                value in error_text
                for value in [
                    "429",
                    "rate limit",
                    "resource exhausted",
                    "503",
                    "unavailable",
                    "500",
                    "internal",
                    "timeout",
                    "deadline"
                ]
            )

            if not retryable:

                raise

            if attempt >= MAX_RETRIES:

                print()
                print(
                    "Gemini failed after "
                    f"{MAX_RETRIES} retries."
                )

                raise last_error

            # ------------------------------------------------
            # Exponential backoff + jitter
            # ------------------------------------------------

            delay = min(
                INITIAL_BACKOFF * (2 ** attempt),
                MAX_BACKOFF
            )

            jitter = random.uniform(
                0,
                1.5
            )

            delay += jitter

            print()
            print(
                f"Gemini temporary error: {e}"
            )

            print(
                f"Retrying in {delay:.1f} seconds..."
            )

            time.sleep(delay)

    raise last_error


# ============================================================
# CHUNK SUMMARY
# ============================================================

def summarize_chunk(
    text: str,
    chunk_number: int
) -> str:

    prompt = f"""
You are a professional video summarization assistant.

You are given CHUNK {chunk_number} of a video's transcript.

Your job is to summarize ONLY what is actually said in this
transcript chunk.

Do NOT introduce information from your own knowledge.

Do NOT change the topic.

Do NOT assume that the video is explaining something that is
not present in the transcript.

Preserve:

- the main topic
- important explanations
- definitions
- examples
- comparisons
- arguments
- conclusions
- important terminology

Remove:

- filler words
- repeated phrases
- greetings
- unnecessary conversational language

Write a concise but information-rich summary.

IMPORTANT:
This is only one part of a larger transcript, so do not invent
a conclusion if this chunk does not contain one.

Transcript chunk:

--------------------
{text}
--------------------

Return only the summary.
"""

    return call_gemini(
        prompt=prompt,
        temperature=0.15
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

def generate_final_summary(
    source: Source,
    chunk_summaries: list
) -> str:

    combined = "\n\n".join(

        f"""
CHUNK {item['chunk_id'] + 1}

{item['summary']}
"""
        for item in chunk_summaries
        if item.get("summary")
    )

    prompt = f"""
You are creating the FINAL SUMMARY of a video.

Video title:

{source.source_name}

Below are summaries generated from different sequential
sections of the video's transcript.

Your job is to combine them into ONE accurate, coherent,
complete summary of the ENTIRE VIDEO.

IMPORTANT RULES:

1. Stay strictly grounded in the provided chunk summaries.

2. Do NOT introduce outside information.

3. Do NOT change the video's topic.

4. Follow the actual flow of the video.

5. Explain what the speaker actually discusses.

6. If the video compares two concepts, explain the comparison
   clearly.

7. Preserve important definitions and examples.

8. Remove duplicated information between chunks.

9. Do not write generic textbook information that was not
   discussed in the video.

10. Do not start with:
   "This video discusses..."

11. Do not say:
   "Machine learning is a subset of AI..."
   unless that idea is actually supported by the supplied
   content.

12. The final summary should read like a person watched the
   complete video and is explaining what the video actually
   said.

13. Use clear paragraphs.

14. Use bullet points only when they improve readability.

15. Make the final summary detailed enough that someone who
   did not watch the video can understand the video's actual
   message.

VIDEO:

{source.source_name}

CHUNK SUMMARIES:

==============================
{combined}
==============================

Now write the final video summary.
"""

    return call_gemini(
        prompt=prompt,
        temperature=0.15
    )


# ============================================================
# CREATE SUMMARY
# ============================================================

def create_summary(
    source: Source,
    chunk_result: dict
) -> dict:

    chunks = chunk_result.get(
        "chunks",
        []
    )

    if not chunks:

        raise ValueError(
            "No text chunks available for summarization."
        )

    summary_dir = os.path.join(
        "storage",
        "sessions",
        source.source_id,
        "summary"
    )

    os.makedirs(
        summary_dir,
        exist_ok=True
    )

    chunk_summary_dir = os.path.join(
        summary_dir,
        "chunk_summaries"
    )

    os.makedirs(
        chunk_summary_dir,
        exist_ok=True
    )

    print()
    print("=" * 60)
    print("AI SUMMARY GENERATION")
    print("=" * 60)

    print(
        f"Source: {source.source_name}"
    )

    print(
        f"Model: {GEMINI_MODEL}"
    )

    print(
        f"Text chunks: {len(chunks)}"
    )

    chunk_summaries = []

    # ========================================================
    # SUMMARIZE EACH TEXT CHUNK
    # ========================================================

    for index, chunk in enumerate(chunks):

        chunk_id = chunk.get(
            "chunk_id",
            index
        )

        text = chunk.get(
            "text",
            ""
        ).strip()

        if not text:

            print(
                f"Skipping empty chunk "
                f"{index + 1}."
            )

            continue

        print()
        print(
            f"Summarizing chunk "
            f"{index + 1}/{len(chunks)}..."
        )

        try:

            summary = summarize_chunk(
                text=text,
                chunk_number=index + 1
            )

            chunk_summary = {
                "chunk_id": chunk_id,
                "summary": summary
            }

            chunk_summaries.append(
                chunk_summary
            )

            # -----------------------------------------------
            # Save individual chunk summary
            # -----------------------------------------------

            chunk_summary_file = os.path.join(
                chunk_summary_dir,
                f"summary_{index:03d}.txt"
            )

            with open(
                chunk_summary_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(summary)

            print(
                f"Chunk {index + 1} completed."
            )

        except Exception as e:

            print(
                f"Chunk {index + 1} failed: {e}"
            )

            # Do not silently continue with an empty summary.
            raise

    if not chunk_summaries:

        raise ValueError(
            "No chunk summaries were generated."
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("GENERATING FINAL VIDEO SUMMARY")
    print("=" * 60)

    final_summary = generate_final_summary(
        source=source,
        chunk_summaries=chunk_summaries
    )

    # ========================================================
    # SAVE FINAL SUMMARY
    # ========================================================

    final_summary_path = os.path.join(
        summary_dir,
        "final_summary.txt"
    )

    with open(
        final_summary_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(final_summary)

    # ========================================================
    # SAVE JSON
    # ========================================================

    result = {

        "source_id":
            source.source_id,

        "source_name":
            source.source_name,

        "model":
            GEMINI_MODEL,

        "chunk_count":
            len(chunk_summaries),

        "chunk_summaries":
            chunk_summaries,

        "final_summary":
            final_summary,

        "summary_path":
            final_summary_path
    }

    json_path = os.path.join(
        summary_dir,
        "summary.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 60)
    print("SUMMARY COMPLETED")
    print("=" * 60)

    print()
    print("FINAL SUMMARY")
    print("-" * 60)

    print(final_summary)

    print()
    print("Summary saved to:")
    print(final_summary_path)

    print()
    print("JSON saved to:")
    print(json_path)

    return result