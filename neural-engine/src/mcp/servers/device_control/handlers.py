"""Device control handlers for MCP server operations."""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import asyncio


class DeviceControlHandlers:
    """Handles device control operations for MCP server."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize device control handlers.

        Args:
            config: Device manager configuration
        """
        self.config = config
        self.api_url = config.get("api_url", "http://localhost:8000")

        # Mock device data for demonstration
        self._mock_devices = self._create_mock_devices()
        self._active_connections = {}
        self._recording_sessions = {}

    async def list_devices(
        self,
        device_type: Optional[str] = None,
        status: str = "all",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List available BCI devices.

        Args:
            device_type: Filter by device type
            status: Filter by connection status
            location: Filter by device location

        Returns:
            Dictionary with devices and metadata
        """
        filtered_devices = []

        for device in self._mock_devices:
            # Apply filters
            if device_type and device["type"] != device_type:
                continue

            if status != "all":
                device_connected = device["id"] in self._active_connections
                if status == "connected" and not device_connected:
                    continue
                if status == "disconnected" and device_connected:
                    continue

            if location and device.get("location") != location:
                continue

            # Update connection status
            device["connected"] = device["id"] in self._active_connections
            device["last_seen"] = self._active_connections.get(device["id"], {}).get(
                "connected_at"
            ) or device.get("last_seen")

            filtered_devices.append(device)

        return {
            "devices": filtered_devices,
            "total_count": len(filtered_devices),
            "active_connections": len(self._active_connections),
            "filter_parameters": {
                "device_type": device_type,
                "status": status,
                "location": location,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_device_info(
        self,
        device_id: str,
        include_capabilities: bool = True,
        include_history: bool = False,
    ) -> Dict[str, Any]:
        """Get detailed device information.

        Args:
            device_id: Device identifier
            include_capabilities: Include device capabilities
            include_history: Include usage history

        Returns:
            Dictionary with device information
        """
        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        # Create detailed device info
        device_info = device.copy()
        device_info["connected"] = device_id in self._active_connections

        if device_id in self._active_connections:
            connection = self._active_connections[device_id]
            device_info["connection_info"] = {
                "connected_at": connection["connected_at"],
                "connection_duration": (
                    datetime.utcnow()
                    - datetime.fromisoformat(connection["connected_at"])
                ).total_seconds(),
                "signal_quality": connection.get("signal_quality", "Good"),
                "impedance_check_passed": connection.get(
                    "impedance_check_passed", True
                ),
            }

        if include_capabilities:
            device_info["capabilities"] = self._get_device_capabilities(device["type"])

        if include_history:
            device_info["usage_history"] = self._get_device_history(device_id)

        # Add current recording status
        if device_id in self._recording_sessions:
            session = self._recording_sessions[device_id]
            device_info["current_recording"] = {
                "session_id": session["session_id"],
                "start_time": session["start_time"],
                "duration": (
                    datetime.utcnow() - datetime.fromisoformat(session["start_time"])
                ).total_seconds(),
                "patient_id": session.get("patient_id"),
            }

        return device_info

    async def connect_device(
        self,
        device_id: str,
        connection_params: Dict[str, Any],
        verify_connection: bool = True,
    ) -> Dict[str, Any]:
        """Connect to a BCI device.

        Args:
            device_id: Device identifier
            connection_params: Connection parameters
            verify_connection: Verify connection after establishing

        Returns:
            Dictionary with connection status
        """
        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        if device_id in self._active_connections:
            raise ValueError(f"Device already connected: {device_id}")

        # Simulate connection process
        await asyncio.sleep(0.5)  # Simulate connection time

        # Create connection record
        connection = {
            "device_id": device_id,
            "connected_at": datetime.utcnow().isoformat(),
            "connection_params": connection_params,
            "signal_quality": "Good",
            "impedance_check_passed": True,
        }

        if verify_connection:
            # Simulate verification
            await asyncio.sleep(0.3)
            connection["verification_passed"] = True
            connection["firmware_version"] = device.get("firmware_version", "2.1.0")
            connection["battery_level"] = np.random.randint(50, 100)

        self._active_connections[device_id] = connection

        return {
            "device_id": device_id,
            "status": "connected",
            "connection_info": connection,
            "device_type": device["type"],
            "channel_count": device["channel_count"],
            "sampling_rate": device["sampling_rate"],
            "message": f"Successfully connected to {device['name']}",
        }

    async def disconnect_device(
        self, device_id: str, force: bool = False, save_session: bool = True
    ) -> Dict[str, Any]:
        """Disconnect from a BCI device.

        Args:
            device_id: Device identifier
            force: Force disconnection
            save_session: Save ongoing session

        Returns:
            Dictionary with disconnection status
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        # Check for active recording
        if device_id in self._recording_sessions and not force:
            raise ValueError(
                f"Device {device_id} has active recording. Use force=True to disconnect."
            )

        # Save session if recording
        session_saved = False
        if device_id in self._recording_sessions and save_session:
            session = self._recording_sessions[device_id]
            session["end_time"] = datetime.utcnow().isoformat()
            session["status"] = "completed"
            session_saved = True
            del self._recording_sessions[device_id]

        # Disconnect device
        connection_info = self._active_connections[device_id]
        connection_duration = (
            datetime.utcnow() - datetime.fromisoformat(connection_info["connected_at"])
        ).total_seconds()

        del self._active_connections[device_id]

        return {
            "device_id": device_id,
            "status": "disconnected",
            "connection_duration": connection_duration,
            "session_saved": session_saved,
            "message": f"Successfully disconnected from device {device_id}",
        }

    async def configure_device(
        self,
        device_id: str,
        sampling_rate: Optional[int] = None,
        channels: Optional[List[int]] = None,
        filters: Optional[Dict[str, float]] = None,
        gain: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Configure device settings.

        Args:
            device_id: Device identifier
            sampling_rate: Sampling rate in Hz
            channels: Channels to enable
            filters: Hardware filter settings
            gain: Amplification gain

        Returns:
            Dictionary with configuration status
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        # Validate configuration parameters
        config_changes = {}

        if sampling_rate is not None:
            if sampling_rate not in device["supported_sampling_rates"]:
                raise ValueError(
                    f"Unsupported sampling rate: {sampling_rate}. "
                    f"Supported rates: {device['supported_sampling_rates']}"
                )
            config_changes["sampling_rate"] = sampling_rate

        if channels is not None:
            max_channels = device["channel_count"]
            if any(ch >= max_channels or ch < 0 for ch in channels):
                raise ValueError(
                    f"Invalid channel numbers. Device has {max_channels} channels."
                )
            config_changes["enabled_channels"] = channels

        if filters is not None:
            config_changes["filters"] = filters

        if gain is not None:
            if gain < 1 or gain > 1000:
                raise ValueError("Gain must be between 1 and 1000")
            config_changes["gain"] = gain

        # Simulate configuration process
        await asyncio.sleep(0.2)

        # Update device configuration
        device.update(config_changes)

        return {
            "device_id": device_id,
            "configuration_applied": config_changes,
            "current_configuration": {
                "sampling_rate": device.get("sampling_rate"),
                "enabled_channels": device.get(
                    "enabled_channels", list(range(device["channel_count"]))
                ),
                "filters": device.get("filters", {}),
                "gain": device.get("gain", 24),
            },
            "status": "configured",
            "message": "Device configuration updated successfully",
        }

    async def start_recording(
        self,
        device_id: str,
        duration: Optional[float] = None,
        session_name: Optional[str] = None,
        patient_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Start neural data recording.

        Args:
            device_id: Device identifier
            duration: Recording duration in seconds
            session_name: Name for the session
            patient_id: Patient identifier
            metadata: Additional metadata

        Returns:
            Dictionary with recording status
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        if device_id in self._recording_sessions:
            raise ValueError(f"Device {device_id} is already recording")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        # Create recording session
        session_id = f"rec_{device_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        session = {
            "session_id": session_id,
            "device_id": device_id,
            "device_type": device["type"],
            "start_time": datetime.utcnow().isoformat(),
            "duration": duration,
            "session_name": session_name or f"Recording {session_id}",
            "patient_id": patient_id,
            "metadata": metadata or {},
            "channel_count": device["channel_count"],
            "sampling_rate": device["sampling_rate"],
            "status": "recording",
            "data_buffer_size": 0,
        }

        self._recording_sessions[device_id] = session

        # Simulate recording start
        await asyncio.sleep(0.1)

        return {
            "session_id": session_id,
            "device_id": device_id,
            "status": "recording_started",
            "start_time": session["start_time"],
            "expected_duration": duration,
            "storage_location": f"/data/recordings/{session_id}",
            "estimated_file_size_mb": self._estimate_file_size(device, duration),
            "message": f"Recording started on {device['name']}",
        }

    async def stop_recording(
        self, device_id: str, save_data: bool = True, auto_analyze: bool = False
    ) -> Dict[str, Any]:
        """Stop neural data recording.

        Args:
            device_id: Device identifier
            save_data: Save recorded data
            auto_analyze: Start automatic analysis

        Returns:
            Dictionary with recording stop status
        """
        if device_id not in self._recording_sessions:
            raise ValueError(f"No active recording on device {device_id}")

        session = self._recording_sessions[device_id]
        end_time = datetime.utcnow()
        start_time = datetime.fromisoformat(session["start_time"])
        actual_duration = (end_time - start_time).total_seconds()

        # Prepare session summary
        session_summary = {
            "session_id": session["session_id"],
            "device_id": device_id,
            "start_time": session["start_time"],
            "end_time": end_time.isoformat(),
            "actual_duration": actual_duration,
            "expected_duration": session.get("duration"),
            "channel_count": session["channel_count"],
            "sampling_rate": session["sampling_rate"],
            "data_saved": save_data,
        }

        if save_data:
            # Simulate data saving
            await asyncio.sleep(0.3)
            file_size_mb = self._estimate_file_size(
                {
                    "channel_count": session["channel_count"],
                    "sampling_rate": session["sampling_rate"],
                },
                actual_duration,
            )
            session_summary["file_size_mb"] = file_size_mb
            session_summary["file_path"] = (
                f"/data/recordings/{session['session_id']}.edf"
            )

        if auto_analyze:
            # Queue for analysis
            analysis_id = str(uuid.uuid4())
            session_summary["analysis_queued"] = True
            session_summary["analysis_id"] = analysis_id

        # Remove from active recordings
        del self._recording_sessions[device_id]

        return {
            "status": "recording_stopped",
            "session_summary": session_summary,
            "message": f"Recording stopped successfully on device {device_id}",
        }

    async def check_impedance(
        self,
        device_id: str,
        channels: Optional[List[int]] = None,
        test_frequency: float = 10,
        acceptable_threshold: float = 5000,
    ) -> Dict[str, Any]:
        """Check electrode impedances.

        Args:
            device_id: Device identifier
            channels: Channels to check
            test_frequency: Test frequency in Hz
            acceptable_threshold: Acceptable impedance in ohms

        Returns:
            Dictionary with impedance results
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        if channels is None:
            channels = list(range(device["channel_count"]))

        # Simulate impedance measurement
        await asyncio.sleep(0.5)

        # Generate mock impedance values
        impedances = {}
        failed_channels = []

        for channel in channels:
            # Most channels have good impedance, some are borderline
            if np.random.random() < 0.8:
                impedance = np.random.uniform(1000, 4000)  # Good
            elif np.random.random() < 0.9:
                impedance = np.random.uniform(4000, 6000)  # Borderline
            else:
                impedance = np.random.uniform(6000, 20000)  # Poor

            impedances[f"channel_{channel}"] = impedance

            if impedance > acceptable_threshold:
                failed_channels.append(channel)

        # Calculate statistics
        impedance_values = list(impedances.values())

        return {
            "device_id": device_id,
            "test_frequency": test_frequency,
            "channels_tested": len(channels),
            "impedances": impedances,
            "statistics": {
                "mean": float(np.mean(impedance_values)),
                "median": float(np.median(impedance_values)),
                "min": float(np.min(impedance_values)),
                "max": float(np.max(impedance_values)),
                "std": float(np.std(impedance_values)),
            },
            "threshold": acceptable_threshold,
            "passed_channels": len(channels) - len(failed_channels),
            "failed_channels": failed_channels,
            "overall_status": "passed" if len(failed_channels) == 0 else "failed",
            "recommendations": self._generate_impedance_recommendations(
                impedances, acceptable_threshold
            ),
            "test_duration": 0.5,
            "tested_at": datetime.utcnow().isoformat(),
        }

    async def monitor_signal_quality(
        self,
        device_id: str,
        duration: float = 10,
        channels: Optional[List[int]] = None,
        quality_metrics: List[str] = None,
    ) -> Dict[str, Any]:
        """Monitor real-time signal quality.

        Args:
            device_id: Device identifier
            duration: Monitoring duration
            channels: Channels to monitor
            quality_metrics: Metrics to calculate

        Returns:
            Dictionary with signal quality results
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        if channels is None:
            channels = list(range(min(8, device["channel_count"])))

        if quality_metrics is None:
            quality_metrics = ["snr", "artifacts", "noise_level"]

        # Simulate monitoring
        monitoring_id = str(uuid.uuid4())
        results = {}

        for metric in quality_metrics:
            if metric == "snr":
                # Generate SNR values for each channel
                snr_values = {}
                for ch in channels:
                    snr = np.random.uniform(10, 40)  # dB
                    snr_values[f"channel_{ch}"] = float(snr)
                results["snr"] = {
                    "values": snr_values,
                    "average": float(np.mean(list(snr_values.values()))),
                    "unit": "dB",
                }

            elif metric == "artifacts":
                # Detect artifacts
                artifact_counts = {}
                for ch in channels:
                    count = np.random.poisson(2)  # Average 2 artifacts
                    artifact_counts[f"channel_{ch}"] = count
                results["artifacts"] = {
                    "counts": artifact_counts,
                    "total": sum(artifact_counts.values()),
                    "rate": sum(artifact_counts.values()) / duration,
                    "unit": "artifacts/second",
                }

            elif metric == "drift":
                # Measure baseline drift
                drift_values = {}
                for ch in channels:
                    drift = np.random.uniform(0, 50)  # microvolts
                    drift_values[f"channel_{ch}"] = float(drift)
                results["drift"] = {
                    "values": drift_values,
                    "average": float(np.mean(list(drift_values.values()))),
                    "unit": "microvolts",
                }

            elif metric == "saturation":
                # Check for saturation events
                saturation_events = {}
                for ch in channels:
                    events = np.random.poisson(0.5)  # Rare events
                    saturation_events[f"channel_{ch}"] = events
                results["saturation"] = {
                    "events": saturation_events,
                    "total": sum(saturation_events.values()),
                    "channels_affected": sum(
                        1 for v in saturation_events.values() if v > 0
                    ),
                }

            elif metric == "noise_level":
                # Measure noise levels
                noise_values = {}
                for ch in channels:
                    noise = np.random.uniform(0.5, 5)  # microvolts RMS
                    noise_values[f"channel_{ch}"] = float(noise)
                results["noise_level"] = {
                    "values": noise_values,
                    "average": float(np.mean(list(noise_values.values()))),
                    "unit": "microvolts RMS",
                }

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(results)

        return {
            "monitoring_id": monitoring_id,
            "device_id": device_id,
            "duration": duration,
            "channels_monitored": channels,
            "metrics_calculated": quality_metrics,
            "results": results,
            "overall_quality_score": quality_score,
            "quality_rating": self._get_quality_rating(quality_score),
            "recommendations": self._generate_quality_recommendations(results),
            "monitored_at": datetime.utcnow().isoformat(),
        }

    async def run_device_diagnostics(
        self, device_id: str, test_suite: str = "basic", generate_report: bool = True
    ) -> Dict[str, Any]:
        """Run comprehensive device diagnostics.

        Args:
            device_id: Device identifier
            test_suite: Test suite to run
            generate_report: Generate diagnostic report

        Returns:
            Dictionary with diagnostic results
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        diagnostic_id = str(uuid.uuid4())
        test_results = {}

        # Define test suites
        test_definitions = {
            "basic": ["connectivity", "firmware", "battery"],
            "extended": ["connectivity", "firmware", "battery", "channels", "sampling"],
            "full": [
                "connectivity",
                "firmware",
                "battery",
                "channels",
                "sampling",
                "noise",
                "filters",
                "memory",
            ],
        }

        tests_to_run = test_definitions.get(test_suite, test_definitions["basic"])

        # Run each test
        for test in tests_to_run:
            if test == "connectivity":
                test_results["connectivity"] = {
                    "status": "passed",
                    "latency_ms": float(np.random.uniform(1, 10)),
                    "packet_loss": 0.0,
                    "signal_strength": "excellent",
                }

            elif test == "firmware":
                test_results["firmware"] = {
                    "status": "passed",
                    "current_version": device.get("firmware_version", "2.1.0"),
                    "latest_version": "2.1.0",
                    "update_available": False,
                }

            elif test == "battery":
                battery_level = np.random.randint(50, 100)
                test_results["battery"] = {
                    "status": "passed" if battery_level > 20 else "warning",
                    "level": battery_level,
                    "voltage": float(np.random.uniform(3.6, 4.2)),
                    "estimated_runtime_hours": battery_level * 0.1,
                }

            elif test == "channels":
                # Test all channels
                channel_status = {}
                for ch in range(device["channel_count"]):
                    # Most channels pass
                    status = "passed" if np.random.random() < 0.95 else "failed"
                    channel_status[f"channel_{ch}"] = status

                failed_channels = [
                    ch for ch, st in channel_status.items() if st == "failed"
                ]
                test_results["channels"] = {
                    "status": "passed" if len(failed_channels) == 0 else "failed",
                    "total_channels": device["channel_count"],
                    "passed_channels": device["channel_count"] - len(failed_channels),
                    "failed_channels": failed_channels,
                    "channel_status": channel_status,
                }

            elif test == "sampling":
                # Test sampling accuracy
                test_results["sampling"] = {
                    "status": "passed",
                    "nominal_rate": device["sampling_rate"],
                    "measured_rate": device["sampling_rate"]
                    * np.random.uniform(0.999, 1.001),
                    "jitter_us": float(np.random.uniform(1, 10)),
                    "accuracy_ppm": float(np.random.uniform(10, 50)),
                }

            elif test == "noise":
                # Measure noise floor
                noise_levels = []
                for _ in range(device["channel_count"]):
                    noise_levels.append(float(np.random.uniform(0.5, 3)))

                test_results["noise"] = {
                    "status": "passed",
                    "average_noise_uv": float(np.mean(noise_levels)),
                    "max_noise_uv": float(np.max(noise_levels)),
                    "noise_floor_spec": "< 5 uV RMS",
                }

            elif test == "filters":
                # Test hardware filters
                test_results["filters"] = {
                    "status": "passed",
                    "highpass_cutoff": device.get("filters", {}).get("highpass", 0.5),
                    "lowpass_cutoff": device.get("filters", {}).get("lowpass", 100),
                    "notch_filter": "50/60 Hz",
                    "filter_response": "within spec",
                }

            elif test == "memory":
                # Test internal memory
                test_results["memory"] = {
                    "status": "passed",
                    "total_mb": 512,
                    "used_mb": np.random.randint(50, 200),
                    "available_mb": 512 - np.random.randint(50, 200),
                    "buffer_status": "healthy",
                }

            # Simulate test duration
            await asyncio.sleep(0.2)

        # Calculate overall status
        all_passed = all(
            result.get("status") == "passed" for result in test_results.values()
        )
        any_failed = any(
            result.get("status") == "failed" for result in test_results.values()
        )

        overall_status = (
            "passed" if all_passed else ("failed" if any_failed else "warning")
        )

        diagnostic_result = {
            "diagnostic_id": diagnostic_id,
            "device_id": device_id,
            "device_name": device["name"],
            "test_suite": test_suite,
            "overall_status": overall_status,
            "test_results": test_results,
            "tests_run": len(test_results),
            "tests_passed": sum(
                1 for r in test_results.values() if r.get("status") == "passed"
            ),
            "tests_failed": sum(
                1 for r in test_results.values() if r.get("status") == "failed"
            ),
            "diagnostic_duration": len(test_results) * 0.2,
            "performed_at": datetime.utcnow().isoformat(),
        }

        if generate_report:
            report_id = str(uuid.uuid4())
            diagnostic_result["report_generated"] = True
            diagnostic_result["report_id"] = report_id
            diagnostic_result["report_url"] = f"/reports/diagnostics/{report_id}.pdf"

        return diagnostic_result

    async def calibrate_device(
        self,
        device_id: str,
        calibration_type: str = "full",
        reference_signal: Optional[Dict[str, Any]] = None,
        channels: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Calibrate device.

        Args:
            device_id: Device identifier
            calibration_type: Type of calibration
            reference_signal: Reference signal parameters
            channels: Channels to calibrate

        Returns:
            Dictionary with calibration results
        """
        if device_id not in self._active_connections:
            raise ValueError(f"Device not connected: {device_id}")

        device = next((d for d in self._mock_devices if d["id"] == device_id), None)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        if channels is None:
            channels = list(range(device["channel_count"]))

        calibration_id = str(uuid.uuid4())

        # Simulate calibration process
        calibration_steps = []
        calibration_values = {}

        if calibration_type in ["offset", "full"]:
            # DC offset calibration
            await asyncio.sleep(0.3)
            offset_values = {}
            for ch in channels:
                offset = np.random.uniform(-10, 10)  # microvolts
                offset_values[f"channel_{ch}"] = float(offset)
            calibration_values["offset"] = offset_values
            calibration_steps.append("DC offset calibration completed")

        if calibration_type in ["gain", "full"]:
            # Gain calibration
            await asyncio.sleep(0.3)
            gain_values = {}
            for ch in channels:
                gain_correction = np.random.uniform(0.98, 1.02)
                gain_values[f"channel_{ch}"] = float(gain_correction)
            calibration_values["gain"] = gain_values
            calibration_steps.append("Gain calibration completed")

        if calibration_type == "full":
            # Additional full calibration steps
            await asyncio.sleep(0.2)
            calibration_values["linearity"] = "verified"
            calibration_values["crosstalk"] = "< -60 dB"
            calibration_steps.append("Linearity verification completed")
            calibration_steps.append("Crosstalk measurement completed")

        if calibration_type == "channel_specific" and reference_signal:
            # Channel-specific calibration with reference
            await asyncio.sleep(0.4)
            channel_calibration = {}
            for ch in channels:
                channel_calibration[f"channel_{ch}"] = {
                    "offset": float(np.random.uniform(-5, 5)),
                    "gain": float(np.random.uniform(0.99, 1.01)),
                    "phase": float(np.random.uniform(-1, 1)),
                }
            calibration_values["channel_specific"] = channel_calibration
            calibration_steps.append("Channel-specific calibration completed")

        # Save calibration data
        calibration_data = {
            "calibration_id": calibration_id,
            "device_id": device_id,
            "calibration_type": calibration_type,
            "channels_calibrated": channels,
            "calibration_values": calibration_values,
            "reference_signal": reference_signal,
            "calibration_steps": calibration_steps,
            "status": "completed",
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "performed_at": datetime.utcnow().isoformat(),
        }

        return {
            "status": "calibration_completed",
            "calibration_data": calibration_data,
            "message": f"Device {device_id} calibrated successfully",
            "next_calibration_due": (
                datetime.utcnow() + timedelta(days=30)
            ).isoformat(),
        }

    def _create_mock_devices(self) -> List[Dict[str, Any]]:
        """Create mock device data for demonstration."""
        devices = []

        device_configs = [
            {
                "id": "device_001",
                "name": "NeuraLink Pro EEG-128",
                "type": "EEG",
                "model": "NLP-128",
                "serial_number": "NLP128-2024-001",
                "channel_count": 128,
                "sampling_rate": 1000,
                "supported_sampling_rates": [250, 500, 1000, 2000],
            },
            {
                "id": "device_002",
                "name": "BrainAmp MR 32",
                "type": "EEG",
                "model": "BA-MR32",
                "serial_number": "BAMR32-2024-042",
                "channel_count": 32,
                "sampling_rate": 500,
                "supported_sampling_rates": [250, 500, 1000],
            },
            {
                "id": "device_003",
                "name": "Delsys Trigno EMG",
                "type": "EMG",
                "model": "TRIGNO-16",
                "serial_number": "DTR16-2024-089",
                "channel_count": 16,
                "sampling_rate": 2000,
                "supported_sampling_rates": [1000, 2000, 4000],
            },
            {
                "id": "device_004",
                "name": "NIRScout fNIRS",
                "type": "fNIRS",
                "model": "NS-24",
                "serial_number": "NS24-2024-015",
                "channel_count": 24,
                "sampling_rate": 10,
                "supported_sampling_rates": [10, 20, 50],
            },
            {
                "id": "device_005",
                "name": "MagStim TMS",
                "type": "TMS",
                "model": "MS-RAPID2",
                "serial_number": "MSR2-2024-003",
                "channel_count": 1,
                "sampling_rate": 1,
                "supported_sampling_rates": [1],
            },
        ]

        for config in device_configs:
            device = config.copy()
            device.update(
                {
                    "firmware_version": f"2.{np.random.randint(0, 3)}.{np.random.randint(0, 10)}",
                    "last_seen": (
                        datetime.utcnow() - timedelta(hours=np.random.randint(1, 48))
                    ).isoformat(),
                    "location": np.random.choice(["Lab A", "Lab B", "OR 1", "OR 2"]),
                    "status": "available",
                    "battery_powered": device["type"] in ["EMG", "fNIRS"],
                    "wireless": device["type"] in ["EMG", "fNIRS"],
                    "ce_certified": True,
                    "fda_approved": True,
                }
            )
            devices.append(device)

        return devices

    def _get_device_capabilities(self, device_type: str) -> Dict[str, Any]:
        """Get device capabilities based on type."""
        capabilities = {
            "EEG": {
                "signal_types": ["raw", "filtered", "referenced"],
                "filter_types": ["highpass", "lowpass", "bandpass", "notch"],
                "reference_types": ["average", "linked_ears", "cz", "custom"],
                "impedance_check": True,
                "real_time_processing": True,
                "event_markers": True,
                "max_recording_hours": 24,
            },
            "EMG": {
                "signal_types": ["raw", "rectified", "envelope"],
                "filter_types": ["highpass", "lowpass", "bandpass"],
                "trigger_modes": ["threshold", "pattern", "manual"],
                "impedance_check": True,
                "real_time_processing": True,
                "wireless_range_m": 40,
                "battery_life_hours": 8,
            },
            "ECG": {
                "signal_types": ["raw", "filtered"],
                "filter_types": ["highpass", "lowpass", "notch"],
                "lead_configurations": ["3-lead", "5-lead", "12-lead"],
                "heart_rate_detection": True,
                "arrhythmia_detection": True,
                "real_time_processing": True,
            },
            "fNIRS": {
                "signal_types": ["hbo", "hbr", "thb"],
                "wavelengths_nm": [760, 850],
                "source_detector_pairs": 12,
                "sampling_modes": ["continuous", "event_related"],
                "motion_correction": True,
                "real_time_processing": False,
            },
            "TMS": {
                "pulse_types": ["single", "paired", "theta_burst"],
                "intensity_range": [0, 100],
                "coil_types": ["figure8", "circular", "double_cone"],
                "neuronavigation": True,
                "emg_integration": True,
                "safety_features": ["thermal_monitoring", "automatic_discharge"],
            },
            "tDCS": {
                "stimulation_modes": ["constant", "pulsed", "alternating"],
                "current_range_ma": [0, 4],
                "electrode_configurations": ["bipolar", "multichannel"],
                "impedance_monitoring": True,
                "safety_limits": True,
                "session_duration_min": [5, 30],
            },
            "HYBRID": {
                "integrated_modalities": ["EEG", "TMS", "EMG"],
                "synchronization": True,
                "unified_trigger": True,
                "combined_analysis": True,
                "real_time_processing": True,
            },
        }

        return capabilities.get(device_type, {})

    def _get_device_history(self, device_id: str) -> List[Dict[str, Any]]:
        """Get mock device usage history."""
        history = []

        for i in range(5):
            session_date = datetime.utcnow() - timedelta(days=i * 2)
            history.append(
                {
                    "session_id": f"hist_{device_id}_{i}",
                    "date": session_date.isoformat(),
                    "duration_hours": float(np.random.uniform(0.5, 4)),
                    "patient_count": np.random.randint(1, 5),
                    "data_collected_gb": float(np.random.uniform(0.1, 2)),
                    "issues": (
                        "None"
                        if np.random.random() < 0.8
                        else "Minor connectivity issues"
                    ),
                }
            )

        return history

    def _estimate_file_size(
        self, device: Dict[str, Any], duration: Optional[float]
    ) -> float:
        """Estimate recording file size in MB."""
        if duration is None:
            duration = 3600  # 1 hour default

        channels = device["channel_count"]
        sampling_rate = device["sampling_rate"]
        bytes_per_sample = 4  # 32-bit float

        size_bytes = channels * sampling_rate * duration * bytes_per_sample
        size_mb = size_bytes / (1024 * 1024)

        return round(size_mb, 2)

    def _generate_impedance_recommendations(
        self, impedances: Dict[str, float], threshold: float
    ) -> List[str]:
        """Generate recommendations based on impedance values."""
        recommendations = []

        high_impedance_channels = [
            ch for ch, imp in impedances.items() if imp > threshold
        ]

        if high_impedance_channels:
            recommendations.append(
                f"Re-prepare electrodes on channels: {', '.join(high_impedance_channels)}"
            )
            recommendations.append(
                "Apply additional conductive gel to high-impedance electrodes"
            )

        avg_impedance = np.mean(list(impedances.values()))
        if avg_impedance > threshold * 0.8:
            recommendations.append("Consider skin preparation with abrasive gel")
            recommendations.append("Check electrode age and replace if necessary")

        if not recommendations:
            recommendations.append("All impedances within acceptable range")
            recommendations.append("Ready for recording")

        return recommendations

    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall signal quality score (0-100)."""
        score = 100.0

        # SNR contribution (40%)
        if "snr" in metrics:
            avg_snr = metrics["snr"]["average"]
            snr_score = min(100, (avg_snr / 30) * 100)  # 30 dB = perfect
            score *= 0.6
            score += snr_score * 0.4

        # Artifacts contribution (30%)
        if "artifacts" in metrics:
            artifact_rate = metrics["artifacts"]["rate"]
            artifact_score = max(0, 100 - (artifact_rate * 20))  # 5 artifacts/s = 0
            score *= 0.7
            score += artifact_score * 0.3

        # Noise level contribution (30%)
        if "noise_level" in metrics:
            avg_noise = metrics["noise_level"]["average"]
            noise_score = max(0, 100 - (avg_noise * 20))  # 5 uV = 0
            score *= 0.7
            score += noise_score * 0.3

        return round(score, 1)

    def _get_quality_rating(self, score: float) -> str:
        """Get quality rating based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Acceptable"
        elif score >= 40:
            return "Poor"
        else:
            return "Unacceptable"

    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on signal quality metrics."""
        recommendations = []

        if "snr" in metrics and metrics["snr"]["average"] < 20:
            recommendations.append("Low SNR detected - check electrode connections")
            recommendations.append(
                "Consider moving to electrically quieter environment"
            )

        if "artifacts" in metrics and metrics["artifacts"]["rate"] > 2:
            recommendations.append("High artifact rate - ensure participant is relaxed")
            recommendations.append("Check for sources of interference")

        if "noise_level" in metrics and metrics["noise_level"]["average"] > 3:
            recommendations.append("High noise levels - verify grounding")
            recommendations.append("Check for nearby electrical equipment")

        if "drift" in metrics and metrics["drift"]["average"] > 30:
            recommendations.append(
                "Significant baseline drift - allow amplifiers to warm up"
            )
            recommendations.append("Check electrode stability")

        if not recommendations:
            recommendations.append("Signal quality is excellent")
            recommendations.append("Ready for data collection")

        return recommendations
