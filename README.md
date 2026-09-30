# 🎥 AskTube AI

### YouTube Video Intelligence & RAG-Based Question Answering

**AskTube AI** is an AI-powered video intelligence platform that transforms YouTube videos and uploaded audio/video files into **transcripts, summaries, and context-aware question answering**.

The application combines **Sarvam AI for speech-to-text, Gemini for summarization and question answering, Hugging Face embeddings, and ChromaDB for vector storage and semantic retrieval**.

## 🚀 Live Demo

🌐 **Try AskTube AI:**
https://karthik-ask-ai-video-intelligence-rag.streamlit.app/

📂 **GitHub Repository:**
https://github.com/ShivarathriKarthik/Karthik-Ask-AI-Video-Intelligence-RAG-Q-A

---

## ✨ Features

* 🎬 Process YouTube videos using a URL
* 📁 Upload audio/video files
* 🎧 Extract audio from video
* 🗣️ Generate transcripts using **Sarvam AI**
* 📄 Generate complete video transcripts
* 🧠 Generate AI-powered video summaries
* ✂️ Intelligent text chunking
* 🧩 RAG-based document chunking
* 🔢 Generate text embeddings
* 🗄️ Store embeddings using **ChromaDB**
* 🔎 Perform semantic similarity search
* 📚 Retrieve relevant Top-K chunks
* 🤖 Generate context-aware answers using **Gemini**
* 💬 Ask questions about video content
* ⬇️ Download transcripts
* ⬇️ Download summaries
* 🎨 Interactive **Streamlit** interface

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │   YouTube URL /      │
                    │   Audio / Video File │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Audio Extraction   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Audio Chunking    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Sarvam AI       │
                    │   Speech-to-Text     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Transcript      │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │ Summary Pipeline │          │  RAG Pipeline    │
      └────────┬─────────┘          └────────┬─────────┘
               │                             │
               ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐
      │      Gemini      │          │  Text Chunking   │
      │   Summarization  │          └────────┬─────────┘
      └────────┬─────────┘                   │
               │                             ▼
               ▼                    ┌──────────────────┐
      ┌──────────────────┐          │    Embeddings    │
      │  Video Summary   │          └────────┬─────────┘
      └──────────────────┘                   │
                                             ▼
                                    ┌──────────────────┐
                                    │    ChromaDB      │
                                    │  Vector Storage  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   User Question  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Query Embedding  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Similarity Search│
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Top-K Retrieval  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │ Relevant Context │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │      Gemini      │
                                    │ Context + Query  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Final Answer   │
                                    └──────────────────┘
```

---

## 🔄 RAG Pipeline

AskTube AI uses a Retrieval-Augmented Generation pipeline to answer questions based specifically on the processed video content.

```text
Transcript
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
ChromaDB
    ↓
User Query
    ↓
Query Embedding
    ↓
Similarity Search
    ↓
Top-K Relevant Chunks
    ↓
Context Construction
    ↓
Gemini LLM
    ↓
Context-Aware Answer
```

This approach allows the application to retrieve relevant sections of a long transcript instead of passing the entire transcript to the LLM for every question.

---

## 🧠 AI & Technology Stack

| Component              | Technology                     |
| ---------------------- | ------------------------------ |
| UI                     | Streamlit                      |
| Programming Language   | Python                         |
| Speech-to-Text         | Sarvam AI                      |
| LLM                    | Google Gemini                  |
| Embeddings             | Hugging Face                   |
| Vector Database        | ChromaDB                       |
| RAG                    | Retrieval-Augmented Generation |
| Video Processing       | FFmpeg                         |
| YouTube Processing     | yt-dlp                         |
| Environment Management | python-dotenv                  |

---

## 📂 Project Workflow

### 1️⃣ Input

Users can provide:

* YouTube video URL
* Audio file
* Video file

### 2️⃣ Audio Processing

For video inputs, the application extracts the audio using FFmpeg.

### 3️⃣ Transcription

The extracted audio is processed through **Sarvam AI** to generate the transcript.

### 4️⃣ Summarization

The transcript is processed using **Gemini** to generate a concise video summary.

### 5️⃣ RAG Indexing

The transcript is:

```text
Chunked
   ↓
Embedded
   ↓
Stored in ChromaDB
```

### 6️⃣ Question Answering

When a user asks a question:

```text
Question
   ↓
Query Embedding
   ↓
ChromaDB Similarity Search
   ↓
Top-K Relevant Chunks
   ↓
Context
   ↓
Gemini
   ↓
Answer
```

---

## 🎯 Example Use Cases

AskTube AI can be useful for:

* 📚 Learning from educational videos
* 🎓 Summarizing lectures
* 💼 Analyzing business presentations
* 🧑‍💻 Understanding technical tutorials
* 🎙️ Querying podcast content
* 📰 Extracting information from long-form videos
* 🔍 Searching specific information inside videos
* 📝 Creating quick notes from video content

---

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/ShivarathriKarthik/Karthik-Ask-AI-Video-Intelligence-RAG-Q-A.git

cd Karthik-Ask-AI-Video-Intelligence-RAG-Q-A
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
SARVAM_API_KEY=your_sarvam_api_key
```

Make sure `.env` is included in `.gitignore` and never commit API keys to GitHub.

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

---

## ☁️ Deployment

The application is deployed using **Streamlit Community Cloud**.

### Live Application

🌐 https://karthik-ask-ai-video-intelligence-rag.streamlit.app/

### Source Code

💻 https://github.com/ShivarathriKarthik/Karthik-Ask-AI-Video-Intelligence-RAG-Q-A

---

## 📌 Project Highlights

This project demonstrates practical implementation of:

* Retrieval-Augmented Generation
* Vector databases
* Semantic search
* Embeddings
* LLM-based summarization
* Context-aware question answering
* Speech-to-text processing
* Audio/video processing
* Prompt engineering
* End-to-end AI application development
* Streamlit deployment

---

## 🔮 Future Enhancements

* 🔊 Multi-language transcription
* 🌍 Multi-language question answering
* 🧠 Conversation memory
* 📌 Timestamp-based answers
* 🎞️ Video chapter detection
* 📊 Advanced transcript analytics
* 🔎 Hybrid search
* ⚡ Retrieval optimization
* 👥 Multi-user session management
* 📱 Improved mobile UI

---

## 👨‍💻 Author

### Karthik Shivarathri

AI/ML Engineer | Generative AI Engineer | Agentic AI Engineer

Interested in building production-oriented AI systems using **LLMs, RAG, Agentic AI, NLP, Machine Learning, and Cloud technologies**.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**Live Demo:**
https://karthik-ask-ai-video-intelligence-rag.streamlit.app/

**GitHub:**
https://github.com/ShivarathriKarthik/Karthik-Ask-AI-Video-Intelligence-RAG-Q-A
