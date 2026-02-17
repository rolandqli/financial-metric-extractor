# Earnings PDF Extractor (Next.js)

Next.js version of the frontend. Same UI and API as the Vite frontend; backend (FastAPI) is unchanged.

## Setup

```bash
cd frontend-next
cp .env.example .env   # optional: set NEXT_PUBLIC_API_BASE_URL
npm install
```

## Run

**Dev (port 3000):**

```bash
npm run dev
```

Open http://localhost:3000. Ensure the FastAPI backend is running on port 8000.

**Build and start:**

```bash
npm run build
npm start
```

## Env

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Structure

- `app/` – App Router: `layout.jsx`, `page.jsx`, `globals.css`
- `components/` – `ReportProcessor.jsx` (client component)
- `lib/` – `reportService.js` (API client)

Backend CORS allows `http://localhost:3000` and `http://127.0.0.1:3000` for this app.
