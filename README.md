# EduAskAI

EduAskAI is a small desktop AI assistant for Bachelor of Computer Science students. It supports ordinary AI chat, local PDF reading, PDF-based questions and explanations, study-question generation, and web search for current information.

## Features

- AI chat using Groq's OpenAI-compatible API
- PDF text extraction and local ChromaDB indexing
- Questions answered from uploaded PDF material
- Easy, Medium, and Hard study-question generation with visible labels
- Simple educational explanations based on PDFs
- DuckDuckGo web search for current or external topics
- New Chat and one-click Copy response controls
- Modern dark CustomTkinter interface

## Architecture

```text
Tkinter UI
    |
EduAskAgent
 |       |       |
PDF RAG  Groq    DDGS web search
  |
ChromaDB (local)
```

The agent uses simple keyword-based routing: current-information requests use web search; questions about PDFs use retrieved PDF passages; all other requests use normal chat.

## Technologies

| Technology | Why it is used |
| --- | --- |
| Python + CustomTkinter | Clear, desktop-friendly interface |
| Groq + OpenAI SDK | Fast OpenAI-compatible LLM requests |
| pypdf | Local text extraction from PDF pages |
| ChromaDB | Local vector database for PDF retrieval |
| DuckDuckGo Search (DDGS) | Simple web-search capability |
| python-dotenv | Keeps the API key outside source code |

## Installation

1. Open a terminal in this `EduAskAI` folder.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install packages:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`, then add your Groq key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

5. Start the application:

```bash
python main.py
```

## Project Structure

```text
main.py             Application entry point
app/                Dark UI and reusable message widgets
agent/              Simple request routing and prompts
llm/                Groq OpenAI-compatible client
pdf/                PDF extraction, chunking, and Chroma retrieval
search/             DDGS web search
utils/              Configuration and text utilities
tests/              Small deterministic tests
data/pdfs/          Reserved local PDF data folder
database/chroma/    Local ChromaDB storage (created automatically)
```

## How PDF RAG works

```text
PDF → text extraction → clean text → chunks → embeddings → ChromaDB
Student question → vector retrieval → relevant passages → LLM answer
```

Each stored chunk includes its original PDF file name and page number. The AI is instructed to prefer retrieved content and admit when the PDF does not contain an answer.

## How the agent works

EduAskAI is one simple agent, not a multi-agent system. It can choose among normal conversation, PDF retrieval, PDF question generation, simple PDF explanation, and web search. Easy questions focus on facts, Medium questions on relationships, and Hard questions on reasoning and analysis.

## Offline PDF reading vs. online AI

PDF extraction and ChromaDB storage happen locally on your computer. The current Groq LLM configuration needs Internet access. Web search also needs Internet access. Therefore this version is an online AI application with local PDF processing and storage; it is not a completely offline application.

## Academic notes

The code is organized by responsibility and uses straightforward functions and classes. It is intended to demonstrate Python, prompt engineering, an AI agent, PDF processing, embeddings, a vector database, web search, and a desktop GUI in a form suitable for a BCS monograph defense.
