# 🎙️ TalkTrace — AI Meeting Intelligence Assistant

TalkTrace is an AI-powered meeting intelligence application that transforms meeting audio, video, or YouTube content into meaningful, structured insights.

It can transcribe meetings, generate summaries, extract action items, identify key decisions and questions, and allow users to ask context-aware questions about the meeting using Retrieval-Augmented Generation (RAG).

---

## 🚀 Features

### 🎧 Audio & Video Processing
- Accepts YouTube URLs as input
- Supports local audio/video files
- Automatically extracts audio from YouTube videos
- Converts audio into WAV format
- Converts audio to mono 16 kHz format for speech processing
- Splits long audio into manageable chunks

### 📝 AI-Powered Transcription
TalkTrace supports multiple transcription approaches:

- **OpenAI Whisper** for English transcription
- **Sarvam AI** for Hinglish transcription
- Automatic processing of long recordings through audio chunking
- CPU-compatible Whisper transcription using `fp16=False`

### 🧠 Meeting Summarization
The application generates an AI-powered meeting summary using Groq-hosted LLMs.

The summarization pipeline can process long transcripts by splitting them into smaller sections before generating the final summary.

### 📌 Meeting Intelligence Extraction

TalkTrace extracts important information from the transcript:

- **Action Items**
- **Key Decisions**
- **Questions**

This converts a long meeting transcript into structured and useful information.

### 🔎 RAG-Based Meeting Q&A

TalkTrace creates a searchable knowledge base from the meeting transcript.

Users can ask questions such as:

> What were the main decisions made during the meeting?

> What action items were assigned?

> What was discussed about RAG?

The system retrieves relevant meeting context and uses an LLM to generate an answer based on the meeting content.

### 🏷️ Automatic Meeting Title Generation

TalkTrace automatically generates a meaningful title from the meeting transcript.

### 🖥️ Streamlit Interface

The application provides a simple Streamlit-based interface where users can:

1. Provide a YouTube URL or upload a local file
2. Select the transcription language
3. Analyse the meeting
4. View the generated title
5. Read the summary
6. View extracted insights
7. Read the complete transcript
8. Ask questions about the meeting

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User Input     │
                    │                     │
                    │ YouTube URL / File  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Audio Processor   │
                    │                     │
                    │ Download / Convert  │
                    │ WAV Conversion      │
                    │ Audio Chunking      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Transcription   │
                    │                     │
                    │ Whisper / Sarvam AI │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Meeting Transcript│
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌────────────┐   ┌─────────────┐
       │ Summarizer │   │  Extractor │   │ RAG Engine  │
       │            │   │            │   │             │
       │ Summary    │   │ Actions    │   │ Embeddings  │
       │ Title      │   │ Decisions  │   │ Retrieval   │
       │            │   │ Questions  │   │ Q&A         │
       └────────────┘   └────────────┘   └──────┬──────┘
                                                │
                                                ▼
                                      ┌──────────────────┐
                                      │   User Q&A       │
                                      │ Context-Aware    │
                                      │ Meeting Answers  │
                                      └──────────────────┘
