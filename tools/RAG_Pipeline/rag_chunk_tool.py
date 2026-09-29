import os
import json
import re

from tools.source_model import Source


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def clean_text(text: str) -> str:

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def create_rag_chunks(
    source: Source,
    transcript: str
) -> dict:

    transcript = clean_text(
        transcript
    )

    if not transcript:

        raise ValueError(
            "Transcript is empty."
        )

    chunks = []

    start = 0
    chunk_id = 0

    while start < len(transcript):

        end = start + CHUNK_SIZE

        chunk_text = transcript[
            start:end
        ]

        # Try to finish at a sentence boundary
        if end < len(transcript):

            last_period = max(
                chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!")
            )

            if last_period > CHUNK_SIZE * 0.6:

                chunk_text = chunk_text[
                    :last_period + 1
                ]

                end = start + len(
                    chunk_text
                )

        chunk_text = chunk_text.strip()

        if chunk_text:

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end
                }
            )

            chunk_id += 1

        next_start = end - CHUNK_OVERLAP

        if next_start <= start:

            next_start = end

        start = next_start

    chunk_dir = os.path.join(
        "storage",
        "sessions",
        source.source_id,
        "rag_chunks"
    )

    os.makedirs(
        chunk_dir,
        exist_ok=True
    )

    for chunk in chunks:

        path = os.path.join(
            chunk_dir,
            f"chunk_{chunk['chunk_id']:04d}.txt"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(chunk["text"])

        chunk["path"] = path

    output = {
        "source_id": source.source_id,
        "source_name": source.source_name,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "chunks": chunks
    }

    json_path = os.path.join(
        chunk_dir,
        "chunks.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print("=" * 60)
    print("RAG TEXT CHUNKING")
    print("=" * 60)

    print(
        f"Created {len(chunks)} RAG chunks."
    )

    return output