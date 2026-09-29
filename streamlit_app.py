import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Karthik Ask AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD ENVIRONMENT / STREAMLIT CLOUD SECRETS
# IMPORTANT:
# This happens BEFORE importing your tools because
# summary_tool.py checks GEMINI_API_KEY during import.
# ============================================================

load_dotenv()


def load_streamlit_secrets():

    try:

        if hasattr(st, "secrets"):

            for key in [
                "SARVAM_API_KEY",
                "SARVAM_STT_MODEL",
                "SARVAM_STT_MODE",
                "GEMINI_API_KEY",
                "GOOGLE_API_KEY",
                "GEMINI_MODEL",
                "GEMINI_MAX_RETRIES",
                "GEMINI_INITIAL_BACKOFF",
                "GEMINI_MAX_BACKOFF"
            ]:

                try:

                    value = st.secrets.get(key)

                    if value is not None:

                        os.environ[key] = str(value)

                except Exception:
                    pass

    except Exception:
        pass


load_streamlit_secrets()


# GOOGLE_API_KEY fallback
# Your summary_tool.py expects GEMINI_API_KEY.

if (
    not os.getenv("GEMINI_API_KEY")
    and os.getenv("GOOGLE_API_KEY")
):

    os.environ["GEMINI_API_KEY"] = os.getenv(
        "GOOGLE_API_KEY"
    )


# ============================================================
# IMPORT YOUR EXISTING PIPELINE
# ============================================================

from tools.media_tool import get_audio_source
from tools.audio_chunk_tool import split_audio
from tools.transcription_tool import transcribe_audio_chunks
from tools.text_chunk_tool import create_text_chunks
from tools.summary_tool import create_summary
from tools.RAG_Pipeline.rag_chunk_tool import create_rag_chunks
from tools.RAG_Pipeline.vector_store_tool import store_chunks
from tools.RAG_Pipeline.rag_tool import answer_question


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "processed": False,
    "processing": False,
    "source": None,
    "transcription": None,
    "transcript": "",
    "summary": None,
    "final_summary": "",
    "rag_chunks": None,
    "rag_ready": False,
    "audio_chunks": [],
    "messages": [],
    "error": None,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    .pipeline-card {
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        min-height: 100px;
        border: 1px solid rgba(128,128,128,0.25);
        background: rgba(128,128,128,0.08);
    }

    .pipeline-icon {
        font-size: 1.7rem;
        margin-bottom: 0.3rem;
    }

    .pipeline-title {
        font-size: 0.9rem;
        font-weight: 700;
    }

    .pipeline-status {
        font-size: 0.72rem;
        opacity: 0.7;
        margin-top: 0.25rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 750;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }

    .answer-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        background: rgba(128,128,128,0.06);
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 10px;
        padding: 0.8rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Settings")

    st.divider()

    st.subheader("🎙️ Transcription")

    language = st.selectbox(
        "Transcription Language",
        [
            "English",
            "Hindi",
            "Telugu"
        ],
        index=0
    )

    language_map = {
        "English": "english",
        "Hindi": "hindi",
        "Telugu": "telugu"
    }

    selected_language = language_map[language]

    st.divider()

    st.subheader("🤖 AI Configuration")

    st.caption(
        "Transcription: Sarvam AI"
    )

    st.caption(
        "Summarization: Gemini"
    )

    st.caption(
        "Vector Database: ChromaDB"
    )

    st.caption(
        "Retrieval: Semantic Similarity Search"
    )

    st.divider()

    st.subheader("📌 Pipeline")

    pipeline_items = [
        "1. Media extraction",
        "2. Audio chunking",
        "3. Sarvam transcription",
        "4. Text chunking",
        "5. AI summarization",
        "6. RAG chunking",
        "7. Embeddings",
        "8. ChromaDB",
        "9. Similarity search",
        "10. Gemini Q&A"
    ]

    for item in pipeline_items:
        st.write(item)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">🎬 Karthik Ask AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'YouTube Video Intelligence • Transcription • '
    'Summarization • RAG Q&A'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PIPELINE DISPLAY
# ============================================================

st.markdown(
    "### 🔄 AI Processing Pipeline"
)

pipeline = [
    ("🎥", "YouTube / File"),
    ("🎵", "Audio"),
    ("🎙️", "Sarvam AI"),
    ("📄", "Transcript"),
    ("✂️", "Chunking"),
    ("🧠", "Embeddings"),
    ("🗄️", "ChromaDB"),
    ("💬", "RAG Q&A"),
]

columns = st.columns(len(pipeline))

for column, item in zip(columns, pipeline):

    icon, title = item

    with column:

        st.markdown(
            f"""
            <div class="pipeline-card">
                <div class="pipeline-icon">{icon}</div>
                <div class="pipeline-title">{title}</div>
                <div class="pipeline-status">Pipeline</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown(
    "### 🎬 Analyze Video"
)

input_type = st.radio(
    "Select input type",
    [
        "🔗 YouTube URL",
        "📁 Upload File"
    ],
    horizontal=True
)


user_input = None


# ============================================================
# YOUTUBE URL
# ============================================================

if input_type == "🔗 YouTube URL":

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )

    user_input = youtube_url.strip()


# ============================================================
# FILE UPLOAD
# ============================================================

else:

    uploaded_file = st.file_uploader(
        "Upload audio or video",
        type=[
            "mp4",
            "mkv",
            "mov",
            "avi",
            "webm",
            "mp3",
            "wav",
            "m4a",
            "aac",
            "flac"
        ]
    )

    if uploaded_file:

        upload_dir = Path(
            "storage",
            "uploads"
        )

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        uploaded_path = (
            upload_dir /
            uploaded_file.name
        )

        with open(
            uploaded_path,
            "wb"
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )

        user_input = str(
            uploaded_path
        )

        st.success(
            f"Uploaded: {uploaded_file.name}"
        )


# ============================================================
# PROCESS BUTTON
# ============================================================

process_video = st.button(
    "🚀 Process Video",
    type="primary",
    use_container_width=True
)


# ============================================================
# MAIN PROCESSING PIPELINE
# ============================================================

if process_video:

    if not user_input:

        st.error(
            "Please provide a YouTube URL or upload a file."
        )

    else:

        # Reset previous session data

        st.session_state.processed = False
        st.session_state.processing = True
        st.session_state.source = None
        st.session_state.transcription = None
        st.session_state.transcript = ""
        st.session_state.summary = None
        st.session_state.final_summary = ""
        st.session_state.rag_chunks = None
        st.session_state.rag_ready = False
        st.session_state.audio_chunks = []
        st.session_state.messages = []
        st.session_state.error = None

        try:

            # ==================================================
            # STEP 1 - MEDIA EXTRACTION
            # ==================================================

            with st.status(
                "🎬 Processing video...",
                expanded=True
            ) as status:

                st.write(
                    "🎵 Extracting audio..."
                )

                source = get_audio_source(
                    user_input
                )

                st.session_state.source = source

                st.write(
                    f"Source: {source.source_name}"
                )

                st.write(
                    "Audio extraction completed."
                )

                # ==============================================
                # STEP 2 - AUDIO CHUNKING
                # ==============================================

                st.write(
                    "✂️ Splitting audio into chunks..."
                )

                audio_chunks = split_audio(
                    audio_path=source.audio_path,
                    source_id=source.source_id
                )

                st.session_state.audio_chunks = (
                    audio_chunks
                )

                st.write(
                    f"Created {len(audio_chunks)} "
                    f"audio chunks."
                )

                # ==============================================
                # STEP 3 - SARVAM TRANSCRIPTION
                # ==============================================

                st.write(
                    "🎙️ Transcribing with Sarvam AI..."
                )

                transcription = (
                    transcribe_audio_chunks(
                        source=source,
                        audio_chunks=audio_chunks,
                        language=selected_language
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

                st.session_state.transcription = (
                    transcription
                )

                st.session_state.transcript = (
                    transcript
                )

                st.write(
                    "Transcription completed."
                )

                # ==============================================
                # STEP 4 - SUMMARY TEXT CHUNKING
                # ==============================================

                st.write(
                    "✂️ Creating summary text chunks..."
                )

                summary_chunks = (
                    create_text_chunks(
                        source=source,
                        transcript=transcript
                    )
                )

                summary_chunk_count = len(
                    summary_chunks.get(
                        "chunks",
                        []
                    )
                )

                st.write(
                    f"Created {summary_chunk_count} "
                    f"summary chunks."
                )

                # ==============================================
                # STEP 5 - GEMINI SUMMARY
                # ==============================================

                st.write(
                    "🧠 Generating AI summary..."
                )

                summary = create_summary(
                    source=source,
                    chunk_result=summary_chunks
                )

                final_summary = summary.get(
                    "final_summary",
                    ""
                )

                st.session_state.summary = (
                    summary
                )

                st.session_state.final_summary = (
                    final_summary
                )

                st.write(
                    "Video summary completed."
                )

                # ==============================================
                # STEP 6 - RAG CHUNKING
                # ==============================================

                st.write(
                    "📚 Creating RAG chunks..."
                )

                rag_chunks = create_rag_chunks(
                    source=source,
                    transcript=transcript
                )

                chunks = rag_chunks.get(
                    "chunks",
                    []
                )

                st.session_state.rag_chunks = (
                    rag_chunks
                )

                st.write(
                    f"Created {len(chunks)} RAG chunks."
                )

                # ==============================================
                # STEP 7 - EMBEDDINGS + CHROMADB
                # ==============================================

                st.write(
                    "🧠 Creating embeddings..."
                )

                store_chunks(
                    source_id=source.source_id,
                    chunks=chunks
                )

                st.session_state.rag_ready = True

                st.write(
                    "🗄️ Embeddings stored in ChromaDB."
                )

                status.update(
                    label="✅ Video processing completed!",
                    state="complete",
                    expanded=False
                )

            st.session_state.processed = True
            st.session_state.processing = False

            st.success(
                "Video successfully processed. "
                "You can now ask questions."
            )

        except Exception as e:

            st.session_state.processing = False
            st.session_state.error = str(e)

            st.error(
                f"❌ Processing failed: {e}"
            )


# ============================================================
# SHOW PROCESSING INFORMATION
# ============================================================

if st.session_state.processed:

    source = st.session_state.source

    st.divider()

    st.markdown(
        "### 📊 Processing Information"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Audio Chunks",
            len(
                st.session_state.audio_chunks
            )
        )

    with col2:

        rag_chunks = (
            st.session_state.rag_chunks
        )

        rag_count = 0

        if rag_chunks:

            rag_count = len(
                rag_chunks.get(
                    "chunks",
                    []
                )
            )

        st.metric(
            "RAG Chunks",
            rag_count
        )

    with col3:

        transcript_words = len(
            st.session_state.transcript.split()
        )

        st.metric(
            "Transcript Words",
            transcript_words
        )

    with col4:

        st.metric(
            "RAG Status",
            "Ready"
            if st.session_state.rag_ready
            else "Not Ready"
        )


    # ========================================================
    # VIDEO DETAILS
    # ========================================================

    st.markdown(
        "### 🎥 Video Information"
    )

    st.info(
        f"**Source:** {source.source_name}\n\n"
        f"**Source ID:** {source.source_id}\n\n"
        f"**Language:** {language}"
    )


    # ========================================================
    # TABS
    # ========================================================

    tab_summary, tab_transcript, tab_rag = st.tabs(
        [
            "📝 Summary",
            "📄 Transcript",
            "🧠 RAG Information"
        ]
    )


    # ========================================================
    # SUMMARY TAB
    # ========================================================

    with tab_summary:

        st.markdown(
            "### 📝 Final Video Summary"
        )

        final_summary = (
            st.session_state.final_summary
        )

        if final_summary:

            st.markdown(
                final_summary
            )

            st.download_button(
                label="⬇️ Download Summary",
                data=final_summary,
                file_name="video_summary.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:

            st.warning(
                "No summary available."
            )


    # ========================================================
    # TRANSCRIPT TAB
    # ========================================================

    with tab_transcript:

        st.markdown(
            "### 📄 Full Transcript"
        )

        transcript = (
            st.session_state.transcript
        )

        if transcript:

            st.text_area(
                "Transcript",
                value=transcript,
                height=500,
                label_visibility="collapsed"
            )

            st.download_button(
                label="⬇️ Download Transcript",
                data=transcript,
                file_name="full_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:

            st.warning(
                "Transcript is not available."
            )


    # ========================================================
    # RAG INFORMATION TAB
    # ========================================================

    with tab_rag:

        st.markdown(
            "### 🧠 RAG Pipeline"
        )

        st.success(
            "RAG pipeline is ready for questions."
        )

        rag_chunks = (
            st.session_state.rag_chunks
        )

        if rag_chunks:

            chunks = rag_chunks.get(
                "chunks",
                []
            )

            st.write(
                f"Total RAG chunks: {len(chunks)}"
            )

            if chunks:

                with st.expander(
                    "View RAG chunks"
                ):

                    for index, chunk in enumerate(
                        chunks[:10]
                    ):

                        text = chunk.get(
                            "text",
                            ""
                        )

                        st.markdown(
                            f"**Chunk {index + 1}**"
                        )

                        st.write(
                            text[:1000]
                        )

                        st.divider()


    # ========================================================
    # Q&A SECTION
    # ========================================================

    st.divider()

    st.markdown(
        "### 💬 Ask Questions About the Video"
    )

    st.caption(
        "Ask anything based on the processed video. "
        "The system retrieves relevant transcript chunks "
        "from ChromaDB and sends the context to Gemini."
    )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    question = st.chat_input(
        "Ask a question about this video..."
    )


    if question:

        question = question.strip()

        if question:

            # ----------------------------------------------
            # USER MESSAGE
            # ----------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):

                st.markdown(
                    question
                )


            # ----------------------------------------------
            # ASSISTANT RESPONSE
            # ----------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "🔎 Searching video context..."
                ):

                    try:

                        result = answer_question(
                            source_id=source.source_id,
                            question=question,
                            top_k=5
                        )

                        answer = result.get(
                            "answer",
                            ""
                        )

                        if not answer:

                            answer = (
                                "I could not find "
                                "a relevant answer in "
                                "the video."
                            )

                        st.markdown(
                            answer
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                    except Exception as e:

                        error_message = (
                            f"Unable to answer the question: "
                            f"{e}"
                        )

                        st.error(
                            error_message
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": error_message
                            }
                        )


# ============================================================
# INITIAL SCREEN
# ============================================================

else:

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🎙️ **Transcription**\n\n"
            "Audio is extracted and converted "
            "into text using Sarvam AI."
        )

    with col2:

        st.info(
            "📝 **Summarization**\n\n"
            "Gemini generates a detailed summary "
            "from transcript chunks."
        )

    with col3:

        st.info(
            "🧠 **RAG Q&A**\n\n"
            "ChromaDB retrieves relevant context "
            "to answer your questions."
        )

    st.markdown(
        """
        ### 🚀 How it works

        1. Provide a **YouTube URL** or upload an audio/video file.
        2. Audio is extracted from the media.
        3. Audio is split into manageable chunks.
        4. **Sarvam AI** transcribes the audio.
        5. The transcript is chunked for **Gemini summarization**.
        6. The complete transcript is independently chunked for **RAG**.
        7. RAG chunks are embedded and stored in **ChromaDB**.
        8. Ask questions about the video.
        9. The question is embedded and matched against the vector database.
        10. The top relevant chunks are sent as context to **Gemini**.
        11. Gemini generates the final answer.
        """
    )