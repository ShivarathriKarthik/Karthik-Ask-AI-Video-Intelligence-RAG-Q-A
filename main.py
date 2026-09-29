from tools.media_tool import get_audio_source
from tools.audio_chunk_tool import split_audio
from tools.transcription_tool import transcribe_audio_chunks
from tools.text_chunk_tool import create_text_chunks
from tools.summary_tool import create_summary
from tools.RAG_Pipeline.rag_chunk_tool import create_rag_chunks
from tools.RAG_Pipeline.vector_store_tool import store_chunks
from tools.RAG_Pipeline.rag_tool import answer_question

def print_separator():

    print()
    print("=" * 70)


def main():

    print_separator()

    print(
        "KARTHIK ASK PROJECT"
    )

    print("=" * 70)

    # =========================================================
    # 1. USER INPUT
    # =========================================================

    user_input = input(
        "your_youtube_url_or_file_path : "
    ).strip()

    if not user_input:

        raise ValueError(
            "YouTube URL or file path "
            "cannot be empty."
        )

    # =========================================================
    # 2. MEDIA EXTRACTION
    # =========================================================

    print()
    print("Extracting audio...")

    source = get_audio_source(
        user_input
    )

    print()
    print("Source ID:")
    print(source.source_id)

    print()
    print("Source Name:")
    print(source.source_name)

    print()
    print("Audio Path:")
    print(source.audio_path)

    # =========================================================
    # 3. AUDIO CHUNKING
    # =========================================================

    print()
    print("Splitting audio...")

    audio_chunks = split_audio(
        audio_path=source.audio_path,
        source_id=source.source_id
    )

    print()
    print(
        f"Audio chunks created: "
        f"{len(audio_chunks)}"
    )

    # =========================================================
    # 4. LANGUAGE
    # =========================================================

    print()
    print("Select transcription language:")

    print("1. English")
    print("2. Hindi")
    print("3. Telugu")

    choice = input(
        "Enter choice (1/2/3): "
    ).strip()

    language_map = {

        "1": "english",
        "2": "hindi",
        "3": "telugu"

    }

    language = language_map.get(
        choice,
        "english"
    )

    print()
    print(
        f"Selected language: {language}"
    )

    # =========================================================
    # 5. SARVAM TRANSCRIPTION
    # =========================================================

    transcription = (
        transcribe_audio_chunks(
            source=source,
            audio_chunks=audio_chunks,
            language=language
        )
    )

    transcript = transcription.get(
        "transcript",
        ""
    )

    if not transcript:

        raise ValueError(
            "Transcription is empty."
        )

    # =========================================================
    # 6. DISPLAY TRANSCRIPT
    # =========================================================

    print_separator()

    print("TRANSCRIPT")

    print("=" * 70)

    print(transcript)

    # =========================================================
    # 7. SUMMARY CHUNKING
    # =========================================================

    print()
    print(
        "Creating summary chunks..."
    )

    summary_chunks = create_text_chunks(
        source=source,
        transcript=transcript
    )

    print()
    print(
        "Summary chunks created: "
        f"{len(summary_chunks.get('chunks', []))}"
    )

    # =========================================================
    # 8. VIDEO SUMMARY
    # =========================================================

    print()
    print(
        "Generating video summary..."
    )

    summary = create_summary(
        source=source,
        chunk_result=summary_chunks
    )

    final_summary = summary.get(
        "final_summary",
        ""
    )

    print_separator()

    print(
        "FINAL VIDEO SUMMARY"
    )

    print("=" * 70)

    print(final_summary)

    # =========================================================
    # 9. RAG CHUNKING
    # =========================================================

    print()
    print(
        "Creating RAG chunks..."
    )

    rag_chunks = create_rag_chunks(
        source=source,
        transcript=transcript
    )

    chunks = rag_chunks.get(
        "chunks",
        []
    )

    print()
    print(
        f"RAG chunks created: "
        f"{len(chunks)}"
    )

    # =========================================================
    # 10. EMBEDDING + CHROMADB
    # =========================================================

    print()
    print(
        "Creating embeddings "
        "and storing in ChromaDB..."
    )

    store_chunks(
        source_id=source.source_id,
        chunks=chunks
    )

    # =========================================================
    # 11. ASK QUESTIONS
    # =========================================================

    print_separator()

    print(
        "VIDEO Q&A"
    )

    print("=" * 70)

    print(
        "Ask questions about the video."
    )

    print(
        "Type 'exit' to finish."
    )

    while True:

        question = input(
            "\nYour question: "
        ).strip()

        if question.lower() == "exit":

            break

        if not question:

            continue

        # =====================================================
        # 12. QUERY EMBEDDING
        # 13. SIMILARITY SEARCH
        # 14. TOP-K DOCUMENTS
        # 15. CONTEXT BUILDING
        # 16. GEMINI
        # =====================================================

        result = answer_question(
            source_id=source.source_id,
            question=question,
            top_k=5
        )

        print()
        print("-" * 70)

        print("ANSWER")

        print("-" * 70)

        print(
            result["answer"]
        )

        print("-" * 70)

    # =========================================================
    # 17. COMPLETED
    # =========================================================

    print_separator()

    print(
        "KARTHIK ASK PROJECT COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()