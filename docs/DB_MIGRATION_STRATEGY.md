# Database & Migration Strategy

This note codifies the plan to move from the current sqlite-in-memory workflow to a production-friendly PostgreSQL deployment managed via Alembic migrations.

## Current State (2025-11-26)
- ORM: SQLModel (SQLAlchemy 2.0 stack).
- Tables: `user`, `chatsession`, `chatmessage` created ad-hoc via `SQLModel.metadata.create_all()`.
- Environments: Local dev/test use SQLite (`sqlite:///./data/zgpt.db`). No canonical schema history.

## Target State
1. **Database Backends**
   - Local dev/tests remain on SQLite for zero-config convenience.
   - Staging/production use PostgreSQL (managed by `DATABASE_URL`/`DB_URL`).
2. **Schema Management**
   - Alembic provides versioned migrations (checked into repo under `backend/db/migrations`).
   - Initial baseline migration creates `user`, `chatsession`, `chatmessage` tables with constraints/indexes aligned with SQLModel definitions.
3. **Automation**
   - CLI entrypoints (make targets or `python -m alembic ...`) for `upgrade`/`downgrade` plus helper script to auto-generate migrations from SQLModel metadata when needed.
   - GitHub Actions job runs `alembic upgrade head` against an ephemeral SQLite DB to ensure migrations stay valid.
4. **Operations**
   - Docs spell out how to configure Postgres DSNs, seed an admin user, and roll back.
   - Future migrations will be authored via `alembic revision --autogenerate` after SQLModel changes.

## Key Tasks
- [x] Capture target requirements (this document).
- [ ] Scaffold Alembic config tied to FastAPI settings.
- [ ] Generate baseline migration matching current SQLModel models.
- [ ] Update README/docs with migration commands for dev/prod workflows.

This roadmap keeps local developer ergonomics intact while unlocking reliable releases on PostgreSQL-backed environments.