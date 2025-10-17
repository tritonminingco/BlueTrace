"""OpenTelemetry configuration."""

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.core.config import settings


def setup_telemetry() -> None:
    """Configure OpenTelemetry tracing."""
    # Create resource with service name
    resource = Resource(attributes={"service.name": settings.OTEL_SERVICE_NAME})

    # Set up tracer provider
    provider = TracerProvider(resource=resource)

    # Configure exporter based on settings
    if settings.OTEL_EXPORTER_TYPE == "console":
        exporter = ConsoleSpanExporter()
    else:
        # Could add OTLP exporter here
        exporter = ConsoleSpanExporter()

    # Add span processor
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Set as global tracer provider
    trace.set_tracer_provider(provider)


def instrument_app(app: any) -> None:
    """Instrument FastAPI app with OpenTelemetry."""
    FastAPIInstrumentor.instrument_app(app)
