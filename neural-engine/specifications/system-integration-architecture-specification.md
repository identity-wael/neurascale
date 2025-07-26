# System Integration & Architecture Specification

**Version**: 1.0.0
**Created**: 2025-07-26
**Priority**: CRITICAL (Foundation for all phases)
**Duration**: 5 days
**Lead**: Senior Backend Engineer + DevOps Engineer

## Executive Summary

This specification defines the comprehensive system integration architecture for the NeuraScale Neural Engine, providing the communication backbone, orchestration layer, and integration patterns that enable all components to work together as a unified neural management system.

## System Architecture Overview

### **Current State Assessment**

- ✅ **Microservices**: Individual components implemented (ledger, security, processing)
- ✅ **Storage Layer**: Multi-tier storage architecture operational
- ✅ **Basic APIs**: FastAPI endpoints for core functionality
- 🚨 **Missing**: Service mesh, API gateway, event coordination, workflow orchestration

### **Target Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    NeuraScale Neural Management System           │
├─────────────────────────────────────────────────────────────────┤
│  User Experience Layer                                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ Clinical    │ │ Patient     │ │ Admin       │ │ Research    ││
│  │ Dashboard   │ │ Mobile App  │ │ Console     │ │ Portal      ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  API Gateway & Load Balancer (Kong/Istio)                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Authentication │ Rate Limiting │ SSL Termination │ Routing ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Service Mesh & Communication Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │        Event Bus (Kafka/Pub/Sub) + gRPC + REST APIs        ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Layer (Microservices)                           │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │
│  │ Clinical  │ │ Neural    │ │ Device    │ │ ML Model  │        │
│  │ Workflow  │ │ Ledger    │ │ Manager   │ │ Service   │        │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │
│  │ Security  │ │ Signal    │ │ Monitoring│ │ Ingestion │        │
│  │ Service   │ │ Processing│ │ Service   │ │ Pipeline  │        │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐        │
│  │ Neural    │ │ Time      │ │ Meta      │ │ Cloud     │        │
│  │ Ledger    │ │ Series DB │ │ data DB   │ │ Storage   │        │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Core Integration Components

### 1. API Gateway & Traffic Management

```yaml
# Kong API Gateway Configuration
services:
  neural-engine-gateway:
    image: kong:latest
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: neural-engine-db
      KONG_PLUGINS: bundled,jwt,rate-limiting,cors,prometheus
    ports:
      - "8000:8000" # HTTP
      - "8443:8443" # HTTPS
      - "8001:8001" # Admin API

plugins:
  - name: jwt
    config:
      key_claim_name: iss
      secret_is_base64: false

  - name: rate-limiting
    config:
      minute: 1000
      hour: 10000

  - name: cors
    config:
      origins: ["https://neural.neurascale.com"]
      credentials: true

  - name: prometheus
    config:
      per_consumer: true
```

### 2. Event-Driven Architecture

```python
# Event bus implementation
from dataclasses import dataclass
from typing import Dict, Any, List, Callable
import asyncio
from google.cloud import pubsub_v1

@dataclass
class SystemEvent:
    """Standardized system event"""
    event_type: str
    source_service: str
    event_id: str
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None

class EventBus:
    """Central event coordination system"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.event_handlers: Dict[str, List[Callable]] = {}

    async def publish_event(self, event: SystemEvent) -> str:
        """Publish event to appropriate topic"""
        topic_path = self.publisher.topic_path(
            self.project_id, f"neural-events-{event.event_type}"
        )

        message_data = json.dumps(asdict(event)).encode('utf-8')
        future = self.publisher.publish(topic_path, message_data)
        return future.result()

    def subscribe_to_events(self, event_type: str, handler: Callable):
        """Subscribe handler to specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def start_event_processing(self):
        """Start processing events from all subscriptions"""
        for event_type, handlers in self.event_handlers.items():
            subscription_path = self.subscriber.subscription_path(
                self.project_id, f"neural-events-{event_type}-subscription"
            )

            # Pull messages and dispatch to handlers
            def callback(message):
                event_data = json.loads(message.data.decode('utf-8'))
                event = SystemEvent(**event_data)

                for handler in handlers:
                    asyncio.create_task(handler(event))

                message.ack()

            self.subscriber.subscribe(subscription_path, callback=callback)

# Event types for the system
NEURAL_EVENTS = [
    "patient.registered",
    "session.started",
    "session.completed",
    "device.connected",
    "device.disconnected",
    "signal.quality_alert",
    "safety.emergency_stop",
    "model.inference_completed",
    "ledger.event_recorded",
    "security.authentication_failed",
    "system.health_check",
]
```

### 3. Workflow Orchestration

```python
# Temporal workflow for complex processes
from temporalio import workflow, activity
from datetime import timedelta

class ClinicalSessionWorkflow:
    """Orchestrates complete clinical session lifecycle"""

    @workflow.defn
    class ClinicalSessionWorkflow:
        @workflow.run
        async def run(self, session_request: dict) -> dict:
            # Step 1: Validate patient and provider
            validation_result = await workflow.execute_activity(
                validate_session_prerequisites,
                session_request,
                start_to_close_timeout=timedelta(minutes=5)
            )

            if not validation_result['valid']:
                return {'status': 'failed', 'reason': validation_result['reason']}

            # Step 2: Setup devices and calibration
            device_setup = await workflow.execute_activity(
                setup_session_devices,
                session_request['device_config'],
                start_to_close_timeout=timedelta(minutes=10)
            )

            # Step 3: Start neural data collection
            data_collection = await workflow.execute_activity(
                start_neural_data_collection,
                {
                    'session_id': session_request['session_id'],
                    'device_connections': device_setup['connections']
                },
                start_to_close_timeout=timedelta(hours=2)
            )

            # Step 4: Real-time monitoring
            monitoring_task = workflow.create_task(
                monitor_session_safety,
                session_request['session_id']
            )

            # Step 5: Process and analyze data
            analysis_result = await workflow.execute_activity(
                process_session_data,
                data_collection,
                start_to_close_timeout=timedelta(minutes=30)
            )

            # Step 6: Generate clinical report
            report = await workflow.execute_activity(
                generate_clinical_report,
                {
                    'session_id': session_request['session_id'],
                    'analysis': analysis_result
                },
                start_to_close_timeout=timedelta(minutes=15)
            )

            return {
                'status': 'completed',
                'session_id': session_request['session_id'],
                'report': report
            }

@activity.defn
async def validate_session_prerequisites(session_request: dict) -> dict:
    """Validate patient consent, provider availability, device status"""
    # Implementation here
    pass

@activity.defn
async def setup_session_devices(device_config: dict) -> dict:
    """Setup and calibrate BCI devices for session"""
    # Implementation here
    pass

@activity.defn
async def start_neural_data_collection(config: dict) -> dict:
    """Start neural signal collection from devices"""
    # Implementation here
    pass
```

### 4. Service Discovery & Configuration

```python
# Service registry and configuration management
from consul import Consul
from typing import Dict, List, Optional

class ServiceRegistry:
    """Centralized service discovery and health checking"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = Consul(host=consul_host, port=consul_port)

    def register_service(self, service_name: str, service_id: str,
                        address: str, port: int, health_check_url: str) -> bool:
        """Register service with health check"""
        return self.consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=address,
            port=port,
            check=Consul.Check.http(health_check_url, interval="10s")
        )

    def discover_service(self, service_name: str) -> List[Dict]:
        """Discover healthy instances of a service"""
        _, services = self.consul.health.service(service_name, passing=True)
        return [
            {
                'address': service['Service']['Address'],
                'port': service['Service']['Port'],
                'service_id': service['Service']['ID']
            }
            for service in services
        ]

    def get_service_config(self, service_name: str) -> Dict:
        """Get configuration for a service"""
        _, config = self.consul.kv.get(f"config/{service_name}")
        return json.loads(config['Value'].decode()) if config else {}

class ConfigurationManager:
    """Dynamic configuration management"""

    def __init__(self, consul_client: Consul):
        self.consul = consul_client
        self.cached_config = {}
        self.config_callbacks = {}

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with caching"""
        if key not in self.cached_config:
            _, config_data = self.consul.kv.get(key)
            if config_data:
                self.cached_config[key] = json.loads(config_data['Value'].decode())
            else:
                self.cached_config[key] = default

        return self.cached_config[key]

    def watch_config(self, key: str, callback: Callable):
        """Watch for configuration changes"""
        self.config_callbacks[key] = callback
        # Implementation for watching config changes
```

### 5. Circuit Breaker & Resilience

```python
# Circuit breaker pattern for service resilience
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from typing import Any, Callable

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for service resilience"""

    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Service client with circuit breaker
class ResilientServiceClient:
    """HTTP client with circuit breaker and retry logic"""

    def __init__(self, base_url: str, circuit_breaker: CircuitBreaker):
        self.base_url = base_url
        self.circuit_breaker = circuit_breaker
        self.session = aiohttp.ClientSession()

    async def get(self, endpoint: str, **kwargs) -> dict:
        """GET request with circuit breaker"""
        return await self.circuit_breaker.call(
            self._make_request, 'GET', endpoint, **kwargs
        )

    async def post(self, endpoint: str, **kwargs) -> dict:
        """POST request with circuit breaker"""
        return await self.circuit_breaker.call(
            self._make_request, 'POST', endpoint, **kwargs
        )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"

        async with self.session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                raise aiohttp.ClientError(f"HTTP {response.status}")
            return await response.json()
```

## Implementation Plan

### Day 1: API Gateway & Load Balancing

**Tasks:**

- [ ] Deploy Kong API Gateway with PostgreSQL backend
- [ ] Configure SSL termination and domain routing
- [ ] Implement JWT authentication plugin
- [ ] Setup rate limiting and CORS policies
- [ ] Configure service routing rules
- [ ] Add Prometheus metrics collection

### Day 2: Event Bus & Messaging

**Tasks:**

- [ ] Setup Google Pub/Sub topics for system events
- [ ] Implement EventBus class with publish/subscribe
- [ ] Create event schemas for all system events
- [ ] Setup event handlers for each microservice
- [ ] Implement event correlation and causation tracking
- [ ] Add event replay capability for debugging

### Day 3: Service Discovery & Configuration

**Tasks:**

- [ ] Deploy Consul cluster for service discovery
- [ ] Implement ServiceRegistry for health checks
- [ ] Create ConfigurationManager for dynamic config
- [ ] Setup service registration for all microservices
- [ ] Implement configuration watching and updates
- [ ] Add service dependency mapping

### Day 4: Workflow Orchestration

**Tasks:**

- [ ] Deploy Temporal cluster for workflow management
- [ ] Implement ClinicalSessionWorkflow
- [ ] Create workflow activities for each service
- [ ] Setup workflow monitoring and debugging
- [ ] Implement workflow retry and error handling
- [ ] Add workflow versioning and migration

### Day 5: Resilience & Monitoring

**Tasks:**

- [ ] Implement CircuitBreaker pattern for all services
- [ ] Create ResilientServiceClient for HTTP calls
- [ ] Setup distributed tracing with Jaeger
- [ ] Implement health check endpoints for all services
- [ ] Add service dependency health monitoring
- [ ] Create integration test suite for full system

## Integration Patterns

### 1. Request-Response Pattern

```python
# Synchronous service communication
async def get_patient_data(patient_id: str) -> PatientData:
    clinical_client = ResilientServiceClient(
        "http://clinical-service:8080",
        CircuitBreaker(failure_threshold=3)
    )

    patient_data = await clinical_client.get(f"/patients/{patient_id}")
    return PatientData(**patient_data)
```

### 2. Event-Driven Pattern

```python
# Asynchronous event processing
async def handle_session_started(event: SystemEvent):
    """Handle session started event"""
    session_id = event.data['session_id']

    # Start monitoring
    await monitoring_service.start_session_monitoring(session_id)

    # Initialize neural ledger
    await neural_ledger.create_session_entry(session_id)

    # Setup real-time processing
    await signal_processor.setup_session_pipeline(session_id)

event_bus.subscribe_to_events("session.started", handle_session_started)
```

### 3. Workflow Pattern

```python
# Complex business process orchestration
@workflow.defn
class PatientOnboardingWorkflow:
    @workflow.run
    async def run(self, patient_data: dict) -> dict:
        # Step 1: Create patient record
        patient = await workflow.execute_activity(
            create_patient_record, patient_data
        )

        # Step 2: Setup security access
        security_setup = await workflow.execute_activity(
            setup_patient_security, patient['patient_id']
        )

        # Step 3: Initialize treatment plan
        treatment_plan = await workflow.execute_activity(
            create_initial_treatment_plan, patient['patient_id']
        )

        return {
            'patient_id': patient['patient_id'],
            'onboarding_complete': True
        }
```

## Monitoring & Observability

### Distributed Tracing

```python
# Jaeger tracing integration
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_neural_signal")
async def process_neural_signal(signal_data: np.ndarray) -> ProcessedSignal:
    """Process neural signal with distributed tracing"""
    current_span = trace.get_current_span()
    current_span.set_attribute("signal.channels", len(signal_data))
    current_span.set_attribute("signal.samples", signal_data.shape[1])

    # Processing logic here
    with tracer.start_as_current_span("filter_signal") as filter_span:
        filtered_signal = await apply_filters(signal_data)
        filter_span.set_attribute("filter.type", "bandpass")

    with tracer.start_as_current_span("extract_features") as feature_span:
        features = await extract_features(filtered_signal)
        feature_span.set_attribute("features.count", len(features))

    return ProcessedSignal(signal=filtered_signal, features=features)
```

## Security Integration

### Service-to-Service Authentication

```python
# mTLS and JWT for service communication
class SecureServiceClient:
    """Secure communication between services"""

    def __init__(self, service_name: str, cert_path: str, key_path: str):
        self.service_name = service_name
        self.cert_path = cert_path
        self.key_path = key_path
        self.jwt_token = None

    async def authenticate(self) -> str:
        """Get service-to-service JWT token"""
        auth_request = {
            'service_name': self.service_name,
            'scope': 'service-to-service'
        }

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(self.cert_path, self.key_path)

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            async with session.post('/auth/service-token', json=auth_request) as response:
                token_data = await response.json()
                self.jwt_token = token_data['access_token']
                return self.jwt_token

    async def make_request(self, method: str, url: str, **kwargs) -> dict:
        """Make authenticated request to another service"""
        if not self.jwt_token:
            await self.authenticate()

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.jwt_token}"
        kwargs['headers'] = headers

        # Use mTLS for request
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(self.cert_path, self.key_path)

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            async with session.request(method, url, **kwargs) as response:
                return await response.json()
```

## Cost Estimation

### Infrastructure Costs (Monthly)

- **Kong API Gateway**: $200/month (Enterprise features)
- **Consul Cluster**: $150/month (3-node cluster)
- **Temporal Cluster**: $300/month (workflow orchestration)
- **Pub/Sub Messaging**: $100/month (high-volume events)
- **Load Balancers**: $75/month (multi-zone)
- **SSL Certificates**: $50/month (wildcard certs)
- **Total Monthly**: ~$875/month

### Development Resources

- **Senior Backend Engineer**: 3 days
- **DevOps Engineer**: 2 days
- **System Integration Testing**: 2 days
- **Performance Optimization**: 1 day

## Success Criteria

### Integration Success

- [ ] All services discoverable via service registry
- [ ] Event-driven communication operational
- [ ] API Gateway routing all traffic correctly
- [ ] Workflow orchestration handling complex processes
- [ ] Circuit breakers protecting against failures

### Performance Success

- [ ] API response times <100ms (95th percentile)
- [ ] Event processing latency <50ms
- [ ] Service discovery resolution <10ms
- [ ] Workflow orchestration overhead <2%
- [ ] System uptime >99.9%

### Security Success

- [ ] Service-to-service authentication operational
- [ ] mTLS encryption for all internal communication
- [ ] JWT token validation at API gateway
- [ ] Security audit logging for all requests
- [ ] Zero security vulnerabilities in integration layer

---

**Dependencies**: All microservices must implement standard interfaces
**Review Date**: Integration completion + comprehensive testing
**Critical Path**: Required before user interface development
