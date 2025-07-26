"""OpenTelemetry distributed tracing for NeuraScale Neural Engine.

This module implements distributed tracing to track neural processing
workflows across multiple services and components.
"""

import time
import functools
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
import logging
import asyncio
from contextlib import asynccontextmanager, contextmanager

# OpenTelemetry imports (these would be added to requirements)
try:
    from opentelemetry import trace, context, propagate
    from opentelemetry.trace import Status, StatusCode, SpanKind
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.propagators.b3 import B3MultiFormat

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TraceConfig:
    """Configuration for OpenTelemetry tracing."""

    service_name: str = "neurascale-neural-engine"
    service_version: str = "1.0.0"
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    sampling_ratio: float = 1.0  # Sample all traces initially
    batch_export_timeout: int = 30000  # milliseconds
    max_export_batch_size: int = 512


class NeuralTracer:
    """OpenTelemetry tracer for neural processing workflows."""

    def __init__(self, config: TraceConfig):
        """Initialize neural tracer.

        Args:
            config: Tracing configuration
        """
        self.config = config
        self.tracer = None
        self.provider = None
        self.processor = None
        self.exporter = None

        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available, tracing disabled")
            return

        try:
            self._setup_tracing()
            logger.info("NeuralTracer initialized with OpenTelemetry")
        except Exception as e:
            logger.error(f"Failed to initialize tracer: {str(e)}")

    def _setup_tracing(self) -> None:
        """Set up OpenTelemetry tracing components."""
        # Create resource
        resource = Resource.create(
            {
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
                "service.namespace": "neurascale",
            }
        )

        # Create tracer provider
        self.provider = TracerProvider(resource=resource)

        # Create Jaeger exporter
        self.exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
            collector_endpoint=self.config.jaeger_endpoint,
        )

        # Create span processor
        self.processor = BatchSpanProcessor(
            self.exporter,
            max_export_batch_size=self.config.max_export_batch_size,
            export_timeout_millis=self.config.batch_export_timeout,
        )

        # Add processor to provider
        self.provider.add_span_processor(self.processor)

        # Set global tracer provider
        trace.set_tracer_provider(self.provider)

        # Set up propagation
        propagate.set_global_textmap(B3MultiFormat())

        # Get tracer
        self.tracer = trace.get_tracer(
            __name__,
            version=self.config.service_version,
        )

    async def start(self) -> bool:
        """Start the tracer.

        Returns:
            True if started successfully
        """
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available")
            return False

        try:
            # Tracer is already set up in __init__
            logger.info("NeuralTracer started")
            return True
        except Exception as e:
            logger.error(f"Failed to start tracer: {str(e)}")
            return False

    async def stop(self) -> None:
        """Stop the tracer and flush remaining spans."""
        if not OPENTELEMETRY_AVAILABLE or not self.provider:
            return

        try:
            # Shutdown the provider to flush remaining spans
            self.provider.shutdown()
            logger.info("NeuralTracer stopped")
        except Exception as e:
            logger.error(f"Failed to stop tracer: {str(e)}")

    @contextmanager
    def trace_neural_processing(
        self,
        operation_name: str,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        **kwargs,
    ):
        """Context manager for tracing neural processing operations.

        Args:
            operation_name: Name of the operation being traced
            session_id: Optional session identifier
            device_id: Optional device identifier
            **kwargs: Additional span attributes
        """
        if not self.tracer:
            yield None
            return

        # Create span attributes
        attributes = {
            "neural.operation": operation_name,
            "neural.timestamp": datetime.utcnow().isoformat(),
        }

        if session_id:
            attributes["neural.session_id"] = session_id
        if device_id:
            attributes["neural.device_id"] = device_id

        # Add custom attributes
        for key, value in kwargs.items():
            attributes[f"neural.{key}"] = str(value)

        # Create and start span
        with self.tracer.start_as_current_span(
            operation_name, kind=SpanKind.INTERNAL, attributes=attributes
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    @asynccontextmanager
    async def trace_async_neural_processing(
        self,
        operation_name: str,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        **kwargs,
    ):
        """Async context manager for tracing neural processing operations.

        Args:
            operation_name: Name of the operation being traced
            session_id: Optional session identifier
            device_id: Optional device identifier
            **kwargs: Additional span attributes
        """
        if not self.tracer:
            yield None
            return

        # Create span attributes
        attributes = {
            "neural.operation": operation_name,
            "neural.timestamp": datetime.utcnow().isoformat(),
        }

        if session_id:
            attributes["neural.session_id"] = session_id
        if device_id:
            attributes["neural.device_id"] = device_id

        # Add custom attributes
        for key, value in kwargs.items():
            attributes[f"neural.{key}"] = str(value)

        # Create and start span
        with self.tracer.start_as_current_span(
            operation_name, kind=SpanKind.INTERNAL, attributes=attributes
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    def trace_signal_processing(self, session_id: str, device_id: str):
        """Trace signal processing workflow.

        Args:
            session_id: Processing session identifier
            device_id: Device identifier
        """
        return self.trace_neural_processing(
            "signal_processing",
            session_id=session_id,
            device_id=device_id,
            component="signal_processor",
        )

    def trace_feature_extraction(
        self, session_id: str, feature_count: Optional[int] = None
    ):
        """Trace feature extraction workflow.

        Args:
            session_id: Processing session identifier
            feature_count: Number of features extracted
        """
        kwargs = {"component": "feature_extractor"}
        if feature_count is not None:
            kwargs["feature_count"] = feature_count

        return self.trace_neural_processing(
            "feature_extraction", session_id=session_id, **kwargs
        )

    def trace_model_inference(
        self, session_id: str, model_id: str, input_size: Optional[int] = None
    ):
        """Trace model inference workflow.

        Args:
            session_id: Processing session identifier
            model_id: Model identifier
            input_size: Size of input data
        """
        kwargs = {
            "component": "model_inference",
            "model_id": model_id,
        }
        if input_size is not None:
            kwargs["input_size"] = input_size

        return self.trace_neural_processing(
            "model_inference", session_id=session_id, **kwargs
        )

    def trace_device_operation(self, device_id: str, operation: str):
        """Trace device operations.

        Args:
            device_id: Device identifier
            operation: Type of operation (connect, disconnect, data_read, etc.)
        """
        return self.trace_neural_processing(
            f"device_{operation}",
            device_id=device_id,
            component="device_manager",
            operation_type=operation,
        )

    def trace_api_request(
        self, method: str, endpoint: str, user_id: Optional[str] = None
    ):
        """Trace API requests.

        Args:
            method: HTTP method
            endpoint: API endpoint
            user_id: Optional user identifier
        """
        kwargs = {
            "component": "api",
            "http_method": method,
            "http_endpoint": endpoint,
        }
        if user_id:
            kwargs["user_id"] = user_id

        return self.trace_neural_processing(
            f"api_{method.lower()}_{endpoint.replace('/', '_')}", **kwargs
        )

    def trace_security_operation(self, operation: str, user_id: Optional[str] = None):
        """Trace security operations.

        Args:
            operation: Security operation (auth, encrypt, decrypt, etc.)
            user_id: Optional user identifier
        """
        kwargs = {
            "component": "security",
            "security_operation": operation,
        }
        if user_id:
            kwargs["user_id"] = user_id

        return self.trace_neural_processing(f"security_{operation}", **kwargs)

    def trace_ledger_operation(self, operation: str, event_type: Optional[str] = None):
        """Trace Neural Ledger operations.

        Args:
            operation: Ledger operation (write, read, query, etc.)
            event_type: Optional event type
        """
        kwargs = {
            "component": "neural_ledger",
            "ledger_operation": operation,
        }
        if event_type:
            kwargs["event_type"] = event_type

        return self.trace_neural_processing(f"ledger_{operation}", **kwargs)

    def add_span_event(
        self, name: str, attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an event to the current span.

        Args:
            name: Event name
            attributes: Optional event attributes
        """
        if not self.tracer:
            return

        try:
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.add_event(name, attributes or {})
        except Exception as e:
            logger.debug(f"Failed to add span event: {str(e)}")

    def set_span_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the current span.

        Args:
            key: Attribute key
            value: Attribute value
        """
        if not self.tracer:
            return

        try:
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_attribute(key, str(value))
        except Exception as e:
            logger.debug(f"Failed to set span attribute: {str(e)}")

    def get_trace_context(self) -> Dict[str, str]:
        """Get the current trace context for propagation.

        Returns:
            Dictionary containing trace context headers
        """
        if not self.tracer:
            return {}

        try:
            # Create carrier for context propagation
            carrier = {}
            propagate.inject(carrier)
            return carrier
        except Exception as e:
            logger.debug(f"Failed to get trace context: {str(e)}")
            return {}

    def set_trace_context(self, context_headers: Dict[str, str]) -> None:
        """Set trace context from headers.

        Args:
            context_headers: Dictionary containing trace context headers
        """
        if not self.tracer or not context_headers:
            return

        try:
            # Extract context and set as current
            ctx = propagate.extract(context_headers)
            context.attach(ctx)
        except Exception as e:
            logger.debug(f"Failed to set trace context: {str(e)}")

    def get_tracer_stats(self) -> Dict[str, Any]:
        """Get tracer statistics.

        Returns:
            Tracer statistics
        """
        stats = {
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "tracer_initialized": self.tracer is not None,
            "service_name": self.config.service_name,
            "jaeger_endpoint": self.config.jaeger_endpoint,
        }

        if OPENTELEMETRY_AVAILABLE and self.provider:
            try:
                # Get processor stats if available
                if hasattr(self.processor, "get_stats"):
                    stats["processor_stats"] = self.processor.get_stats()
            except Exception as e:
                stats["stats_error"] = str(e)

        return stats


# Decorators for automatic tracing


def trace_neural_processing(
    operation_name: Optional[str] = None,
    session_id_param: Optional[str] = None,
    device_id_param: Optional[str] = None,
    **trace_kwargs,
):
    """Decorator for tracing neural processing functions.

    Args:
        operation_name: Optional operation name (defaults to function name)
        session_id_param: Parameter name containing session ID
        device_id_param: Parameter name containing device ID
        **trace_kwargs: Additional trace attributes
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get global tracer instance (this would be injected/configured)
            tracer = getattr(wrapper, "_neural_tracer", None)
            if not tracer:
                return func(*args, **kwargs)

            # Extract parameters
            op_name = operation_name or func.__name__
            session_id = None
            device_id = None

            if session_id_param and session_id_param in kwargs:
                session_id = kwargs[session_id_param]
            if device_id_param and device_id_param in kwargs:
                device_id = kwargs[device_id_param]

            # Create trace context
            with tracer.trace_neural_processing(
                op_name, session_id=session_id, device_id=device_id, **trace_kwargs
            ) as span:
                # Add function metadata
                if span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                return func(*args, **kwargs)

        return wrapper

    return decorator


def trace_async_neural_processing(
    operation_name: Optional[str] = None,
    session_id_param: Optional[str] = None,
    device_id_param: Optional[str] = None,
    **trace_kwargs,
):
    """Decorator for tracing async neural processing functions.

    Args:
        operation_name: Optional operation name (defaults to function name)
        session_id_param: Parameter name containing session ID
        device_id_param: Parameter name containing device ID
        **trace_kwargs: Additional trace attributes
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get global tracer instance (this would be injected/configured)
            tracer = getattr(wrapper, "_neural_tracer", None)
            if not tracer:
                return await func(*args, **kwargs)

            # Extract parameters
            op_name = operation_name or func.__name__
            session_id = None
            device_id = None

            if session_id_param and session_id_param in kwargs:
                session_id = kwargs[session_id_param]
            if device_id_param and device_id_param in kwargs:
                device_id = kwargs[device_id_param]

            # Create trace context
            async with tracer.trace_async_neural_processing(
                op_name, session_id=session_id, device_id=device_id, **trace_kwargs
            ) as span:
                # Add function metadata
                if span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Factory function
def create_neural_tracer(config: Optional[TraceConfig] = None) -> NeuralTracer:
    """Create a neural tracer instance.

    Args:
        config: Optional trace configuration

    Returns:
        NeuralTracer instance
    """
    if config is None:
        config = TraceConfig()

    return NeuralTracer(config)
