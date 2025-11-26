import logging
from logging.config import dictConfig
from contextvars import ContextVar

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - simple filter
        record.request_id = request_id_ctx_var.get("-")
        return True


def setup_logging(level: str) -> None:
    log_level = (level or "INFO").upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {
                    "()": "backend.core.logging_utils.RequestIdFilter",
                }
            },
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s | request_id=%(request_id)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["request_id"],
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console"],
                    "level": log_level,
                }
            },
        }
    )
