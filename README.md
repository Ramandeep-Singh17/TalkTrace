# 🎙️ TalkTrace — AI Meeting Intelligence Assistant

> **Turn long meetings into searchable, structured, actionable knowledge.**

TalkTrace is an end-to-end AI meeting intelligence application that takes a **YouTube meeting URL or a local audio/video file** and converts it into a structured meeting workspace.

Instead of only generating a transcript, TalkTrace builds a complete pipeline around the transcript:

- 🎧 Audio/video acquisition and preprocessing
- 📝 Speech-to-text transcription
- 🌐 English and Hinglish transcription paths
- 🧠 AI-generated meeting summary
- 🏷️ Automatic meeting title generation
- 📌 Action-item extraction
- ✅ Key-decision extraction
- ❓ Open-question extraction
- 🔎 Retrieval-Augmented Generation (RAG)
- 💬 Context-aware questions about the meeting
- 🌐 Streamlit deployment for public access

---

## 🚀 Live Demo

### 🌐 Try TalkTrace

**https://talktrace-by-raman.streamlit.app/**

### 💻 GitHub Repository

**https://github.com/Ramandeep-Singh17/TalkTrace**

---

# 📌 What Problem Does TalkTrace Solve?

Meetings often contain a large amount of information:

- decisions
- tasks
- deadlines
- unresolved questions
- technical discussions
- requirements
- follow-ups
- important statements

Reading or manually processing a long recording is time-consuming.

TalkTrace automates this workflow.

### Input

A user provides either:

1. A YouTube meeting/video URL, or
2. A local audio/video file

### Output

TalkTrace produces:

1. A generated meeting title
2. A professional meeting summary
3. Action items with owner/deadline when available
4. Key decisions
5. Open questions
6. Full transcript
7. A searchable RAG knowledge base
8. A conversational Q&A interface over the meeting

The goal is to transform **unstructured meeting audio into structured, searchable knowledge**.

---

# ✨ Core Features

## 1. 🎧 YouTube and Local File Processing

TalkTrace supports two input paths.

### YouTube URL

The application uses **yt-dlp** to download the best available audio stream.

The downloaded media is then converted into WAV audio using FFmpeg/Pydub.

### Local File

A user can upload an audio/video file.

TalkTrace converts the file into:

- WAV
- Mono channel
- 16 kHz sample rate

This standardization makes the audio suitable for downstream speech processing.

---

# 2. ✂️ Long Audio Chunking

Long recordings are not processed as one enormous audio object.

TalkTrace divides the normalized WAV file into **10-minute chunks**.

This provides several advantages:

- avoids processing very large audio objects at once
- reduces memory pressure
- makes long recordings easier to process
- allows sequential transcription
- makes failures easier to isolate

```text
Long Audio
    ↓
WAV Conversion
    ↓
Mono + 16 kHz
    ↓
10-Minute Chunks
    ↓
Transcription
```

---

# 3. 📝 Speech-to-Text Pipeline

TalkTrace currently has two transcription paths.

## 🇬🇧 English → OpenAI Whisper

For English mode, TalkTrace uses the locally loaded **OpenAI Whisper** model.

The default model is:

```text
small
```

The model can also be configured through:

```text
WHISPER_MODEL
```

Whisper runs locally inside the application environment.

CPU-compatible inference is explicitly configured using:

```python
fp16=False
```

This allows Whisper to run in environments without a CUDA GPU.

---

## 🇮🇳 Hinglish → Sarvam AI

For Hinglish mode, TalkTrace routes the audio through **Sarvam AI's speech-to-text translation API**.

The configured model is:

```text
saaras:v2.5
```

The Sarvam synchronous API used by the project has a short audio-request limitation.

Therefore, each 10-minute TalkTrace audio chunk is further divided into **25-second pieces** before being sent to Sarvam.

```text
10-minute audio chunk
        ↓
25-second pieces
        ↓
Sarvam STT + Translation
        ↓
English transcript
```

Temporary Sarvam audio pieces are deleted after processing.

This makes the Hinglish transcription pipeline capable of processing longer recordings while respecting the API's request limitations.

---

# 4. 🧠 AI Meeting Summarization

After transcription, TalkTrace sends the transcript to a **Groq-hosted LLM**.

Current model:

```text
openai/gpt-oss-120b
```

The summarization pipeline is designed to handle long transcripts.

## Map → Combine Strategy

The transcript is first divided into smaller text chunks:

```text
Chunk Size: 3000 characters
Overlap:    200 characters
```

Each chunk is summarized independently.

The partial summaries are then combined and passed through another LLM step to generate the final professional meeting summary.

```text
Full Transcript
      ↓
Text Splitting
      ↓
Multiple Transcript Chunks
      ↓
Chunk-Level Summaries
      ↓
Combine Partial Summaries
      ↓
Final Meeting Summary
```

This is a practical **map-and-combine summarization architecture** for long transcripts.

---

# 5. 🏷️ Automatic Meeting Title Generation

TalkTrace automatically generates a meaningful professional title from the meeting transcript.

The title generation prompt limits the output to a maximum of **8 words**.

Only the first **2000 characters** of the transcript are used for title generation.

Example:

```text
Raw meeting recording
        ↓
Transcript
        ↓
LLM title generation
        ↓
"Project Architecture Planning Meeting"
```

---

# 6. 📌 Meeting Intelligence Extraction

A transcript alone is not enough for practical meeting management.

TalkTrace extracts three important categories of meeting intelligence.

---

## ✅ Action Items

For each action item, the system attempts to identify:

- Task description
- Owner
- Deadline

If an owner or deadline is not mentioned, the system returns:

```text
Not specified
```

The extraction prompts explicitly instruct the LLM **not to invent missing details**.

Example:

```text
1. Complete API integration
   Owner: Rahul
   Deadline: Friday
```

---

## 🎯 Key Decisions

TalkTrace extracts decisions that were explicitly made during the meeting.

The system attempts to distinguish between:

- confirmed decisions
- suggestions
- ongoing discussions

Suggestions should not automatically become confirmed decisions.

Example:

```text
1. The team decided to use PostgreSQL
2. Deployment will be done using Docker
```

---

## ❓ Open Questions

TalkTrace extracts:

- unresolved questions
- unanswered issues
- topics requiring follow-up

Questions that were clearly answered are intentionally excluded.

Example:

```text
1. Who will handle production deployment?
2. What is the final database schema?
```

---

# 7. 🔄 Extraction Strategy

Long transcripts are divided into:

```text
Chunk Size: 5000 characters
Overlap:    500 characters
```

Each chunk is processed independently.

The extracted results are then combined and deduplicated using another LLM step.

```text
Transcript
    ↓
5000-character chunks
    ↓
Extract:
  ├── Action Items
  ├── Key Decisions
  └── Open Questions
    ↓
Combine Partial Results
    ↓
Remove Duplicates
    ↓
Final Structured Output
```

This allows the application to process larger transcripts while maintaining structured outputs.

---

# 8. 🔎 Retrieval-Augmented Generation (RAG)

One of the most important features of TalkTrace is the meeting-specific Q&A system.

Instead of sending the entire transcript to the LLM every time the user asks a question, TalkTrace creates a searchable vector representation of the meeting transcript.

## RAG Pipeline

```text
Meeting Transcript
       ↓
Text Chunking
       ↓
LangChain Documents
       ↓
HuggingFace Embeddings
       ↓
ChromaDB Vector Store
       ↓
Similarity Retrieval
       ↓
Top 4 Relevant Chunks
       ↓
Groq LLM
       ↓
Context-Aware Answer
```

---

# 9. 🧩 RAG Document Chunking

For the vector database, the transcript is divided into:

```text
Chunk Size: 500 characters
Overlap:    50 characters
```

Each chunk is stored as a LangChain `Document`.

Each document receives metadata containing its:

```text
chunk_index
```

This creates smaller semantic units that can be searched independently.

---

# 10. 🔢 Embedding Model

TalkTrace uses:

```text
all-MiniLM-L6-v2
```

through the LangChain HuggingFace embedding integration.

The embedding model runs on:

```text
CPU
```

This avoids requiring a separate embedding API.

---

# 11. 🗄️ ChromaDB Vector Store

TalkTrace uses **ChromaDB** as the vector database.

Runtime vector database directory:

```text
vector_db/
```

Collection name:

```text
meeting_transcript
```

The vector store is built from the current meeting transcript during analysis.

The generated `vector_db/` directory is intentionally excluded from GitHub because it is runtime-generated data rather than application source code.

---

# 12. 🔍 Similarity Retrieval

When the user asks a question, TalkTrace performs semantic similarity search.

The retriever currently retrieves:

```text
k = 4
```

relevant transcript chunks.

These retrieved chunks are then passed to the Groq LLM as context.

Example:

```text
User Question
      ↓
Embedding / Similarity Search
      ↓
Top 4 Relevant Transcript Chunks
      ↓
Context + Question
      ↓
Groq LLM
      ↓
Answer
```

---

# 13. 🛡️ Grounded RAG Q&A

The RAG prompt explicitly instructs the LLM to answer **only from the meeting transcript context**.

If the requested information cannot be found, the system is instructed to respond:

```text
I could not find this information in the meeting transcript.
```

This helps reduce hallucinations and keeps the answers grounded in the actual meeting content.

---

# 🧱 Complete System Architecture

```text
                         ┌─────────────────────────┐
                         │       User Input        │
                         │                         │
                         │ YouTube URL / Local     │
                         │ Audio / Video File      │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Audio Processor      │
                         │                         │
                         │ yt-dlp / Pydub / FFmpeg │
                         │ WAV / Mono / 16 kHz     │
                         │ 10-min chunking         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Transcription       │
                         │                         │
                         │ English → Whisper       │
                         │ Hinglish → Sarvam AI    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Meeting Transcript    │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼────────────────────────┐
              │                       │                        │
              ▼                       ▼                        ▼
     ┌─────────────────┐    ┌─────────────────┐     ┌──────────────────┐
     │   Summarizer    │    │    Extractor    │     │    RAG Engine    │
     │                 │    │                 │     │                  │
     │ Map/Combine     │    │ Action Items    │     │ Text Chunking    │
     │ Summary         │    │ Decisions       │     │ Embeddings       │
     │ Title           │    │ Open Questions  │     │ ChromaDB         │
     └────────┬────────┘    └────────┬────────┘     │ Similarity       │
              │                      │              │ Retrieval        │
              │                      │              └────────┬─────────┘
              │                      │                       │
              └──────────────────────┴───────────────────────┘
                                                             │
                                                             ▼
                                                   ┌──────────────────┐
                                                   │   User Q&A       │
                                                   │                  │
                                                   │ Groq LLM         │
                                                   │ Grounded Answer  │
                                                   └──────────────────┘
```

---

# 🔄 End-to-End Execution Flow

When the user clicks **Analyse Meeting**, the application follows this sequence:

```text
1. Receive YouTube URL / uploaded file
                ↓
2. Download or convert media
                ↓
3. Normalize audio
   ├── WAV
   ├── Mono
   └── 16 kHz
                ↓
4. Split audio into 10-minute chunks
                ↓
5. Select transcription engine
   ├── English  → Whisper
   └── Hinglish → Sarvam AI
                ↓
6. Build complete transcript
                ↓
7. Generate meeting title
                ↓
8. Generate professional summary
                ↓
9. Extract action items
                ↓
10. Extract key decisions
                ↓
11. Extract open questions
                ↓
12. Create ChromaDB vector store
                ↓
13. Create similarity retriever
                ↓
14. Enable meeting-specific RAG Q&A
```

---

# 🧩 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| UI | Streamlit | Web application |
| YouTube Acquisition | yt-dlp | Download audio |
| Audio Processing | Pydub | Conversion, normalization and chunking |
| Media Processing | FFmpeg | Audio extraction/conversion |
| English STT | OpenAI Whisper | Local speech recognition |
| Hinglish STT | Sarvam AI | Speech-to-text + translation |
| LLM | Groq | Summary, title, extraction and Q&A |
| LLM Framework | LangChain | Prompting, LCEL chains and RAG orchestration |
| Vector Database | ChromaDB | Semantic meeting retrieval |
| Embeddings | HuggingFace / all-MiniLM-L6-v2 | Semantic embeddings |
| UI / Deployment | Streamlit Community Cloud | Public hosting |
| Source Control | Git + GitHub | Version control |
| Configuration | python-dotenv | Local environment variables |

---

# 📁 Project Structure

```text
TalkTrace/
│
├── app.py
│   └── Main Streamlit application and UI
│
├── main.py
│   └── Project entry/support module
│
├── core/
│   │
│   ├── transcriber.py
│   │   ├── Whisper model loading
│   │   ├── Whisper transcription
│   │   ├── Sarvam API integration
│   │   └── Language-based routing
│   │
│   ├── summarize.py
│   │   ├── Transcript splitting
│   │   ├── Chunk summarization
│   │   ├── Final summary generation
│   │   └── Title generation
│   │
│   ├── extractor.py
│   │   ├── Action-item extraction
│   │   ├── Decision extraction
│   │   ├── Question extraction
│   │   └── Result combination/deduplication
│   │
│   ├── rag_engine.py
│   │   ├── RAG chain creation
│   │   ├── Retriever integration
│   │   └── Grounded Q&A
│   │
│   └── vector_store.py
│       ├── HuggingFace embeddings
│       ├── ChromaDB
│       ├── Transcript chunking
│       └── Similarity retriever
│
├── utils/
│   │
│   └── audio_processor.py
│       ├── YouTube audio download
│       ├── Media → WAV conversion
│       ├── Audio normalization
│       └── 10-minute chunking
│
├── requirements.txt
│   └── Python dependencies
│
├── packages.txt
│   └── FFmpeg system dependency for Streamlit Cloud
│
├── README.md
│   └── Project documentation
│
├── test_app.py
│   └── Application test/support file
│
└── .gitignore
    └── Excludes secrets, runtime media and virtual environments
```

---

# 🔐 Environment Variables & Secrets

For local development, create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

For Streamlit Cloud, configure the same values under **Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
SARVAM_API_KEY = "your_sarvam_api_key"
WHISPER_MODEL = "small"
SARVAM_STT_MODEL = "saaras:v2.5"
```

### ⚠️ Security

Never commit API keys to GitHub.

The project intentionally keeps `.env` excluded through `.gitignore`.

---

# 🛠️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Ramandeep-Singh17/TalkTrace.git
cd TalkTrace
```

---

## 2. Create Virtual Environment

Python 3.11 is recommended.

```bash
python -m venv .venv
```

Activate on Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure FFmpeg is available for local execution.

---

## 4. Configure Environment Variables

Create:

```text
.env
```

Then add:

```env
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

---

## 5. Run the Application

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

---

# ☁️ Streamlit Community Cloud Deployment

TalkTrace is deployed using **Streamlit Community Cloud**.

The repository contains:

```text
requirements.txt
packages.txt
```

### `requirements.txt`

This installs the Python dependencies required by TalkTrace, including:

- Whisper
- PyTorch
- Torchaudio
- LangChain
- Groq
- ChromaDB
- HuggingFace embeddings
- Streamlit
- yt-dlp
- Pydub

### `packages.txt`

The project contains:

```text
ffmpeg
```

This installs the required FFmpeg system package in the Streamlit Cloud environment.

### Deployment Configuration

```text
Repository:
Ramandeep-Singh17/TalkTrace

Branch:
main

Main File:
app.py

Python:
3.11
```

### End User Requirements

Users accessing the hosted application only need:

```text
A web browser
```

They do **not** need to install:

- Python
- Whisper
- PyTorch
- FFmpeg
- LangChain
- ChromaDB

These dependencies run in the hosted application environment.

---

# 🔒 Security & Git Configuration

The repository intentionally excludes sensitive and runtime-generated files.

```text
.env
.venv/
__pycache__/
downloads/
*.wav
*.mp3
*.mp4
*.m4a
*.webm
vector_db/
```

This prevents:

- API keys from being pushed
- virtual environments from being committed
- large audio/video files from being committed
- runtime ChromaDB data from being committed

---

# 🧠 Important Engineering Decisions

## Why Audio Chunking?

Long recordings can be large and expensive to process as one object.

Chunking provides:

- lower memory pressure
- manageable processing
- better error isolation
- easier API handling
- support for long meetings

---

## Why 25-Second Sarvam Pieces?

The Sarvam synchronous speech-to-text endpoint used by the project has a short audio-request limitation.

Instead of sending a full 10-minute chunk, TalkTrace uses:

```text
25 seconds
```

per Sarvam request.

The 25-second value provides a small safety margin below the endpoint's limit.

---

## Why Whisper for English?

Whisper provides local speech recognition.

This means English audio can be processed without sending the audio to a separate transcription API.

It also makes the project demonstrate actual local speech-model inference.

---

## Why Sarvam for Hinglish?

Hinglish can contain a mixture of:

- Hindi
- English
- Indian conversational speech

TalkTrace uses Sarvam's speech-to-text translation path for this mode so that the resulting transcript can be used directly by the downstream English-oriented LLM pipeline.

---

## Why LangChain?

LangChain provides the orchestration layer for:

- Prompt templates
- LCEL chains
- Transcript splitting
- LLM invocation
- Retrievers
- Vector-store integration

---

## Why ChromaDB?

The application needs semantic retrieval rather than simple keyword search.

ChromaDB provides a lightweight vector database suitable for the meeting-specific RAG pipeline.

---

## Why HuggingFace Embeddings?

TalkTrace uses:

```text
all-MiniLM-L6-v2
```

for local CPU-based semantic embeddings.

This avoids requiring a separate embedding API.

---

## Why RAG Instead of Sending the Entire Transcript?

Sending the entire transcript for every question is inefficient for long meetings.

RAG allows the application to:

1. Search the transcript
2. Retrieve only relevant sections
3. Give those sections to the LLM
4. Generate a grounded answer

This makes the Q&A architecture more scalable and focused.

---

# 🧪 Example User Journey

Suppose a user provides a 45-minute project meeting.

TalkTrace processes it approximately as:

```text
45-minute video
      ↓
Audio extraction
      ↓
WAV + mono + 16 kHz
      ↓
5 × 10-minute chunks
      ↓
Whisper / Sarvam transcription
      ↓
Complete transcript
      ↓
┌───────────────────────────────────┐
│       Meeting Intelligence        │
│                                   │
│ Meeting Title                     │
│ Summary                           │
│ Action Items                      │
│ Key Decisions                     │
│ Open Questions                    │
└───────────────────────────────────┘
      ↓
Transcript
      ↓
Embeddings
      ↓
ChromaDB
      ↓
User asks:
"What did the team decide about deployment?"
      ↓
Similarity Retrieval
      ↓
Top 4 Relevant Transcript Chunks
      ↓
Groq LLM
      ↓
Grounded Answer
```

---

# 💬 Example RAG Questions

After a meeting has been analysed, users can ask:

```text
What were the main decisions made?

What action items were assigned?

Who was responsible for the deployment task?

What deadlines were discussed?

What problems were identified?

What was discussed about the database?

What did the team decide about the project architecture?

Were there any unresolved questions?

What was discussed about RAG?
```

The system answers using the retrieved meeting context.

---

# ⚠️ Current Limitations

TalkTrace is a strong project-level MVP, but several areas can be improved.

## 1. Speaker Diarization

The current Sarvam request uses:

```text
with_diarization = false
```

Therefore the current version does not identify individual speakers.

---

## 2. Runtime Resource Requirements

Whisper and the embedding model run inside the application environment.

Longer recordings therefore require more:

- CPU
- RAM
- processing time

---

## 3. Processing Time

A long meeting requires multiple operations:

- transcription
- summarization
- title generation
- action extraction
- decision extraction
- question extraction
- embeddings

Therefore processing time increases with meeting duration.

---

## 4. Vector Store Lifecycle

The ChromaDB vector store is generated at runtime for the current meeting.

It is not intended to be permanently versioned and committed to GitHub.

---

## 5. Transcript Quality

Final results depend on:

- audio quality
- background noise
- speaker clarity
- language mixing
- transcription model quality

---

## 6. YouTube Availability

YouTube processing depends on the provided video's availability and accessibility through the download pipeline.

---

# 🔮 Future Improvements

Potential future versions can add:

- 👥 Speaker diarization
- ⏱️ Speaker-wise timestamps
- 🧑‍💼 Speaker identification
- 📄 PDF meeting reports
- 📥 TXT/Markdown transcript export
- 📊 Meeting analytics dashboard
- 🔔 Automatic follow-up reminders
- 📧 Email-ready meeting summaries
- 🗃️ Persistent multi-meeting knowledge base
- 🔍 Search across multiple meetings
- 🧠 Conversation memory
- ⚡ Parallel chunk transcription
- 🎯 Better transcript citations in RAG answers
- 🗣️ More Indian-language support
- 🔐 Authentication
- 👤 User-specific meeting workspaces

---

# 🎯 What This Project Demonstrates

TalkTrace demonstrates multiple practical AI and software-engineering concepts.

## 🤖 Generative AI

- LLM-based summarization
- structured information extraction
- prompt engineering
- grounded question answering

## 🔎 RAG

- document chunking
- embeddings
- vector database
- semantic similarity search
- retrieval
- context injection
- retriever + LLM architecture
- grounded generation

## 🎙️ Speech AI

- local Whisper inference
- API-based speech recognition
- audio preprocessing
- long-audio chunking
- Hinglish processing
- speech-to-text translation

## 🐍 Backend / Python Engineering

- modular Python architecture
- environment-based configuration
- API integration
- error handling
- temporary file management
- dependency management

## ☁️ Deployment

- Git
- GitHub
- Streamlit Community Cloud
- Python dependency management
- system package management
- cloud secrets

---

# 📊 Project Pipeline at a Glance

| Stage | Input | Processing | Output |
|---|---|---|---|
| Acquisition | URL / File | yt-dlp / Upload | Raw media |
| Preprocessing | Raw media | FFmpeg / Pydub | WAV, mono, 16 kHz |
| Chunking | WAV | 10-minute splitting | Audio chunks |
| Transcription | Audio chunks | Whisper / Sarvam | Transcript |
| Title | Transcript | Groq LLM | Meeting title |
| Summary | Transcript | Map + Combine LLM | Summary |
| Extraction | Transcript | Chunked LLM extraction | Actions / Decisions / Questions |
| Embedding | Transcript | MiniLM embeddings | Vectors |
| Storage | Vectors | ChromaDB | Searchable knowledge base |
| Retrieval | User question | Similarity search | Top 4 relevant chunks |
| Q&A | Context + question | Groq LLM | Grounded answer |

---

# 📦 Major Dependencies

```text
yt-dlp
pydub
ffmpeg-python

openai-whisper
torch
torchaudio

requests

langchain
langchain-core
langchain-community
langchain-groq
langchain-text-splitters
langchain-chroma

chromadb
sentence-transformers
langchain-huggingface
huggingface-hub
tiktoken

groq
python-dotenv

streamlit
streamlit-extras
watchdog

reportlab
fpdf2
```

See `requirements.txt` for the complete dependency specification.

---

# 🏆 Why TalkTrace Is More Than a Basic AI Project

A simple meeting application could be:

```text
Audio → Speech-to-Text → Summary
```

TalkTrace goes further:

```text
                    ┌───────────────┐
                    │ Audio / Video │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Preprocessing │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Transcription │
                    │ Whisper/Sarvam│
                    └───────┬───────┘
                            ↓
                  ┌─────────┴─────────┐
                  ↓                   ↓
          ┌───────────────┐   ┌───────────────┐
          │ Meeting       │   │ RAG Knowledge │
          │ Intelligence  │   │ Base          │
          └───────┬───────┘   └───────┬───────┘
                  │                   │
                  │                   ↓
                  │           ┌───────────────┐
                  │           │ Retrieval     │
                  │           └───────┬───────┘
                  │                   │
                  └─────────┬─────────┘
                            ↓
                    ┌───────────────┐
                    │ User Q&A      │
                    │ Grounded LLM  │
                    └───────────────┘
```

This makes TalkTrace an end-to-end combination of:

**Speech AI + Generative AI + RAG + Vector Search + LLM Orchestration + Cloud Deployment**

rather than a simple transcription or chatbot project.

---

# 👨‍💻 Author

## Ramandeep Singh

**B.Tech — Computer Science & Engineering (AI & ML)**

### Areas of Interest

- Generative AI
- Agentic AI
- RAG Systems
- NLP
- Machine Learning
- Full-Stack AI Applications

---

# 🌐 Project Links

### 🚀 Live Demo

https://talktrace-by-raman.streamlit.app/

### 💻 GitHub Repository

https://github.com/Ramandeep-Singh17/TalkTrace

---

# ⭐ TalkTrace

> **From meeting audio to actionable intelligence.**

```text
Audio
  ↓
Transcription
  ↓
Structured Meeting Intelligence
  ↓
Semantic Knowledge Base
  ↓
Grounded Conversational Q&A
```

TalkTrace transforms unstructured meeting recordings into **searchable, summarized and actionable knowledge** using modern AI technologies.
