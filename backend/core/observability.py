from __future__ import annotations

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

from backend.config.settings import Settings

logger = logging.getLogger(__name__)


def setup_metrics(app: FastAPI, settings: Settings) -> Optional[Instrumentator]:
    if not settings.metrics_enabled:
        return None

    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers={settings.metrics_endpoint},
    )
    instrumentator.instrument(app).expose(
        app,
        include_in_schema=False,
        should_gzip=True,
        endpoint=settings.metrics_endpoint,
    )
    logger.info("Prometheus metrics enabled at %s", settings.metrics_endpoint)
    return instrumentator


def setup_tracing(app: FastAPI, settings: Settings) -> Optional[TracerProvider]:
    if not settings.otel_exporter_endpoint:
        return None

    resource = Resource.create({"service.name": settings.otel_service_name})
    tracer_provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_endpoint,
        headers=settings.otel_headers_dict,
        insecure=settings.otel_exporter_insecure,
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry tracing enabled -> %s", settings.otel_exporter_endpoint)
    return tracer_provider
