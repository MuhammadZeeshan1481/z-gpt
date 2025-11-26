import time
from pathlib import Path
from typing import Iterator

from prometheus_client import REGISTRY, Counter, Histogram
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import event

from backend.config.settings import get_settings
from backend.db import models  # noqa: F401 - ensure models registered

settings = get_settings()

if "zgpt_db_query_duration_seconds" in REGISTRY._names_to_collectors:  # type: ignore[attr-defined]
    DB_QUERY_LATENCY = REGISTRY._names_to_collectors["zgpt_db_query_duration_seconds"]  # type: ignore[index]
else:
    DB_QUERY_LATENCY = Histogram(
        "zgpt_db_query_duration_seconds",
        "Time spent executing SQL statements",
        labelnames=("operation",),
    )

if "zgpt_db_query_errors_total" in REGISTRY._names_to_collectors:  # type: ignore[attr-defined]
    DB_QUERY_ERRORS = REGISTRY._names_to_collectors["zgpt_db_query_errors_total"]  # type: ignore[index]
else:
    DB_QUERY_ERRORS = Counter(
        "zgpt_db_query_errors_total",
        "Total database query errors",
    )

def _build_engine():
    url = settings.db_url
    connect_args = {}
    if url.startswith("sqlite"):
        path = url.replace("sqlite:///", "", 1)
        if path and not path.startswith(":"):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        connect_args = {"check_same_thread": False}
    return create_engine(url, echo=False, connect_args=connect_args)


def create_database() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


engine = _build_engine()


if settings.metrics_enabled:

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore[override]
        conn.info.setdefault("_query_start_time", []).append(time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore[override]
        starts = conn.info.get("_query_start_time")
        if not starts:
            return
        start = starts.pop(-1)
        duration = time.perf_counter() - start
        operation = "UNKNOWN"
        if statement:
            operation = statement.strip().split(" ", 1)[0].upper()
        DB_QUERY_LATENCY.labels(operation=operation).observe(duration)

    @event.listens_for(engine, "handle_error")
    def handle_error(context):  # type: ignore[override]
        DB_QUERY_ERRORS.inc()
