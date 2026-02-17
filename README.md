# Earnings PDF Processor

Full-stack app for extracting financial metrics from earnings PDFs (transcripts and decks) using an AI/LLM backend.

## Quick Start

### 1. Install

From the project root:

```bash
./scripts/install.sh
```

### 2. Configure

**Backend** — `backend/.env`:

```env
OPENAI_API_KEY=your-openai-api-key
```

**Frontend** — `frontend-next/.env` (optional):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Run

```bash
./scripts/run.sh
```

- **Backend API:** http://localhost:8000  
- **Frontend (Next.js):** http://localhost:3000  

Open http://localhost:3000 in your browser. Use **Ctrl+C** to stop both servers.

Logs are written to **`logs/backend.log`** and **`logs/frontend.log`**.

## Project Structure

```
.
├── backend/           # FastAPI API
│   ├── routers/      # API routes
│   ├── services/     # Extraction / LLM logic
│   ├── utils.py      # Helpers
│   ├── main.py       # App entry
│   └── requirements.txt
├── frontend-next/    # Next.js + React + Tailwind
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── logs/             # backend.log, frontend.log (created by run.sh)
├── scripts/
│   ├── install.sh    # One-time setup
│   └── run.sh        # Start backend + frontend
└── README.md
```

## Requirements

- **Python** 3.9+
- **Next.js**

## Documentation

- [Backend API](./backend/README.md)
- [Frontend (Next.js)](./frontend-next/README.md)

**Backend:**

```bash
cd backend
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
# Set OPENAI_API_KEY in .env
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend-next
npm install
npm run dev
```
