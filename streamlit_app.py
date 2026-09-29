import os
import streamlit as st

from tools.media_tool import get_audio_source
from tools.audio_chunk_tool import split_audio
from tools.transcription_tool import transcribe_audio_chunks
from tools.text_chunk_tool import create_text_chunks
from tools.summary_tool import create_summary

from tools.RAG_Pipeline.rag_chunk_tool import create_rag_chunks
from tools.RAG_Pipeline.vector_store_tool import store_chunks
from tools.RAG_Pipeline.rag_tool import answer_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Karthik Ask AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.stApp {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.hero-subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 16px;
    margin-bottom: 30px;
}

.pipeline-box {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 30px;
}

.pipeline-label {
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
    margin-bottom: 15px;
}

.pipeline-step {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 5px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

.info-box {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px;
}

.footer {
    text-align: center;
    color: #6b7280;
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #30363d;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "source" not in st.session_state:
    st.session_state.source = None

if "transcription" not in st.session_state:
    st.session_state.transcription = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "rag_chunks" not in st.session_state:
    st.session_state.rag_chunks = None

if "processed" not in st.session_state:
    st.session_state.processed = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">🤖 Karthik Ask AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'YouTube Video Intelligence • Transcription • Summarization • RAG Q&A'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PIPELINE
# ============================================================

st.markdown(
    '<div class="pipeline-label">AI PROCESSING PIPELINE</div>',
    unsafe_allow_html=True
)

pipeline = [
    ("🎥", "YouTube / File"),
    ("🎵", "Audio"),
    ("🗣️", "Sarvam AI"),
    ("📝", "Transcript"),
    ("✂️", "Chunking"),
    ("🧠", "Embeddings"),
    ("🗄️", "ChromaDB"),
    ("💬", "RAG Q&A")
]

pipeline_columns = st.columns(len(pipeline))

for column, (icon, name) in zip(
    pipeline_columns,
    pipeline
):

    with column:

        st.markdown(
            f"""
            <div class="pipeline-step">
                {icon}<br>
                {name}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Settings")

    st.divider()

    language = st.selectbox(
        "🎙️ Transcription Language",
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

    st.subheader("📌 Pipeline")

    st.write(
        "1. Media extraction"
    )

    st.write(
        "2. Audio chunking"
    )

    st.write(
        "3. Sarvam transcription"
    )

    st.write(
        "4. Text chunking"
    )

    st.write(
        "5. AI summarization"
    )

    st.write(
        "6. RAG chunking"
    )

    st.write(
        "7. Embeddings"
    )

    st.write(
        "8. ChromaDB"
    )

    st.write(
        "9. Similarity search"
    )

    st.write(
        "10. Gemini Q&A"
    )

    st.divider()

    if st.session_state.processed:

        st.success(
            "Video processed"
        )

    else:

        st.info(
            "No video processed"
        )


# ============================================================
# INPUT
# ============================================================

st.markdown(
    '<div class="section-title">🎬 Analyze Video</div>',
    unsafe_allow_html=True
)

input_tab, upload_tab = st.tabs(
    [
        "🔗 YouTube URL",
        "📁 Upload File"
    ]
)


youtube_url = ""

uploaded_file = None


with input_tab:

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )


with upload_tab:

    uploaded_file = st.file_uploader(
        "Upload Audio / Video",
        type=[
            "mp3",
            "wav",
            "m4a",
            "mp4",
            "webm",
            "mov",
            "avi",
            "mkv"
        ]
    )


st.write("")


# ============================================================
# PROCESS BUTTON
# ============================================================

process_button = st.button(
    "🚀 Process Video",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS VIDEO
# ============================================================

if process_button:

    if not youtube_url.strip() and uploaded_file is None:

        st.warning(
            "Please enter a YouTube URL or upload a file."
        )

        st.stop()

    try:

        # ====================================================
        # INPUT SOURCE
        # ====================================================

        if youtube_url.strip():

            input_source = youtube_url.strip()

        else:

            upload_dir = os.path.join(
                "storage",
                "uploads"
            )

            os.makedirs(
                upload_dir,
                exist_ok=True
            )

            input_source = os.path.join(
                upload_dir,
                uploaded_file.name
            )

            with open(
                input_source,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )


        # ====================================================
        # PROGRESS
        # ====================================================

        progress = st.progress(
            0
        )

        status = st.empty()


        # ====================================================
        # 1. MEDIA EXTRACTION
        # ====================================================

        status.info(
            "🎵 Extracting audio..."
        )

        source = get_audio_source(
            input_source
        )

        st.session_state.source = source

        progress.progress(
            10
        )


        # ====================================================
        # 2. AUDIO CHUNKING
        # ====================================================

        status.info(
            "✂️ Splitting audio..."
        )

        audio_chunks = split_audio(
            audio_path=source.audio_path,
            source_id=source.source_id
        )

        progress.progress(
            20
        )


        # ====================================================
        # 3. SARVAM TRANSCRIPTION
        # ====================================================

        status.info(
            "🗣️ Transcribing with Sarvam AI..."
        )

        transcription = transcribe_audio_chunks(
            source=source,
            audio_chunks=audio_chunks,
            language=selected_language
        )

        st.session_state.transcription = transcription

        transcript = transcription.get(
            "transcript",
            ""
        )

        if not transcript:

            raise ValueError(
                "Transcription is empty."
            )

        progress.progress(
            40
        )


        # ====================================================
        # 4. SUMMARY TEXT CHUNKING
        # ====================================================

        status.info(
            "✂️ Creating summary chunks..."
        )

        summary_chunks = create_text_chunks(
            source=source,
            transcript=transcript
        )

        progress.progress(
            50
        )


        # ====================================================
        # 5. SUMMARY
        # ====================================================

        status.info(
            "🧠 Generating video summary..."
        )

        summary = create_summary(
            source=source,
            chunk_result=summary_chunks
        )

        st.session_state.summary = summary

        progress.progress(
            60
        )


        # ====================================================
        # 6. RAG CHUNKING
        # ====================================================

        status.info(
            "📚 Creating RAG chunks..."
        )

        rag_chunks = create_rag_chunks(
            source=source,
            transcript=transcript
        )

        st.session_state.rag_chunks = rag_chunks

        chunks = rag_chunks.get(
            "chunks",
            []
        )

        progress.progress(
            70
        )


        # ====================================================
        # 7. EMBEDDINGS + CHROMADB
        # ====================================================

        status.info(
            "🧠 Creating embeddings and storing in ChromaDB..."
        )

        store_chunks(
            source_id=source.source_id,
            chunks=chunks
        )

        progress.progress(
            100
        )

        status.success(
            "✅ Video processing completed successfully."
        )

        st.session_state.processed = True

        st.session_state.messages = []

        st.success(
            f"Processed video: {source.source_name}"
        )


    except Exception as error:

        st.error(
            f"❌ Processing failed: {str(error)}"
        )


# ============================================================
# VIDEO INFORMATION
# ============================================================

if st.session_state.source:

    source = st.session_state.source

    st.divider()

    st.markdown(
        '<div class="section-title">📊 Video Information</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Source Type",
            source.source_type.upper()
        )

    with col2:

        st.metric(
            "Audio",
            "Extracted"
        )

    with col3:

        if st.session_state.rag_chunks:

            rag_count = len(
                st.session_state.rag_chunks.get(
                    "chunks",
                    []
                )
            )

        else:

            rag_count = 0

        st.metric(
            "RAG Chunks",
            rag_count
        )

    st.write("")

    with st.expander(
        "🎥 View Source Information"
    ):

        st.write(
            "**Source Name:**"
        )

        st.write(
            source.source_name
        )

        st.write(
            "**Source ID:**"
        )

        st.code(
            source.source_id
        )

        st.write(
            "**Audio Path:**"
        )

        st.code(
            source.audio_path
        )


# ============================================================
# SUMMARY
# ============================================================

if st.session_state.summary:

    st.divider()

    st.markdown(
        '<div class="section-title">📝 Video Summary</div>',
        unsafe_allow_html=True
    )

    final_summary = st.session_state.summary.get(
        "final_summary",
        ""
    )

    if final_summary:

        st.info(
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
            "No summary was generated."
        )


# ============================================================
# TRANSCRIPT
# ============================================================

if st.session_state.transcription:

    st.divider()

    st.markdown(
        '<div class="section-title">📜 Transcript</div>',
        unsafe_allow_html=True
    )

    transcript = st.session_state.transcription.get(
        "transcript",
        ""
    )

    if transcript:

        with st.expander(
            "👁️ View Full Transcript"
        ):

            st.text_area(
                "Transcript",
                transcript,
                height=450,
                label_visibility="collapsed"
            )

        st.download_button(
            label="⬇️ Download Transcript",
            data=transcript,
            file_name="full_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================
# RAG Q&A
# ============================================================

if st.session_state.processed:

    st.divider()

    st.markdown(
        '<div class="section-title">💬 Ask Questions About the Video</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Ask questions about the video. "
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
    # QUESTION
    # ========================================================

    question = st.chat_input(
        "Ask something about this video..."
    )


    if question:

        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )


        # ----------------------------------------------------
        # ASSISTANT
        # ----------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "🔍 Searching video context..."
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
                            "I couldn't find a relevant answer "
                            "in the video."
                        )

                    st.markdown(
                        answer
                    )


                    # ========================================
                    # RETRIEVED DOCUMENTS
                    # ========================================

                    documents = result.get(
                        "documents",
                        []
                    )

                    if documents:

                        with st.expander(
                            "🔎 Retrieved Context"
                        ):

                            for index, document in enumerate(
                                documents
                            ):

                                st.markdown(
                                    f"### Document {index + 1}"
                                )

                                if isinstance(
                                    document,
                                    dict
                                ):

                                    st.write(
                                        document.get(
                                            "text",
                                            document
                                        )
                                    )

                                else:

                                    st.write(
                                        document
                                    )

                                st.divider()


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )


                except Exception as error:

                    error_message = (
                        f"Unable to generate answer: {str(error)}"
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
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🤖 <b>Karthik Ask AI</b><br>
        YouTube → Sarvam AI → RAG → ChromaDB → Gemini
    </div>
    """,
    unsafe_allow_html=True
)