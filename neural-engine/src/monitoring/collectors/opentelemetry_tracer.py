"""
OpenTelemetry distributed tracing for neural processing
"""

import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

logger = logging.getLogger(__name__)


class NeuralTracer:
    """OpenTelemetry tracer for neural processing operations"""

    def __init__(
        self,
        service_name: str = "neural-engine",
        jaeger_endpoint: str = "localhost:6831",
    ):
        """
        Initialize OpenTelemetry tracer

        Args:
            service_name: Name of the service
            jaeger_endpoint: Jaeger agent endpoint
        """
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint

        # Create resource
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.namespace": "neurascale",
                "service.version": "1.0.0",
            }
        )

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_endpoint.split(":")[0],
            agent_port=int(jaeger_endpoint.split(":")[1]),
            udp_split_oversized_batches=True,
        )

        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Get tracer
        self.tracer = trace.get_tracer(__name__)

        # Auto-instrument libraries
        self._setup_auto_instrumentation()

        logger.info(f"OpenTelemetry tracer initialized for {service_name}")

    def _setup_auto_instrumentation(self) -> None:
        """Setup automatic instrumentation for common libraries"""
        try:
            # Instrument HTTP requests
            RequestsInstrumentor().instrument()

            # Instrument SQLAlchemy if available
            try:
                SQLAlchemyInstrumentor().instrument()
            except Exception:
                pass

            # Instrument Redis if available
            try:
                RedisInstrumentor().instrument()
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Failed to setup auto-instrumentation: {e}")

    @contextmanager
    def trace_neural_processing(self, session_id: str):
        """
        Context manager for tracing neural processing operations

        Args:
            session_id: Neural processing session ID
        """
        with self.tracer.start_as_current_span(
            "neural_processing",
            attributes={"session.id": session_id, "processing.type": "neural"},
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def trace_signal_processing(self, device_id: str, sample_count: int):
        """
        Trace signal processing operations

        Args:
            device_id: Device identifier
            sample_count: Number of samples being processed
        """
        with self.tracer.start_as_current_span(
            "signal_processing",
            attributes={
                "device.id": device_id,
                "signal.sample_count": sample_count,
                "processing.stage": "signal",
            },
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def trace_feature_extraction(self, data_shape: tuple):
        """
        Trace feature extraction operations

        Args:
            data_shape: Shape of data being processed
        """
        with self.tracer.start_as_current_span(
            "feature_extraction",
            attributes={"data.shape": str(data_shape), "processing.stage": "features"},
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def trace_model_inference(self, model_id: str, input_shape: tuple):
        """
        Trace model inference operations

        Args:
            model_id: Model identifier
            input_shape: Shape of model input
        """
        with self.tracer.start_as_current_span(
            "model_inference",
            attributes={
                "model.id": model_id,
                "model.input_shape": str(input_shape),
                "processing.stage": "inference",
            },
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def trace_device_operation(self, device_id: str, operation: str):
        """
        Trace device-specific operations

        Args:
            device_id: Device identifier
            operation: Operation being performed
        """
        with self.tracer.start_as_current_span(
            f"device_{operation}",
            attributes={"device.id": device_id, "device.operation": operation},
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @contextmanager
    def trace_database_operation(self, operation: str, table: str):
        """
        Trace database operations

        Args:
            operation: Database operation (select, insert, update, delete)
            table: Table being accessed
        """
        with self.tracer.start_as_current_span(
            f"db_{operation}",
            attributes={
                "db.operation": operation,
                "db.table": table,
                "db.system": "postgresql",
            },
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    def trace_function(self, name: Optional[str] = None):
        """
        Decorator for tracing function execution

        Args:
            name: Optional custom span name
        """

        def decorator(func: Callable) -> Callable:
            span_name = name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    span_name,
                    attributes={
                        "function.module": func.__module__,
                        "function.name": func.__name__,
                    },
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    span_name,
                    attributes={
                        "function.module": func.__module__,
                        "function.name": func.__name__,
                        "function.async": True,
                    },
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            # Return appropriate wrapper based on function type
            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper

        return decorator

    def add_span_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Add an event to the current span

        Args:
            name: Event name
            attributes: Event attributes
        """
        span = trace.get_current_span()
        if span:
            span.add_event(name, attributes=attributes or {})

    def set_span_attribute(self, key: str, value: Any):
        """
        Set attribute on current span

        Args:
            key: Attribute key
            value: Attribute value
        """
        span = trace.get_current_span()
        if span:
            span.set_attribute(key, value)

    def record_neural_metrics(self, metrics: Dict[str, float]):
        """
        Record neural processing metrics in current span

        Args:
            metrics: Neural processing metrics
        """
        span = trace.get_current_span()
        if span:
            for key, value in metrics.items():
                span.set_attribute(f"neural.{key}", value)

    def record_device_metrics(self, device_id: str, metrics: Dict[str, float]):
        """
        Record device metrics in current span

        Args:
            device_id: Device identifier
            metrics: Device performance metrics
        """
        span = trace.get_current_span()
        if span:
            span.set_attribute("device.id", device_id)
            for key, value in metrics.items():
                span.set_attribute(f"device.{key}", value)

    def create_span_link(
        self, context: trace.SpanContext, attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Create a link to another span

        Args:
            context: Span context to link to
            attributes: Link attributes
        """
        # This would be used for linking related operations
        # Implementation depends on specific use case
        pass


# Convenience decorators
def trace_neural_processing(tracer: Optional[NeuralTracer] = None):
    """Decorator for tracing neural processing functions"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _tracer = tracer or NeuralTracer()
            session_id = kwargs.get("session_id", "unknown")

            with _tracer.trace_neural_processing(session_id):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _tracer = tracer or NeuralTracer()
            session_id = kwargs.get("session_id", "unknown")

            with _tracer.trace_neural_processing(session_id):
                return await func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator
