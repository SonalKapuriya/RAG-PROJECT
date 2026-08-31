# TalentLens — HR Resume RAG System

A production-ready RAG (Retrieval-Augmented Generation) system that lets HR teams upload PDF resumes and ask natural language questions about candidates.

**Stack:** FastAPI · LangChain · Qdrant · Groq (LLaMA 3 70B) · React · Vite · TailwindCSS

---

## Project Structure

```
hr-resume-rag/
├── backend/
│   ├── main.py            ← FastAPI app (3 endpoints)
│   ├── ingestor.py        ← PDF parse → chunk → embed → Qdrant
│   ├── retriever.py       ← similarity search + Groq chat
│   ├── models.py          ← Pydantic request/response schemas
│   ├── requirements.txt
│   └── .env.example       ← copy to .env and fill in your key
├── frontend/
│   ├── src/
│   │   ├── App.jsx              ← root layout (3-column desktop, tabbed mobile)
│   │   ├── api.js               ← fetch helpers
│   │   ├── index.css            ← Tailwind + component styles
│   │   └── components/
│   │       ├── UploadPanel.jsx      ← drag-and-drop PDF uploader
│   │       ├── ChatPanel.jsx        ← conversational Q&A with markdown
│   │       ├── CandidateCard.jsx    ← expandable source attribution
│   │       └── CandidatesSidebar.jsx ← list of indexed candidates
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
└── docker-compose.yml     ← Qdrant vector database
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker Desktop** (for Qdrant)
- **Groq API key** — free at https://console.groq.com

---

## Setup (Step by Step)

### Step 1 — Clone / open in VS Code

Open the `hr-resume-rag` folder in VS Code.

### Step 2 — Start Qdrant (vector database)

```bash
docker-compose up -d
```

Verify it's running: http://localhost:6333/dashboard
You should see the Qdrant web UI.

### Step 3 — Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Now open `.env` and add your Groq API key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4 — Run the backend

```bash
# Make sure you're in /backend with venv activated
uvicorn main:app --reload --port 8000
```

Verify: http://localhost:8000/docs — you should see the FastAPI Swagger UI.

### Step 5 — Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

---

## Usage

1. **Upload resumes** — drag and drop PDF resumes in the left panel. Click "Index Resumes". Wait for the success message.
2. **Ask questions** — type in the chat panel, e.g.:
   - *"Who has the most Python experience?"*
   - *"List candidates with AWS certifications"*
   - *"Compare the top 3 candidates for a senior engineer role"*
   - *"Who has worked at a startup before?"*
3. **View sources** — each answer shows which candidate excerpts were used. Click to expand.

---

## How it works (RAG Pipeline)

```
PDF Upload
  → PyMuPDF extracts text
  → LangChain splits into 800-char chunks (100 overlap)
  → sentence-transformers encodes each chunk (all-MiniLM-L6-v2, local)
  → Qdrant stores vectors + metadata

HR Question
  → same model encodes the question
  → Qdrant cosine similarity search → top 5 chunks
  → chunks injected into Groq prompt as context
  → LLaMA 3 70B generates answer
  → answer + sources returned to UI
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest` | Upload one or more PDF files |
| POST | `/chat` | Send a message with conversation history |
| GET | `/candidates` | List all indexed candidates |
| GET | `/health` | Health check |

Full docs at http://localhost:8000/docs

---

## Troubleshooting

**Qdrant connection error**
Make sure Docker is running and Qdrant container is up:
```bash
docker ps
docker-compose up -d
```

**GROQ_API_KEY not set**
Make sure you copied `.env.example` to `.env` and added your key.

**Embedding model slow on first run**
The `all-MiniLM-L6-v2` model (~90MB) downloads once on first use. Subsequent runs are instant.

**PDF text extraction fails**
Some scanned PDFs have no embedded text. Use PDFs with real text layers (most modern resumes do).

**CORS errors in browser**
Make sure the backend is running on port 8000 and frontend on 5173. Check `main.py` CORS origins.

---

## Extending the project

- **Add OCR** for scanned PDFs: integrate `pytesseract` in `ingestor.py`
- **Add filters** in the chat: pass candidate name to `retrieve_chunks()` to search within one resume
- **Export shortlist**: add a `POST /export` endpoint that returns a CSV of selected candidates
- **Re-ranking**: add cross-encoder re-ranking after the initial retrieval for better accuracy
- **Auth**: add FastAPI JWT auth to protect the endpoints in production
