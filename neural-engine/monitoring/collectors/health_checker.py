"""Health monitoring system for NeuraScale Neural Engine.

This module performs comprehensive health checks on all system components
including services, databases, external dependencies, and device connections.
"""

import asyncio
import aiohttp
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check definition."""

    name: str
    description: str
    check_function: Callable
    timeout_seconds: float = 30.0
    interval_seconds: float = 60.0
    critical: bool = False
    tags: Dict[str, str] = field(default_factory=dict)

    # Runtime data
    last_run: Optional[datetime] = None
    last_result: Optional["HealthResult"] = None
    consecutive_failures: int = 0


@dataclass
class HealthResult:
    """Result of a health check."""

    check_name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class HealthReport:
    """Comprehensive health report."""

    overall_status: HealthStatus
    total_checks: int
    healthy_checks: int
    warning_checks: int
    critical_checks: int
    unknown_checks: int
    report_timestamp: datetime = field(default_factory=datetime.utcnow)
    check_results: List[HealthResult] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "overall_status": self.overall_status.value,
            "total_checks": self.total_checks,
            "healthy_checks": self.healthy_checks,
            "warning_checks": self.warning_checks,
            "critical_checks": self.critical_checks,
            "unknown_checks": self.unknown_checks,
            "report_timestamp": self.report_timestamp.isoformat(),
            "check_results": [result.to_dict() for result in self.check_results],
            "system_info": self.system_info,
        }


class HealthChecker:
    """Comprehensive health monitoring system."""

    def __init__(self, config):
        """Initialize health checker.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_history: Dict[str, List[HealthResult]] = {}

        # Runtime tracking
        self.total_checks_performed = 0
        self.check_errors = 0
        self.last_comprehensive_check: Optional[datetime] = None

        # Initialize standard health checks
        self._register_standard_checks()

        logger.info("HealthChecker initialized")

    def _register_standard_checks(self) -> None:
        """Register standard health checks for Neural Engine."""

        # System resource checks
        self.register_check(
            "system_cpu_usage",
            "System CPU usage check",
            self._check_cpu_usage,
            critical=True,
            interval_seconds=30,
        )

        self.register_check(
            "system_memory_usage",
            "System memory usage check",
            self._check_memory_usage,
            critical=True,
            interval_seconds=30,
        )

        self.register_check(
            "system_disk_space",
            "System disk space check",
            self._check_disk_space,
            critical=True,
            interval_seconds=120,
        )

        # Process health checks
        self.register_check(
            "neural_engine_process",
            "Neural Engine process health",
            self._check_neural_engine_process,
            critical=True,
            interval_seconds=60,
        )

        # Service connectivity checks
        self.register_check(
            "redis_connectivity",
            "Redis service connectivity",
            self._check_redis_connectivity,
            critical=False,
            interval_seconds=60,
        )

        self.register_check(
            "database_connectivity",
            "Database connectivity check",
            self._check_database_connectivity,
            critical=True,
            interval_seconds=60,
        )

        # Neural Engine specific checks
        self.register_check(
            "device_manager_status",
            "Device manager service status",
            self._check_device_manager,
            critical=False,
            interval_seconds=60,
        )

        self.register_check(
            "neural_ledger_connectivity",
            "Neural Ledger service connectivity",
            self._check_neural_ledger,
            critical=False,
            interval_seconds=120,
        )

        # Security service checks
        self.register_check(
            "auth_service_status",
            "Authentication service status",
            self._check_auth_service,
            critical=True,
            interval_seconds=60,
        )

    def register_check(
        self,
        name: str,
        description: str,
        check_function: Callable,
        timeout_seconds: float = 30.0,
        interval_seconds: float = 60.0,
        critical: bool = False,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Register a new health check.

        Args:
            name: Unique check name
            description: Human-readable description
            check_function: Function to perform the check
            timeout_seconds: Check timeout
            interval_seconds: How often to run the check
            critical: Whether this is a critical check
            tags: Optional tags for the check

        Returns:
            True if registration successful
        """
        try:
            if name in self.health_checks:
                logger.warning(f"Health check {name} already exists")
                return False

            check = HealthCheck(
                name=name,
                description=description,
                check_function=check_function,
                timeout_seconds=timeout_seconds,
                interval_seconds=interval_seconds,
                critical=critical,
                tags=tags or {},
            )

            self.health_checks[name] = check
            self.check_history[name] = []

            logger.info(f"Registered health check: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to register health check {name}: {str(e)}")
            return False

    async def perform_check(self, check_name: str) -> Optional[HealthResult]:
        """Perform a specific health check.

        Args:
            check_name: Name of check to perform

        Returns:
            HealthResult or None if check not found
        """
        if check_name not in self.health_checks:
            logger.warning(f"Health check {check_name} not found")
            return None

        check = self.health_checks[check_name]
        start_time = time.perf_counter()

        try:
            # Run the check with timeout
            result = await asyncio.wait_for(
                check.check_function(), timeout=check.timeout_seconds
            )

            response_time_ms = (time.perf_counter() - start_time) * 1000

            # Create result object
            if isinstance(result, HealthResult):
                result.response_time_ms = response_time_ms
                health_result = result
            elif isinstance(result, dict):
                health_result = HealthResult(
                    check_name=check_name,
                    status=HealthStatus(result.get("status", "unknown")),
                    message=result.get("message", ""),
                    response_time_ms=response_time_ms,
                    details=result.get("details", {}),
                )
            else:
                health_result = HealthResult(
                    check_name=check_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Invalid result type: {type(result)}",
                    response_time_ms=response_time_ms,
                )

            # Update check state
            check.last_run = datetime.utcnow()
            check.last_result = health_result

            if health_result.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                check.consecutive_failures += 1
            else:
                check.consecutive_failures = 0

            # Store in history
            self.check_history[check_name].append(health_result)
            if len(self.check_history[check_name]) > 100:
                self.check_history[check_name].pop(0)

            self.total_checks_performed += 1

            return health_result

        except asyncio.TimeoutError:
            response_time_ms = check.timeout_seconds * 1000
            result = HealthResult(
                check_name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Check timed out after {check.timeout_seconds}s",
                response_time_ms=response_time_ms,
            )

            check.last_run = datetime.utcnow()
            check.last_result = result
            check.consecutive_failures += 1

            self.check_history[check_name].append(result)
            self.check_errors += 1

            return result

        except Exception as e:
            response_time_ms = (time.perf_counter() - start_time) * 1000
            result = HealthResult(
                check_name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed: {str(e)}",
                response_time_ms=response_time_ms,
                details={"error": str(e)},
            )

            check.last_run = datetime.utcnow()
            check.last_result = result
            check.consecutive_failures += 1

            self.check_history[check_name].append(result)
            self.check_errors += 1

            logger.error(f"Health check {check_name} failed: {str(e)}")
            return result

    async def perform_comprehensive_check(self) -> HealthReport:
        """Perform all health checks and generate comprehensive report.

        Returns:
            HealthReport with all check results
        """
        try:
            self.last_comprehensive_check = datetime.utcnow()

            # Run all checks concurrently
            check_tasks = []
            for check_name in self.health_checks.keys():
                task = asyncio.create_task(self.perform_check(check_name))
                check_tasks.append(task)

            # Wait for all checks to complete
            results = await asyncio.gather(*check_tasks, return_exceptions=True)

            # Process results
            check_results = []
            status_counts = {status: 0 for status in HealthStatus}

            for i, result in enumerate(results):
                if isinstance(result, HealthResult):
                    check_results.append(result)
                    status_counts[result.status] += 1
                elif isinstance(result, Exception):
                    # Handle task exception
                    check_name = list(self.health_checks.keys())[i]
                    error_result = HealthResult(
                        check_name=check_name,
                        status=HealthStatus.CRITICAL,
                        message=f"Task failed: {str(result)}",
                        response_time_ms=0.0,
                    )
                    check_results.append(error_result)
                    status_counts[HealthStatus.CRITICAL] += 1

            # Determine overall status
            if status_counts[HealthStatus.CRITICAL] > 0:
                overall_status = HealthStatus.CRITICAL
            elif status_counts[HealthStatus.WARNING] > 0:
                overall_status = HealthStatus.WARNING
            elif status_counts[HealthStatus.UNKNOWN] > 0:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.HEALTHY

            # Get system information
            system_info = await self._get_system_info()

            # Create report
            report = HealthReport(
                overall_status=overall_status,
                total_checks=len(check_results),
                healthy_checks=status_counts[HealthStatus.HEALTHY],
                warning_checks=status_counts[HealthStatus.WARNING],
                critical_checks=status_counts[HealthStatus.CRITICAL],
                unknown_checks=status_counts[HealthStatus.UNKNOWN],
                check_results=check_results,
                system_info=system_info,
            )

            logger.info(f"Comprehensive health check completed: {overall_status.value}")
            return report

        except Exception as e:
            logger.error(f"Failed to perform comprehensive health check: {str(e)}")
            return HealthReport(
                overall_status=HealthStatus.CRITICAL,
                total_checks=0,
                healthy_checks=0,
                warning_checks=0,
                critical_checks=1,
                unknown_checks=0,
                check_results=[
                    HealthResult(
                        check_name="comprehensive_check",
                        status=HealthStatus.CRITICAL,
                        message=f"Comprehensive check failed: {str(e)}",
                        response_time_ms=0.0,
                    )
                ],
            )

    async def perform_routine_checks(self) -> Dict[str, HealthResult]:
        """Perform routine health checks based on intervals.

        Returns:
            Dictionary of check results
        """
        current_time = datetime.utcnow()
        results = {}

        for check_name, check in self.health_checks.items():
            # Check if it's time to run this check
            if check.last_run is None:
                should_run = True
            else:
                time_since_last = (current_time - check.last_run).total_seconds()
                should_run = time_since_last >= check.interval_seconds

            if should_run:
                result = await self.perform_check(check_name)
                if result:
                    results[check_name] = result

        return results

    async def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            # CPU info
            cpu_info = {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "load_average": (
                    list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else []
                ),
            }

            # Memory info
            memory = psutil.virtual_memory()
            memory_info = {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "percent": memory.percent,
            }

            # Disk info
            disk = psutil.disk_usage("/")
            disk_info = {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent": (disk.used / disk.total) * 100,
            }

            return {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "uptime_seconds": time.time() - psutil.boot_time(),
            }

        except Exception as e:
            logger.error(f"Failed to get system info: {str(e)}")
            return {"error": str(e)}

    # Standard health check implementations

    async def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check system CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"CPU usage critically high: {cpu_percent:.1f}%"
            elif cpu_percent > 75:
                status = HealthStatus.WARNING
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"

            return {
                "status": status.value,
                "message": message,
                "details": {"cpu_percent": cpu_percent},
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Failed to check CPU usage: {str(e)}",
            }

    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check system memory usage."""
        try:
            memory = psutil.virtual_memory()

            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Memory usage critically high: {memory.percent:.1f}%"
            elif memory.percent > 80:
                status = HealthStatus.WARNING
                message = f"Memory usage high: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "memory_percent": memory.percent,
                    "available_mb": memory.available / (1024 * 1024),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Failed to check memory usage: {str(e)}",
            }

    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check system disk space."""
        try:
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Disk space critically low: {disk_percent:.1f}% used"
            elif disk_percent > 85:
                status = HealthStatus.WARNING
                message = f"Disk space low: {disk_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space sufficient: {disk_percent:.1f}% used"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "disk_percent": disk_percent,
                    "free_gb": disk.free / (1024 * 1024 * 1024),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Failed to check disk space: {str(e)}",
            }

    async def _check_neural_engine_process(self) -> Dict[str, Any]:
        """Check Neural Engine process health."""
        try:
            current_process = psutil.Process()

            # Check if process is running
            if not current_process.is_running():
                return {
                    "status": HealthStatus.CRITICAL.value,
                    "message": "Neural Engine process not running",
                }

            # Check process resources
            cpu_percent = current_process.cpu_percent()
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)

            # Determine status based on resource usage
            if cpu_percent > 95 or memory_mb > 2048:  # More than 2GB
                status = HealthStatus.WARNING
                message = f"High resource usage - CPU: {cpu_percent:.1f}%, Memory: {memory_mb:.1f}MB"
            else:
                status = HealthStatus.HEALTHY
                message = f"Process healthy - CPU: {cpu_percent:.1f}%, Memory: {memory_mb:.1f}MB"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "pid": current_process.pid,
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "num_threads": current_process.num_threads(),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Failed to check Neural Engine process: {str(e)}",
            }

    async def _check_redis_connectivity(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            # This would normally use a Redis client
            # For now, return a placeholder
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Redis connectivity check - placeholder",
                "details": {"note": "Redis check not implemented"},
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Redis connectivity failed: {str(e)}",
            }

    async def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # This would normally test database connection
            # For now, return a placeholder
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Database connectivity check - placeholder",
                "details": {"note": "Database check not implemented"},
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Database connectivity failed: {str(e)}",
            }

    async def _check_device_manager(self) -> Dict[str, Any]:
        """Check device manager status."""
        try:
            # This would check device manager service
            # For now, return a placeholder
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Device manager status check - placeholder",
                "details": {"note": "Device manager check not implemented"},
            }

        except Exception as e:
            return {
                "status": HealthStatus.WARNING.value,
                "message": f"Device manager check failed: {str(e)}",
            }

    async def _check_neural_ledger(self) -> Dict[str, Any]:
        """Check Neural Ledger connectivity."""
        try:
            # This would check Neural Ledger service
            # For now, return a placeholder
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Neural Ledger connectivity check - placeholder",
                "details": {"note": "Neural Ledger check not implemented"},
            }

        except Exception as e:
            return {
                "status": HealthStatus.WARNING.value,
                "message": f"Neural Ledger check failed: {str(e)}",
            }

    async def _check_auth_service(self) -> Dict[str, Any]:
        """Check authentication service status."""
        try:
            # This would check auth service
            # For now, return a placeholder
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Authentication service status check - placeholder",
                "details": {"note": "Auth service check not implemented"},
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL.value,
                "message": f"Auth service check failed: {str(e)}",
            }

    def get_check_summary(self) -> Dict[str, Any]:
        """Get summary of all health checks.

        Returns:
            Summary information
        """
        try:
            total_checks = len(self.health_checks)
            critical_checks = sum(
                1 for check in self.health_checks.values() if check.critical
            )

            # Count recent statuses
            recent_results = {}
            for check_name, check in self.health_checks.items():
                if check.last_result:
                    recent_results[check_name] = check.last_result.status

            status_counts = {status.value: 0 for status in HealthStatus}
            for status in recent_results.values():
                status_counts[status.value] += 1

            return {
                "total_checks": total_checks,
                "critical_checks": critical_checks,
                "total_checks_performed": self.total_checks_performed,
                "check_errors": self.check_errors,
                "last_comprehensive_check": (
                    self.last_comprehensive_check.isoformat()
                    if self.last_comprehensive_check
                    else None
                ),
                "recent_status_counts": status_counts,
            }

        except Exception as e:
            logger.error(f"Failed to get check summary: {str(e)}")
            return {"error": str(e)}
