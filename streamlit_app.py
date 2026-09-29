import os
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AskTube AI",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD STREAMLIT SECRETS INTO ENVIRONMENT
# ============================================================

def load_secrets():

    secret_names = [
        "SARVAM_API_KEY",
        "SARVAM_STT_MODEL",
        "SARVAM_STT_MODE",
        "GOOGLE_API_KEY",
        "GEMINI_MODEL"
    ]

    for name in secret_names:

        if name in st.secrets:

            os.environ[name] = str(
                st.secrets[name]
            )


load_secrets()


# ============================================================
# IMPORT YOUR PIPELINE
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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #151923,
            #1b2230
        );
        border: 1px solid #303642;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #aab2c0;
    }

    .pipeline {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 20px;
    }

    .pipeline-item {
        background: #202632;
        border: 1px solid #343b48;
        padding: 10px 15px;
        border-radius: 12px;
        color: #e8edf5;
        font-size: 14px;
    }

    .section-card {
        background: #151923;
        border: 1px solid #2b313d;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
    }

    .answer-box {
        background: #151923;
        border-left: 4px solid #6c63ff;
        padding: 20px;
        border-radius: 12px;
        line-height: 1.7;
    }

    .status {
        padding: 10px;
        border-radius: 10px;
        background: #171c25;
        border: 1px solid #303642;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🎥 AskTube AI
        </div>

        <div class="hero-subtitle">
            YouTube Video Intelligence • Transcription •
            Summarization • RAG Question Answering
        </div>

        <div class="pipeline">

            <div class="pipeline-item">
                🎬 YouTube / File
            </div>

            <div class="pipeline-item">
                🎧 Audio
            </div>

            <div class="pipeline-item">
                🗣️ Sarvam AI
            </div>

            <div class="pipeline-item">
                📄 Transcript
            </div>

            <div class="pipeline-item">
                ✂️ Chunking
            </div>

            <div class="pipeline-item">
                🧠 Embeddings
            </div>

            <div class="pipeline-item">
                🗄️ ChromaDB
            </div>

            <div class="pipeline-item">
                💬 RAG Q&A
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    language = st.selectbox(
        "Transcription Language",
        [
            "English",
            "Hindi",
            "Telugu"
        ]
    )

    language_map = {
        "English": "english",
        "Hindi": "hindi",
        "Telugu": "telugu"
    }

    selected_language = language_map[
        language
    ]

    st.divider()

    st.markdown(
        """
        ### Pipeline

        🎬 Media  
        ↓  
        🎧 Audio Extraction  
        ↓  
        🗣️ Sarvam AI  
        ↓  
        📄 Transcript  
        ↓  
        ✂️ RAG Chunking  
        ↓  
        🧠 Embeddings  
        ↓  
        🗄️ ChromaDB  
        ↓  
        🔎 Similarity Search  
        ↓  
        🤖 Gemini  
        ↓  
        💬 Answer
        """
    )


# ============================================================
# INPUT
# ============================================================

st.subheader("🎬 Add Your Video")

input_method = st.radio(
    "Choose input method",
    [
        "YouTube URL",
        "Upload Audio / Video"
    ],
    horizontal=True
)

user_input = None


# ============================================================
# YOUTUBE
# ============================================================

if input_method == "YouTube URL":

    user_input = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )


# ============================================================
# FILE UPLOAD
# ============================================================

else:

    uploaded_file = st.file_uploader(
        "Upload your audio or video",
        type=[
            "mp3",
            "wav",
            "m4a",
            "mp4",
            "mov",
            "webm",
            "mkv",
            "avi"
        ]
    )

    if uploaded_file:

        os.makedirs(
            "storage/uploads",
            exist_ok=True
        )

        uploaded_path = os.path.join(
            "storage/uploads",
            uploaded_file.name
        )

        with open(
            uploaded_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        user_input = uploaded_path


# ============================================================
# PROCESS BUTTON
# ============================================================

process_video = st.button(
    "🚀 Process Video",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS PIPELINE
# ============================================================

if process_video:

    if not user_input:

        st.warning(
            "Please provide a YouTube URL or upload a file."
        )

        st.stop()

    try:

        # ----------------------------------------------------
        # 1. MEDIA
        # ----------------------------------------------------

        with st.status(
            "🎬 Processing video...",
            expanded=True
        ) as status:

            st.write(
                "Extracting audio..."
            )

            source = get_audio_source(
                user_input
            )

            st.write(
                f"Source: {source.source_name}"
            )

            # ------------------------------------------------
            # 2. AUDIO CHUNKING
            # ------------------------------------------------

            st.write(
                "Splitting audio..."
            )

            audio_chunks = split_audio(
                audio_path=source.audio_path,
                source_id=source.source_id
            )

            st.write(
                f"Created {len(audio_chunks)} audio chunks."
            )

            # ------------------------------------------------
            # 3. TRANSCRIPTION
            # ------------------------------------------------

            st.write(
                "Transcribing with Sarvam AI..."
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
                    "Transcription returned empty text."
                )

            st.write(
                "Transcription completed."
            )

            # ------------------------------------------------
            # 4. SUMMARY CHUNKING
            # ------------------------------------------------

            st.write(
                "Creating summary chunks..."
            )

            summary_chunks = create_text_chunks(
                source=source,
                transcript=transcript
            )

            # ------------------------------------------------
            # 5. SUMMARY
            # ------------------------------------------------

            st.write(
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

            # ------------------------------------------------
            # 6. RAG CHUNKING
            # ------------------------------------------------

            st.write(
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

            # ------------------------------------------------
            # 7. EMBEDDINGS + CHROMADB
            # ------------------------------------------------

            st.write(
                "Creating embeddings and storing "
                "documents in ChromaDB..."
            )

            store_chunks(
                source_id=source.source_id,
                chunks=chunks
            )

            status.update(
                label="✅ Video processing completed!",
                state="complete"
            )


        # ====================================================
        # SAVE SESSION
        # ====================================================

        st.session_state[
            "source_id"
        ] = source.source_id

        st.session_state[
            "source_name"
        ] = source.source_name

        st.session_state[
            "transcript"
        ] = transcript

        st.session_state[
            "summary"
        ] = final_summary

        st.session_state[
            "processed"
        ] = True


    except Exception as e:

        st.error(
            f"❌ Processing failed: {str(e)}"
        )

        st.stop()


# ============================================================
# RESULTS
# ============================================================

if st.session_state.get(
    "processed",
    False
):

    source_name = st.session_state.get(
        "source_name",
        "Video"
    )

    transcript = st.session_state.get(
        "transcript",
        ""
    )

    final_summary = st.session_state.get(
        "summary",
        ""
    )


    # ========================================================
    # VIDEO INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        f"📺 {source_name}"
    )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "📝 Summary",
            "📄 Transcript",
            "💬 Ask Questions"
        ]
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    with tab1:

        st.markdown(
            "### 🧠 Video Summary"
        )

        st.markdown(
            final_summary
        )

        st.download_button(
            label="⬇️ Download Summary",
            data=final_summary,
            file_name="video_summary.txt",
            mime="text/plain"
        )


    # ========================================================
    # TRANSCRIPT
    # ========================================================

    with tab2:

        st.markdown(
            "### 📄 Full Transcript"
        )

        st.text_area(
            "Transcript",
            transcript,
            height=500,
            label_visibility="collapsed"
        )

        st.download_button(
            label="⬇️ Download Transcript",
            data=transcript,
            file_name="transcript.txt",
            mime="text/plain"
        )


    # ========================================================
    # QUESTION ANSWERING
    # ========================================================

    with tab3:

        st.markdown(
            "### 💬 Ask Anything About This Video"
        )

        question = st.text_input(
            "Your question",
            placeholder="What is the main idea discussed in this video?"
        )

        top_k = st.slider(
            "Number of relevant documents",
            min_value=2,
            max_value=10,
            value=5
        )

        ask = st.button(
            "🔎 Ask",
            type="primary"
        )

        if ask:

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Searching the video and generating answer..."
                ):

                    try:

                        result = answer_question(
                            source_id=st.session_state[
                                "source_id"
                            ],
                            question=question,
                            top_k=top_k
                        )

                        answer = result.get(
                            "answer",
                            ""
                        )

                        st.markdown(
                            "### 🤖 Answer"
                        )

                        st.markdown(
                            f"""
                            <div class="answer-box">
                            {answer}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Question answering failed: {str(e)}"
                        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AskTube AI • Video Intelligence • "
    "Sarvam AI • ChromaDB • Gemini"
)
