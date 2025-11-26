# Deployment Guide

This runbook explains how to promote Z-GPT from local development to a production-like environment. It covers prerequisites, environment configuration, container builds, database migrations, deployment options, and verification steps.

## 1. Prerequisites

- Docker 24+ with the Compose plugin (`docker compose version`).
- Access to a container registry (GHCR, ECR, ACR, etc.) for publishing images.
- A PostgreSQL database (managed or self-hosted). SQLite is only suitable for local dev.
- Redis 6+ for rate limiting and token revocation storage.
- A TLS-terminating reverse proxy or ingress (nginx, Traefik, ALB) that supports HTTP/1.1 keep-alive for Server-Sent Events.
- Secrets management strategy (e.g., `.env` for staging, cloud secrets for prod).

## 2. Environment Configuration

Copy `.env.example` (or `.env`) and populate production-ready values. Key variables:

| Variable | Description |
| --- | --- |
| `APP_ENV=production` | Enables production toggles/logging.
| `DB_URL=postgresql+psycopg://user:pass@host:5432/zgpt` | Target PostgreSQL DSN.
| `REDIS_URL=redis://host:6379/0` | Redis for rate limiting and caching.
| `JWT_SECRET_KEY`, `JWT_ALGORITHM` | Strong secret + HS256/RS256 algorithm.
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Optional upstream LLM keys.
| `CHAT_DEVICE`, `CHAT_PRECISION` | Use `cuda` on GPU-enabled nodes.
| `IMAGE_ENABLED=false` | Disable SD pipeline if hardware is limited.
| `OTEL_*`, `METRICS_ENABLED` | Wire tracing/metrics endpoints.

Store the frontend API origin in `frontend/.env.production` (or via deploy platform):

```
REACT_APP_API_BASE=https://api.your-domain.com
```

## 3. Build & Publish Containers

```bash
# Backend
docker build -f Dockerfile.backend -t ghcr.io/<org>/zgpt-backend:$(git rev-parse --short HEAD) .
docker push ghcr.io/<org>/zgpt-backend:$(git rev-parse --short HEAD)

# Frontend
docker build -f Dockerfile.frontend -t ghcr.io/<org>/zgpt-frontend:$(git rev-parse --short HEAD) .
docker push ghcr.io/<org>/zgpt-frontend:$(git rev-parse --short HEAD)
```

Tag images with semantic versions (e.g., `v1.0.0`) for reproducible rollouts.

## 4. Database Setup & Migrations

1. Provision the target PostgreSQL database and create the `zgpt` user with least privileges.
2. Run Alembic migrations against the database **before** starting new backend pods:

```bash
DB_URL=postgresql+psycopg://zgpt:secret@db-host:5432/zgpt alembic upgrade head
```

3. Schedule backups (daily logical dump + hourly PITR snapshots) and monitor disk usage.

## 5. Deployment Options

### Option A: Docker Compose (staging / single-node prod)

```bash
cp .env .env.prod  # populate with production values
REACT_APP_API_BASE=https://api.example.com docker compose --env-file .env.prod up -d --build
```

Expose the backend via your reverse proxy:

```
backend.example.com -> http://host-ip:8000 (proxy_pass, keep-alive on)
app.example.com     -> http://host-ip:3000
```

### Option B: Kubernetes / ECS

- Create `Secret` objects for `.env` values (JWT secrets, DB credentials, API keys).
- Deploy Redis/Postgres via managed services or Helm charts (bitnami/postgresql, bitnami/redis).
- Define two deployments (`backend`, `frontend`) referencing the pushed images and injecting env vars.
- Configure an Ingress or ALB with sticky HTTP/1.1 connections for `/chat/stream` SSE.
- Use HorizontalPodAutoscaler on the backend (CPU and latency driven). Ensure each pod has access to Redis and Postgres subnets.

## 6. Observability & Operations

- **Metrics:** scrape `https://api.example.com/metrics` with Prometheus; dashboards should track request rate, latency, and rate-limit hits.
- **Tracing:** set `OTEL_EXPORTER_ENDPOINT` to your collector; propagate request IDs via the `X-Request-ID` header (already emitted by middleware).
- **Logs:** forward container logs to your aggregator (CloudWatch, Loki, ELK). Include `request_id` + `session_id` fields for correlation.
- **Scaling considerations:**
  - Enable Redis so rate limits remain consistent across pods.
  - Pin `CHAT_DEVICE=cuda` on GPU nodes; for CPU-only clusters, keep `CHAT_PRECISION=float16` to reduce RAM.
  - Disable `IMAGE_ENABLED` if GPU budget is limited.

## 7. Verification Checklist

After every deploy:

1. Run Alembic migrations and confirm they finish successfully.
2. `curl -f https://api.example.com/healthz` (basic process liveness).
3. `curl -f https://api.example.com/readyz` and ensure `status` is `ready`.
4. Verify protected endpoints with a smoke user (`/auth/signup`, `/chat/`).
5. Hit `/metrics` and confirm Prometheus scrapes succeed.
6. Tail backend logs to ensure rate limiting, moderation, and SSE streaming emit no errors.
7. From the frontend URL, log in, send a chat message, generate an image (if enabled), and delete a session.
8. Run automated tests when possible:

```bash
pytest backend/tests -vv
cd frontend && CI=1 npm test -- --runInBand
```

## 8. Rollback Procedure

- Frontend is static; redeploy the previous image tag to revert instantly.
- Backend rollbacks require two actions:
  1. Redeploy the prior backend image tag.
  2. Apply `alembic downgrade` if the failed release introduced incompatible schema changes.
- If Redis becomes unavailable, the middleware automatically falls back to in-memory rate limiting; monitor logs and restore Redis ASAP.

Document every deploy in your change log and keep this guide in sync when the architecture evolves (e.g., when adding new services or queues).
