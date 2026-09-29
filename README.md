
# 🎥 AskTube AI

### YouTube Video Intelligence & RAG Question Answering

AskTube AI is an AI-powered video understanding application that allows users to provide a YouTube URL or upload an audio/video file and interact with its content using AI.

## 🚀 Features

- 🎬 YouTube URL processing
- 📁 Audio/video file upload
- 🎧 Audio extraction
- 🗣️ Sarvam AI transcription
- 📄 Full transcript generation
- 🧠 AI-powered video summarization
- ✂️ Text chunking
- 🧩 RAG chunking
- 🔢 Text embeddings
- 🗄️ ChromaDB vector storage
- 🔎 Similarity search
- 📚 Top-K document retrieval
- 🤖 Gemini-powered question answering
- 💬 Ask questions about the video
- ⬇️ Download transcript
- ⬇️ Download summary
- 🎨 Streamlit UI

## 🏗️ Architecture

```text
YouTube URL / File
        ↓
Audio Extraction
        ↓
Audio Chunking
        ↓
Sarvam AI
        ↓
Transcript
        ↓
        ├──────────────→ Summary Chunking
        │                       ↓
        │                  Gemini
        │                       ↓
        │               Video Summary
        │
        ↓
RAG Chunking
        ↓
Embeddings
        ↓
ChromaDB
        ↓
User Question
        ↓
Query Embedding
        ↓
Similarity Search
        ↓
Top-K Documents
        ↓
Relevant Context
        ↓
Question + Context
        ↓
Gemini
        ↓
Final Answer
```
