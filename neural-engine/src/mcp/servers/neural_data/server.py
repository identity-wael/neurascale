"""Neural Data MCP Server implementation."""

from typing import Dict, Any, List, Optional

from ...core.base_server import BaseNeuralMCPServer
from ...utils.validators import (
    validate_neural_data_params,
    validate_filter_params,
    validate_export_params,
    validate_pagination_params,
)
from .handlers import NeuralDataHandlers


class NeuralDataMCPServer(BaseNeuralMCPServer):
    """MCP server for neural data access and analysis."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Neural Data MCP server.

        Args:
            config: Server configuration
        """
        super().__init__("neurascale-neural-data", "1.0.0", config)

        # Initialize handlers
        self.handlers = NeuralDataHandlers(config.get("neural_engine", {}))

    async def register_tools(self) -> None:
        """Register all neural data tools."""

        # Data Query Tools
        self.register_tool(
            name="query_sessions",
            handler=self._query_sessions,
            description="Query neural recording sessions with filtering options",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Filter by patient identifier",
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Filter sessions starting after this date",
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Filter sessions starting before this date",
                    },
                    "device_type": {
                        "type": "string",
                        "enum": ["EEG", "EMG", "ECG", "fNIRS", "TMS", "tDCS", "HYBRID"],
                        "description": "Filter by device type",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["COMPLETED", "RECORDING", "FAILED", "PREPARING"],
                        "description": "Filter by session status",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 100,
                        "description": "Maximum number of sessions to return",
                    },
                    "offset": {
                        "type": "integer",
                        "minimum": 0,
                        "default": 0,
                        "description": "Number of sessions to skip",
                    },
                },
                "required": [],
            },
            permissions=["neural_data.read", "sessions.list"],
        )

        self.register_tool(
            name="get_neural_data",
            handler=self._get_neural_data,
            description="Retrieve neural data from a specific recording session",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Specific channels to retrieve (optional)",
                    },
                    "start_time": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Start time in seconds from session beginning",
                    },
                    "end_time": {
                        "type": "number",
                        "minimum": 0,
                        "description": "End time in seconds from session beginning",
                    },
                    "downsample_factor": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 1,
                        "description": "Downsample factor to reduce data size",
                    },
                },
                "required": ["session_id"],
            },
            permissions=["neural_data.read"],
        )

        # Signal Processing Tools
        self.register_tool(
            name="apply_filter",
            handler=self._apply_filter,
            description="Apply signal processing filter to neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "filter_type": {
                        "type": "string",
                        "enum": ["bandpass", "highpass", "lowpass", "notch"],
                        "description": "Type of filter to apply",
                    },
                    "low_freq": {
                        "type": "number",
                        "minimum": 0.1,
                        "maximum": 1000,
                        "description": "Low frequency cutoff (Hz)",
                    },
                    "high_freq": {
                        "type": "number",
                        "minimum": 0.1,
                        "maximum": 1000,
                        "description": "High frequency cutoff (Hz)",
                    },
                    "order": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 4,
                        "description": "Filter order",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to filter (optional, defaults to all)",
                    },
                },
                "required": ["session_id", "filter_type"],
            },
            permissions=["neural_data.process", "signal_processing.apply"],
        )

        # Analysis Tools
        self.register_tool(
            name="run_spectral_analysis",
            handler=self._run_spectral_analysis,
            description="Perform spectral analysis on neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to analyze",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["fft", "welch", "multitaper"],
                        "default": "welch",
                        "description": "Spectral analysis method",
                    },
                    "frequency_bands": {
                        "type": "object",
                        "properties": {
                            "delta": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "theta": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "alpha": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "beta": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "gamma": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                        },
                        "description": "Custom frequency bands for analysis",
                    },
                },
                "required": ["session_id"],
            },
            permissions=["neural_data.analyze", "analysis.spectral"],
        )

        self.register_tool(
            name="detect_artifacts",
            handler=self._detect_artifacts,
            description="Detect artifacts in neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "artifact_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "eye_blink",
                                "muscle",
                                "line_noise",
                                "electrode_pop",
                                "movement",
                            ],
                        },
                        "default": ["eye_blink", "muscle", "line_noise"],
                        "description": "Types of artifacts to detect",
                    },
                    "sensitivity": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "Detection sensitivity",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to analyze for artifacts",
                    },
                },
                "required": ["session_id"],
            },
            permissions=["neural_data.analyze", "artifact_detection.run"],
        )

        # Export Tools
        self.register_tool(
            name="export_neural_data",
            handler=self._export_neural_data,
            description="Export neural data in various formats",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv", "edf", "mat", "fif", "parquet"],
                        "description": "Export format",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to export",
                    },
                    "start_time": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Start time in seconds",
                    },
                    "end_time": {
                        "type": "number",
                        "minimum": 0,
                        "description": "End time in seconds",
                    },
                    "compression": {
                        "type": "boolean",
                        "default": True,
                        "description": "Apply compression to exported file",
                    },
                },
                "required": ["session_id", "format"],
            },
            permissions=["neural_data.export", "data.download"],
        )

        # Visualization Tools
        self.register_tool(
            name="create_visualization",
            handler=self._create_visualization,
            description="Create visualizations of neural data",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Recording session identifier",
                    },
                    "plot_type": {
                        "type": "string",
                        "enum": [
                            "timeseries",
                            "spectrogram",
                            "psd",
                            "topomap",
                            "connectivity",
                        ],
                        "description": "Type of visualization to create",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to visualize",
                    },
                    "time_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "[start_time, end_time] in seconds",
                    },
                    "options": {
                        "type": "object",
                        "description": "Plot-specific options",
                    },
                },
                "required": ["session_id", "plot_type"],
            },
            permissions=["neural_data.visualize", "plots.create"],
        )

    # Tool Implementation Methods
    async def _query_sessions(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        device_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query neural recording sessions."""
        # Validate pagination params
        validate_pagination_params({"limit": limit, "offset": offset})

        return await self.handlers.query_sessions(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            device_type=device_type,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def _get_neural_data(
        self,
        session_id: str,
        channels: Optional[List[int]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        downsample_factor: int = 1,
    ) -> Dict[str, Any]:
        """Retrieve neural data from session."""
        # Validate parameters
        validate_neural_data_params(
            {
                "session_id": session_id,
                "channels": channels,
                "start_time": start_time,
                "end_time": end_time,
                "downsample_factor": downsample_factor,
            }
        )

        return await self.handlers.get_neural_data(
            session_id=session_id,
            channels=channels,
            start_time=start_time,
            end_time=end_time,
            downsample_factor=downsample_factor,
        )

    async def _apply_filter(
        self,
        session_id: str,
        filter_type: str,
        low_freq: Optional[float] = None,
        high_freq: Optional[float] = None,
        order: int = 4,
        channels: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Apply signal processing filter."""
        # Validate filter parameters
        validate_filter_params(
            {
                "filter_type": filter_type,
                "low_freq": low_freq,
                "high_freq": high_freq,
                "order": order,
            }
        )

        return await self.handlers.apply_filter(
            session_id=session_id,
            filter_type=filter_type,
            low_freq=low_freq,
            high_freq=high_freq,
            order=order,
            channels=channels,
        )

    async def _run_spectral_analysis(
        self,
        session_id: str,
        channels: Optional[List[int]] = None,
        method: str = "welch",
        frequency_bands: Optional[Dict[str, List[float]]] = None,
    ) -> Dict[str, Any]:
        """Run spectral analysis on neural data."""
        return await self.handlers.run_spectral_analysis(
            session_id=session_id,
            channels=channels,
            method=method,
            frequency_bands=frequency_bands,
        )

    async def _detect_artifacts(
        self,
        session_id: str,
        artifact_types: List[str] = None,
        sensitivity: str = "medium",
        channels: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Detect artifacts in neural data."""
        if artifact_types is None:
            artifact_types = ["eye_blink", "muscle", "line_noise"]

        return await self.handlers.detect_artifacts(
            session_id=session_id,
            artifact_types=artifact_types,
            sensitivity=sensitivity,
            channels=channels,
        )

    async def _export_neural_data(
        self,
        session_id: str,
        format: str,
        channels: Optional[List[int]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        compression: bool = True,
    ) -> Dict[str, Any]:
        """Export neural data in specified format."""
        # Validate export parameters
        validate_export_params({"session_id": session_id, "format": format})

        return await self.handlers.export_neural_data(
            session_id=session_id,
            format=format,
            channels=channels,
            start_time=start_time,
            end_time=end_time,
            compression=compression,
        )

    async def _create_visualization(
        self,
        session_id: str,
        plot_type: str,
        channels: Optional[List[int]] = None,
        time_range: Optional[List[float]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create visualization of neural data."""
        return await self.handlers.create_visualization(
            session_id=session_id,
            plot_type=plot_type,
            channels=channels,
            time_range=time_range,
            options=options or {},
        )
