"""
Comprehensive health monitoring for Neural Engine services
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp
from sqlalchemy import text

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Individual service health status"""

    service_name: str
    status: HealthStatus
    latency_ms: float
    details: Optional[str] = None
    last_check: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class HealthReport:
    """Comprehensive health report"""

    overall_status: HealthStatus
    services: Dict[str, ServiceHealth]
    timestamp: datetime
    issues: List[str]
    recommendations: List[str]


class HealthChecker:
    """Comprehensive health monitoring for all services"""

    def __init__(
        self,
        services: List[str],
        check_interval_seconds: int = 30,
        timeout_seconds: int = 5,
    ):
        """
        Initialize health checker

        Args:
            services: List of services to monitor
            check_interval_seconds: Health check interval
            timeout_seconds: Health check timeout
        """
        self.services = services
        self.check_interval = check_interval_seconds
        self.timeout = timeout_seconds

        # Service health cache
        self._service_health: Dict[str, ServiceHealth] = {}
        self.last_check_time: Optional[datetime] = None

        # Database connection (to be injected)
        self.db_engine = None

        # Redis connection (to be injected)
        self.redis_client = None

        # Service endpoints
        self.service_endpoints = {
            "neural-processing": "http://localhost:8000/health",
            "device-management": "http://localhost:8001/health",
            "api": "http://localhost:8080/health",
            "cache": "redis://localhost:6379",
            "database": "postgresql://localhost:5432",
        }

        logger.info(f"Health checker initialized for services: {services}")

    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """
        Check health of individual service

        Args:
            service_name: Name of service to check

        Returns:
            Service health status
        """
        start_time = datetime.now()

        try:
            if service_name == "neural-processing":
                health = await self._check_neural_processing_health()
            elif service_name == "device-management":
                health = await self._check_device_management_health()
            elif service_name == "database":
                health = await self._check_database_health()
            elif service_name == "cache":
                health = await self._check_cache_health()
            elif service_name == "api":
                health = await self._check_api_health()
            else:
                health = await self._check_generic_http_health(service_name)

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            health.latency_ms = latency_ms
            health.last_check = datetime.now()

            # Cache result
            self._service_health[service_name] = health

            return health

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")

            health = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
                last_check=datetime.now(),
            )

            self._service_health[service_name] = health
            return health

    async def _check_neural_processing_health(self) -> ServiceHealth:
        """Check neural processing service health"""
        try:
            # Check if neural processing is responsive
            endpoint = self.service_endpoints.get(
                "neural-processing", "http://localhost:8000/health"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check processing metrics
                        if data.get("processing_active", False):
                            return ServiceHealth(
                                service_name="neural-processing",
                                status=HealthStatus.HEALTHY,
                                latency_ms=0,
                                details="Neural processing operational",
                            )
                        else:
                            return ServiceHealth(
                                service_name="neural-processing",
                                status=HealthStatus.DEGRADED,
                                latency_ms=0,
                                details="Neural processing idle",
                            )
                    else:
                        return ServiceHealth(
                            service_name="neural-processing",
                            status=HealthStatus.UNHEALTHY,
                            latency_ms=0,
                            error=f"HTTP {response.status}",
                        )

        except asyncio.TimeoutError:
            return ServiceHealth(
                service_name="neural-processing",
                status=HealthStatus.UNHEALTHY,
                latency_ms=self.timeout * 1000,
                error="Timeout",
            )
        except Exception as e:
            return ServiceHealth(
                service_name="neural-processing",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def _check_device_management_health(self) -> ServiceHealth:
        """Check device management service health"""
        try:
            endpoint = self.service_endpoints.get(
                "device-management", "http://localhost:8001/health"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        active_devices = data.get("active_devices", 0)
                        if active_devices > 0:
                            return ServiceHealth(
                                service_name="device-management",
                                status=HealthStatus.HEALTHY,
                                latency_ms=0,
                                details=f"{active_devices} devices connected",
                            )
                        else:
                            return ServiceHealth(
                                service_name="device-management",
                                status=HealthStatus.DEGRADED,
                                latency_ms=0,
                                details="No active devices",
                            )
                    else:
                        return ServiceHealth(
                            service_name="device-management",
                            status=HealthStatus.UNHEALTHY,
                            latency_ms=0,
                            error=f"HTTP {response.status}",
                        )

        except Exception as e:
            return ServiceHealth(
                service_name="device-management",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def _check_database_health(self) -> ServiceHealth:
        """Check database health"""
        if not self.db_engine:
            return ServiceHealth(
                service_name="database",
                status=HealthStatus.UNKNOWN,
                latency_ms=0,
                error="Database engine not configured",
            )

        try:
            # Execute simple query
            async with self.db_engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()

            # Check connection pool
            pool_status = self.db_engine.pool.status()

            if "overflow" in pool_status and pool_status["overflow"] > 5:
                return ServiceHealth(
                    service_name="database",
                    status=HealthStatus.DEGRADED,
                    latency_ms=0,
                    details=f"High connection pool usage: {pool_status}",
                )
            else:
                return ServiceHealth(
                    service_name="database",
                    status=HealthStatus.HEALTHY,
                    latency_ms=0,
                    details="Database responsive",
                )

        except Exception as e:
            return ServiceHealth(
                service_name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def _check_cache_health(self) -> ServiceHealth:
        """Check cache (Redis) health"""
        if not self.redis_client:
            return ServiceHealth(
                service_name="cache",
                status=HealthStatus.UNKNOWN,
                latency_ms=0,
                error="Redis client not configured",
            )

        try:
            # Ping Redis
            if self.redis_client.ping():
                # Check memory usage
                info = self.redis_client.info("memory")
                used_memory_mb = info.get("used_memory", 0) / 1024 / 1024
                max_memory_mb = info.get("maxmemory", 0) / 1024 / 1024

                if max_memory_mb > 0:
                    usage_percent = (used_memory_mb / max_memory_mb) * 100
                    if usage_percent > 90:
                        return ServiceHealth(
                            service_name="cache",
                            status=HealthStatus.DEGRADED,
                            latency_ms=0,
                            details=f"High memory usage: {usage_percent:.1f}%",
                        )

                return ServiceHealth(
                    service_name="cache",
                    status=HealthStatus.HEALTHY,
                    latency_ms=0,
                    details=f"Memory usage: {used_memory_mb:.1f}MB",
                )
            else:
                return ServiceHealth(
                    service_name="cache",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=0,
                    error="Redis ping failed",
                )

        except Exception as e:
            return ServiceHealth(
                service_name="cache",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def _check_api_health(self) -> ServiceHealth:
        """Check API service health"""
        try:
            endpoint = self.service_endpoints.get("api", "http://localhost:8080/health")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        return ServiceHealth(
                            service_name="api",
                            status=HealthStatus.HEALTHY,
                            latency_ms=0,
                            details="API responsive",
                        )
                    else:
                        return ServiceHealth(
                            service_name="api",
                            status=HealthStatus.UNHEALTHY,
                            latency_ms=0,
                            error=f"HTTP {response.status}",
                        )

        except Exception as e:
            return ServiceHealth(
                service_name="api",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def _check_generic_http_health(self, service_name: str) -> ServiceHealth:
        """Check generic HTTP service health"""
        endpoint = self.service_endpoints.get(service_name)
        if not endpoint:
            return ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                latency_ms=0,
                error="No endpoint configured",
            )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        return ServiceHealth(
                            service_name=service_name,
                            status=HealthStatus.HEALTHY,
                            latency_ms=0,
                            details="Service responsive",
                        )
                    else:
                        return ServiceHealth(
                            service_name=service_name,
                            status=HealthStatus.UNHEALTHY,
                            latency_ms=0,
                            error=f"HTTP {response.status}",
                        )

        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                error=str(e),
            )

    async def check_external_dependencies(self) -> List[ServiceHealth]:
        """Check health of external dependencies"""
        dependencies = []

        # Check external services like S3, external APIs, etc.
        # This is a placeholder for actual implementation

        return dependencies

    async def generate_health_report(self) -> HealthReport:
        """
        Generate comprehensive health report

        Returns:
            Complete health report
        """
        # Check all services
        service_checks = await asyncio.gather(
            *[self.check_service_health(service) for service in self.services]
        )

        # Build service health map
        services = {check.service_name: check for check in service_checks}

        # Determine overall status
        unhealthy_count = sum(
            1 for s in services.values() if s.status == HealthStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for s in services.values() if s.status == HealthStatus.DEGRADED
        )

        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Identify issues
        issues = []
        for service_name, health in services.items():
            if health.status == HealthStatus.UNHEALTHY:
                issues.append(
                    f"{service_name} is unhealthy: {health.error or 'Unknown error'}"
                )
            elif health.status == HealthStatus.DEGRADED:
                issues.append(
                    f"{service_name} is degraded: {health.details or 'Unknown issue'}"
                )

        # Generate recommendations
        recommendations = self._generate_health_recommendations(services)

        # Update last check time
        self.last_check_time = datetime.now()

        return HealthReport(
            overall_status=overall_status,
            services={
                name: {
                    "status": health.status.value,
                    "latency_ms": health.latency_ms,
                    "details": health.details,
                    "error": health.error,
                    "last_check": (
                        health.last_check.isoformat() if health.last_check else None
                    ),
                }
                for name, health in services.items()
            },
            timestamp=datetime.now(),
            issues=issues,
            recommendations=recommendations,
        )

    def _generate_health_recommendations(
        self, services: Dict[str, ServiceHealth]
    ) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []

        # Check for service-specific issues
        if (
            services.get("database")
            and services["database"].status == HealthStatus.DEGRADED
        ):
            recommendations.append(
                "Database showing high connection pool usage - consider scaling connections"
            )

        if services.get("cache") and services["cache"].status == HealthStatus.DEGRADED:
            recommendations.append(
                "Cache memory usage high - consider increasing cache size or implementing eviction"
            )

        if (
            services.get("neural-processing")
            and services["neural-processing"].status == HealthStatus.UNHEALTHY
        ):
            recommendations.append(
                "Neural processing service down - check service logs and restart if necessary"
            )

        # Check for patterns
        unhealthy_services = [
            name
            for name, health in services.items()
            if health.status == HealthStatus.UNHEALTHY
        ]

        if len(unhealthy_services) > len(services) / 2:
            recommendations.append(
                "Multiple services unhealthy - check system resources and network connectivity"
            )

        return recommendations

    def get_service_uptime(self, service_name: str) -> Optional[timedelta]:
        """
        Get service uptime based on health checks

        Args:
            service_name: Service to check

        Returns:
            Uptime duration or None
        """
        if service_name not in self._service_health:
            return None

        health = self._service_health[service_name]
        if health.last_check and health.status == HealthStatus.HEALTHY:
            # This is simplified - in production you'd track state changes
            return datetime.now() - health.last_check

        return None
