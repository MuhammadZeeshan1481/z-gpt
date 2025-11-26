# Z-GPT: AI Assistant with Chat, Image Generation, and Translation

Z-GPT is a full-stack AI assistant built with FastAPI + SQLModel on the backend and a React SPA on the frontend. It now ships with persistent chat sessions, real-time streaming replies, inline language detection/translation, and guarded rate limits so the same codebase can power hackathon demos or production pilots.

## Architecture Highlights

- **Three-tier stack:** React SPA (Bootstrap styling) → FastAPI service → SQLModel database (SQLite by default, Postgres-ready via `DB_URL`).
- **Event streaming:** Chat replies are delivered with Server-Sent Events (SSE) for low-latency UI updates; the backend falls back to blocking responses for legacy clients.
- **Persistence layer:** Every conversation is stored with `ChatSession`/`ChatMessage` models, enabling session lists, hydration, and deletion APIs.
- **ML integrations:** Hugging Face Transformers for chat, Diffusers for image generation (feature-flagged), Argos Translate + langdetect for multilingual flows.
- **Operational readiness:** Structured logging, rate limiting middleware, Docker/Compose manifests, and a complete pytest + React Testing Library suite.

## Features

- Chatbot using Hugging Face Transformers (streaming + persistent history)
- Prompt-based image generation using Diffusers (opt-in via `IMAGE_ENABLED`)
- Language detection + Argos Translate to mirror user language
- Session sidebar with search, deletion, and automatic hydration
- Offline/streaming banners, cancel button, and graceful SSE fallback
- Clean React UI with Jest/RTL coverage for core UX widgets

## Backend Setup (FastAPI)

```bash
git clone https://github.com/your-username/z-gpt.git
cd z-gpt
python -m venv .venv
.venv\Scripts\activate  # On Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Configuration

Copy `.env.example` to `.env` and adjust as needed:

```
APP_ENV=production  # development|staging|production
CHAT_DEVICE=cpu     # or cuda if you have a GPU
CHAT_PRECISION=float16
IMAGE_ENABLED=false # disable heavy SD pipeline locally if RAM is limited
```

Key toggles:

- `CHAT_DEVICE` / `CHAT_PRECISION` control LLM loading and memory usage.
- `IMAGE_ENABLED=false` skips loading the Stable Diffusion pipeline entirely.
- `RATE_LIMIT_PER_MINUTE` keeps hackathon demos safe from abuse.
- `REDIS_URL` enables a shared rate-limit store (fallbacks to in-memory if unset).
- `METRICS_ENABLED` / `METRICS_ENDPOINT` control the Prometheus exporter (default `/metrics`).
- `OTEL_EXPORTER_ENDPOINT` (+ optional `OTEL_EXPORTER_HEADERS`, `OTEL_EXPORTER_INSECURE`) streams traces via OTLP.

### Testing

```bash
pytest
```

## Frontend Setup (React)

```bash
cd frontend
npm install --legacy-peer-deps
REACT_APP_API_BASE=http://localhost:8000 npm start
```

Build for production with `npm run build`.

### Frontend Environment Flags

- `REACT_APP_API_BASE` (default `http://localhost:8000`) should match your deployed backend URL.
- `IMAGE_ENABLED` on the backend controls whether the UI exposes Stable Diffusion replies.
- SSE streaming is enabled by default; pass `forceSync` to `ChatBox` only in tests or when targeting legacy proxies that strip `text/event-stream`.

## Persistence & Session APIs

The backend exposes helper endpoints for the sidebar:

- `GET /chat/sessions` – ordered list with previews
- `GET /chat/sessions/{session_id}` – hydrated history for resuming
- `DELETE /chat/sessions/{session_id}` – removes a session and its messages

By default the SQLite file lives in `data/zgpt.db`. Override `DB_URL` (e.g., `postgresql+psycopg://user:pass@host/dbname`) to plug into a managed database.

### Database Migrations

Schema changes are now versioned with Alembic. Common workflows:

```bash
# Apply the latest schema to your current DB_URL (defaults to SQLite)
alembic upgrade head

# Generate a migration after editing SQLModel definitions
alembic revision --autogenerate -m "add foobar table"

# Target Postgres (example DSN)
DB_URL=postgresql+psycopg://zgpt:secret@localhost:5432/zgpt alembic upgrade head

# Roll back one step if needed
alembic downgrade -1
```

Tip: delete `data/zgpt.db` if it predates the migration baseline before running the first `upgrade`. Pytest fixtures continue to create/drop tables directly for fast feedback, while production/staging must run Alembic migrations during deploys.

### Observability & Rate Limiting

- Prometheus metrics are exposed at `/metrics` when `METRICS_ENABLED=true`. HTTP stats, SSE latency, and SQL timings are all emitted and ready for scraping.
- OpenTelemetry tracing can be toggled via `OTEL_EXPORTER_ENDPOINT` (e.g., `http://otel-collector:4317`). Set `OTEL_EXPORTER_HEADERS="api-key=..."` for authenticated collectors and `OTEL_EXPORTER_INSECURE=true` for plaintext transport.
- Set `REDIS_URL=redis://localhost:6379/0` (or a managed endpoint) to share rate-limit windows across backend replicas. The middleware automatically falls back to the in-memory deque implementation if Redis is unavailable.

## Docker / Compose

```bash
docker compose up --build
```

This launches the FastAPI backend on `http://localhost:8000` and serves the built React app on `http://localhost:3000`.

For production, point a reverse proxy or load balancer at the `backend` service (SSE requires HTTP/1.1 keep-alive). The `frontend` image is static and can be hosted on any CDN or object store.

## Testing Matrix

```bash
# Backend
pytest backend/tests -vv

# Frontend
cd frontend
CI=1 npm test -- --runInBand
```

Pytest fixtures reset the SQLite database between tests, so you can run the suite repeatedly without manual cleanup.

## API Overview

### POST /chat/
- Accepts a message and optional history
- Detects language and translates to English if needed
- Sends to LLM and returns translated response

### POST /image/generate
- Accepts a prompt string
- Returns a generated image in base64 format (feature flag via `IMAGE_ENABLED`)

### POST /translate/
- Accepts text, source language code, and target language code
- Returns translated text

## Troubleshooting & Ops

Common failure modes (missing models, SSE disconnects, DB resets) are documented in [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md). Highlights:

- Use `DB_URL=sqlite:///./test.db pytest` to mimic CI.
- If the streaming endpoint returns HTTP 500, inspect logs for transformer downloads or missing `transformers` install.
- The React UI surfaces offline/streaming issues via the status banner; check browser devtools for blocked SSE requests.

## Requirements

- Python 3.12+
- Node.js 20+
- Optional: Docker, Docker Compose

Python dependencies live in `requirements.txt`, frontend deps in `frontend/package.json`.

## Sample Prompts

- “Who was the first prime minister of Pakistan?”
- “Generate an image of a crescent moon over a desert night in Pakistan.”
- “پاکستان کا پہلا وزیراعظم کون تھا؟”
- “Tell me in French why Paris is famous.”

## Screenshots

Add up-to-date UI captures (dashboard, streaming reply, sessions sidebar) under `docs/screenshots/` and embed them here once ready:

```
![Chat streaming demo](docs/screenshots/chat-stream.png)
![Session sidebar](docs/screenshots/session-sidebar.png)
```

## Deployment Notes

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the full deployment runbook (prereqs, env templates, image publishing, migrations, verification checklist).

- **Container images:** `Dockerfile.backend` (FastAPI + Uvicorn) and `Dockerfile.frontend` (React build) are ready for registry pushes.
- **Env segregation:** store secrets (API keys, DB creds) in `.env` or platform-specific secret managers; never commit them.
- **Scaling:** run multiple `backend` replicas behind nginx/Traefik. SSE works over plain HTTP/1.1 keep-alive; if you terminate at a proxy, ensure it forwards `text/event-stream` without buffering.
- **Security roadmap:** JWT auth + bcrypt hashing can be layered on top of the existing session models. Rate limiting middleware already ships with sane defaults for hackathons.

## License

This project is licensed under the MIT License.
