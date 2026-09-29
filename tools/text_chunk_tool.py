import os
import json
import re

from tools.source_model import Source


# ============================================================
# CONFIGURATION
# ============================================================

# Approximate characters per LLM chunk.
#
# We deliberately don't make this huge because:
# 1. Some transcripts can be very large.
# 2. We want enough context for meaningful summaries.
# 3. We want to reduce the chance of hitting rate/token limits.
#
# 12,000 characters is roughly a few thousand tokens depending
# on the language and transcript.
CHUNK_SIZE = 12000

# Keep some overlap so that a sentence/topic near a boundary
# isn't completely separated from the next chunk.
OVERLAP_SIZE = 500


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:

    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Normalize excessive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# SMART CHUNKING
# ============================================================

def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = OVERLAP_SIZE
) -> list:

    text = clean_text(text)

    if not text:
        return []

    if chunk_size <= overlap:
        raise ValueError(
            "chunk_size must be greater than overlap."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        # If this is not the final chunk,
        # try to end at a natural boundary.
        if end < text_length:

            # Look for paragraph boundary
            paragraph_boundary = text.rfind(
                "\n\n",
                start,
                end
            )

            # Look for sentence boundary
            sentence_boundary = max(
                text.rfind(
                    ". ",
                    start,
                    end
                ),
                text.rfind(
                    "? ",
                    start,
                    end
                ),
                text.rfind(
                    "! ",
                    start,
                    end
                )
            )

            # Prefer paragraph boundary
            if paragraph_boundary > start + int(
                chunk_size * 0.6
            ):

                end = paragraph_boundary + 2

            elif sentence_boundary > start + int(
                chunk_size * 0.6
            ):

                end = sentence_boundary + 1

        chunk_text = text[
            start:end
        ].strip()

        if chunk_text:

            chunks.append(
                chunk_text
            )

        # Move backwards slightly for overlap
        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


# ============================================================
# CREATE TEXT CHUNKS
# ============================================================

def create_text_chunks(
    source: Source,
    transcript: str
) -> dict:

    if not transcript:
        raise ValueError(
            "Transcript is empty."
        )

    text_chunks = split_text(
        transcript
    )

    if not text_chunks:
        raise ValueError(
            "Unable to create text chunks."
        )

    chunk_dir = os.path.join(
        "storage",
        "sessions",
        source.source_id,
        "text_chunks"
    )

    os.makedirs(
        chunk_dir,
        exist_ok=True
    )

    chunks = []

    print()
    print("=" * 60)
    print("TEXT CHUNKING")
    print("=" * 60)

    print(
        f"Chunk size: {CHUNK_SIZE} characters"
    )

    print(
        f"Overlap: {OVERLAP_SIZE} characters"
    )

    print(
        f"Created {len(text_chunks)} text chunks."
    )

    for index, chunk_text in enumerate(
        text_chunks
    ):

        chunk_file = os.path.join(
            chunk_dir,
            f"chunk_{index:03d}.txt"
        )

        with open(
            chunk_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(chunk_text)

        chunk_data = {
            "chunk_id": index,
            "chunk_number": index + 1,
            "text": chunk_text,
            "text_length": len(chunk_text),
            "file_path": chunk_file
        }

        chunks.append(
            chunk_data
        )

        print(
            f"Chunk {index + 1}: "
            f"{len(chunk_text)} characters"
        )

    # Save metadata
    metadata_path = os.path.join(
        chunk_dir,
        "chunks.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "source_id": source.source_id,
                "source_name": source.source_name,
                "chunk_size": CHUNK_SIZE,
                "overlap": OVERLAP_SIZE,
                "total_chunks": len(chunks),
                "chunks": chunks
            },
            f,
            ensure_ascii=False,
            indent=4
        )

    return {
        "source_id": source.source_id,
        "source_name": source.source_name,
        "total_chunks": len(chunks),
        "chunks": chunks,
        "chunks_path": metadata_path
    }