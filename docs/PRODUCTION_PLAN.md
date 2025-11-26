# Production Hardening Plan

This document outlines the steps required to transform Z-GPT from hackathon-ready to production-ready.

## 1. Authentication & Authorization
- Introduce a `User` SQLModel with bcrypt-hashed passwords.
- Implement FastAPI routes for signup/login/refresh with JWT (short-lived access + refresh tokens).
- Scope chat sessions/messages by `user_id`; enforce via dependency.
- Frontend: add auth context, protected routes, and logout handling.

## 2. Database & Migrations
- Standardize on PostgreSQL for staging/prod; keep SQLite for local dev/testing.
- Add Alembic migrations (versioned schema for users, sessions, messages, rate limits).
- Provide seed scripts + rollback instructions.

## 3. Observability & Rate Limiting
- Ship structured logs to OpenTelemetry/OTLP endpoint; add request/DB metrics.
- Add `/metrics` endpoint (Prometheus-compatible) for health dashboards.
- Move rate-limit store from in-memory to Redis so multiple backend instances stay in sync.

## 4. Security & Compliance
- Integrate basic content moderation (prompt/response filters) before persisting.
- Enforce HTTPS, HSTS, CSP headers via FastAPI middleware or upstream proxy guidance.
- Document incident response: backup cadence, key rotation, audit logging.

## 5. CI/CD Pipeline
- GitHub Actions workflow: lint, pytest, npm test, Docker builds, security scans (Trivy/Bandit).
- Automatic image publishing on `main` tags; deploy via infrastructure-as-code (placeholder Terraform).

## 6. Frontend UX Polish
- Add global error boundaries, session timeout handling, analytics hooks.
- Support PWA install/offline caching for chat history snapshots.

## 7. Documentation & Runbooks
- Update README/ops docs when each milestone lands.
- Add `docs/RUNBOOK.md` for on-call procedures, `docs/SECURITY.md` for auth model, and `docs/DEPLOYMENT.md` for infrastructure diagrams.

The recommended execution order is (1) auth, (2) DB/migrations, (3) observability + Redis, (4) security policies, (5) CI/CD, (6) frontend/pwa, (7) docs.
