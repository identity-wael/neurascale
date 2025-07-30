"""Tests for Neural Data MCP Server."""

import pytest
from unittest.mock import AsyncMock, patch

from src.mcp.servers.neural_data.server import NeuralDataMCPServer
from src.mcp.servers.neural_data.handlers import NeuralDataHandlers


class TestNeuralDataMCPServer:
    """Test cases for Neural Data MCP Server."""

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            "auth": {"enabled": False},
            "permissions": {"check_enabled": False},
            "rate_limits": {"enabled": False},
            "neural_engine": {"api_url": "http://test:8000"},
        }

    @pytest.fixture
    async def server(self, config):
        """Create test server instance."""
        server = NeuralDataMCPServer(config)
        await server.register_tools()
        return server

    @pytest.mark.asyncio
    async def test_server_initialization(self, config):
        """Test server initialization."""
        server = NeuralDataMCPServer(config)
        assert server.name == "neurascale-neural-data"
        assert server.version == "1.0.0"
        assert server.config == config
        assert isinstance(server.handlers, NeuralDataHandlers)

    @pytest.mark.asyncio
    async def test_register_tools(self, server):
        """Test tool registration."""
        # Check that all expected tools are registered
        expected_tools = [
            "query_sessions",
            "get_neural_data",
            "apply_filter",
            "run_spectral_analysis",
            "detect_artifacts",
            "export_neural_data",
            "create_visualization",
        ]

        for tool_name in expected_tools:
            assert tool_name in server.tools
            tool = server.tools[tool_name]
            assert "handler" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert "permissions" in tool

    @pytest.mark.asyncio
    async def test_query_sessions(self, server):
        """Test query_sessions tool."""
        # Mock the handler
        with patch.object(
            server.handlers, "query_sessions", new_callable=AsyncMock
        ) as mock_query:
            mock_query.return_value = {
                "sessions": [
                    {
                        "id": "session_001",
                        "patient_id": "patient_001",
                        "device_type": "EEG",
                        "status": "COMPLETED",
                        "start_time": "2024-01-15T10:00:00",
                        "duration": 1800.0,
                    }
                ],
                "total_count": 1,
                "returned_count": 1,
                "offset": 0,
                "limit": 100,
                "has_more": False,
            }

            result = await server._query_sessions(
                patient_id="patient_001",
                device_type="EEG",
                status="COMPLETED",
                limit=100,
                offset=0,
            )

            assert result["total_count"] == 1
            assert len(result["sessions"]) == 1
            assert result["sessions"][0]["id"] == "session_001"

            mock_query.assert_called_once_with(
                patient_id="patient_001",
                start_date=None,
                end_date=None,
                device_type="EEG",
                status="COMPLETED",
                limit=100,
                offset=0,
            )

    @pytest.mark.asyncio
    async def test_get_neural_data(self, server):
        """Test get_neural_data tool."""
        with patch.object(
            server.handlers, "get_neural_data", new_callable=AsyncMock
        ) as mock_get_data:
            mock_get_data.return_value = {
                "session_id": "session_001",
                "data_shape": [8, 10000],
                "sampling_rate": 1000,
                "channels": [0, 1, 2, 3, 4, 5, 6, 7],
                "start_time": 0,
                "end_time": 10,
                "data_summary": {
                    "mean": 0.5,
                    "std": 2.1,
                    "min": -10.2,
                    "max": 12.5,
                },
            }

            result = await server._get_neural_data(
                session_id="session_001",
                channels=[0, 1, 2, 3, 4, 5, 6, 7],
                start_time=0,
                end_time=10,
                downsample_factor=1,
            )

            assert result["session_id"] == "session_001"
            assert result["data_shape"] == [8, 10000]
            assert result["sampling_rate"] == 1000

    @pytest.mark.asyncio
    async def test_apply_filter(self, server):
        """Test apply_filter tool."""
        with patch.object(
            server.handlers, "apply_filter", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = {
                "filter_id": "filter_123",
                "session_id": "session_001",
                "filter_applied": "bandpass",
                "parameters": {
                    "filter_type": "bandpass",
                    "low_freq": 1.0,
                    "high_freq": 40.0,
                    "order": 4,
                },
                "status": "completed",
            }

            result = await server._apply_filter(
                session_id="session_001",
                filter_type="bandpass",
                low_freq=1.0,
                high_freq=40.0,
                order=4,
            )

            assert result["filter_applied"] == "bandpass"
            assert result["parameters"]["low_freq"] == 1.0
            assert result["parameters"]["high_freq"] == 40.0

    @pytest.mark.asyncio
    async def test_run_spectral_analysis(self, server):
        """Test run_spectral_analysis tool."""
        with patch.object(
            server.handlers, "run_spectral_analysis", new_callable=AsyncMock
        ) as mock_spectral:
            mock_spectral.return_value = {
                "analysis_id": "analysis_456",
                "session_id": "session_001",
                "analysis_type": "spectral",
                "method": "welch",
                "frequency_bands": {
                    "delta": [0.5, 4.0],
                    "theta": [4.0, 8.0],
                    "alpha": [8.0, 13.0],
                    "beta": [13.0, 30.0],
                    "gamma": [30.0, 100.0],
                },
                "band_powers": {
                    "channel_0": {
                        "delta": 10.5,
                        "theta": 8.2,
                        "alpha": 15.3,
                        "beta": 5.1,
                        "gamma": 2.8,
                    }
                },
            }

            result = await server._run_spectral_analysis(
                session_id="session_001", channels=[0], method="welch"
            )

            assert result["analysis_type"] == "spectral"
            assert result["method"] == "welch"
            assert "band_powers" in result

    @pytest.mark.asyncio
    async def test_detect_artifacts(self, server):
        """Test detect_artifacts tool."""
        with patch.object(
            server.handlers, "detect_artifacts", new_callable=AsyncMock
        ) as mock_artifacts:
            mock_artifacts.return_value = {
                "detection_id": "detect_789",
                "session_id": "session_001",
                "artifacts_detected": [
                    {
                        "type": "eye_blink",
                        "start_time": 5.2,
                        "duration": 0.3,
                        "channels_affected": [0, 1],
                        "confidence": 0.92,
                    }
                ],
                "total_artifacts": 1,
                "data_quality_score": 0.85,
            }

            result = await server._detect_artifacts(
                session_id="session_001",
                artifact_types=["eye_blink", "muscle"],
                sensitivity="medium",
            )

            assert result["total_artifacts"] == 1
            assert result["data_quality_score"] == 0.85
            assert result["artifacts_detected"][0]["type"] == "eye_blink"

    @pytest.mark.asyncio
    async def test_export_neural_data(self, server):
        """Test export_neural_data tool."""
        with patch.object(
            server.handlers, "export_neural_data", new_callable=AsyncMock
        ) as mock_export:
            mock_export.return_value = {
                "export_id": "export_012",
                "session_id": "session_001",
                "format": "edf",
                "filename": "session_001_edf_export_012.edf",
                "estimated_size_mb": 125.5,
                "status": "processing",
                "download_url": "/downloads/export_012/session_001_edf_export_012.edf",
            }

            result = await server._export_neural_data(
                session_id="session_001", format="edf", compression=True
            )

            assert result["format"] == "edf"
            assert result["status"] == "processing"
            assert "download_url" in result

    @pytest.mark.asyncio
    async def test_create_visualization(self, server):
        """Test create_visualization tool."""
        with patch.object(
            server.handlers, "create_visualization", new_callable=AsyncMock
        ) as mock_viz:
            mock_viz.return_value = {
                "visualization_id": "viz_345",
                "session_id": "session_001",
                "plot_type": "spectrogram",
                "channels_plotted": [0, 1, 2, 3],
                "time_range": [0, 10],
                "image_url": "/visualizations/viz_345/spectrogram.png",
                "interactive": True,
            }

            result = await server._create_visualization(
                session_id="session_001",
                plot_type="spectrogram",
                channels=[0, 1, 2, 3],
                time_range=[0, 10],
            )

            assert result["plot_type"] == "spectrogram"
            assert result["interactive"] is True
            assert "image_url" in result

    @pytest.mark.asyncio
    async def test_input_validation(self, server):
        """Test input validation for tools."""
        # Test invalid pagination
        with pytest.raises(ValueError):
            await server._query_sessions(limit=2000)  # Exceeds max limit

        # Test missing required parameter
        with pytest.raises(ValueError):
            await server._get_neural_data(session_id=None)

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling in tool execution."""
        # Simulate handler error
        with patch.object(
            server.handlers, "query_sessions", new_callable=AsyncMock
        ) as mock_query:
            mock_query.side_effect = Exception("Database connection failed")

            with pytest.raises(Exception) as exc_info:
                await server._query_sessions()

            assert "Database connection failed" in str(exc_info.value)


class TestNeuralDataHandlers:
    """Test cases for Neural Data Handlers."""

    @pytest.fixture
    def handlers(self):
        """Create test handlers instance."""
        config = {"api_url": "http://test:8000"}
        return NeuralDataHandlers(config)

    @pytest.mark.asyncio
    async def test_query_sessions_filtering(self, handlers):
        """Test session filtering logic."""
        result = await handlers.query_sessions(
            device_type="EEG", status="COMPLETED", limit=10
        )

        assert "sessions" in result
        assert "total_count" in result
        assert result["limit"] == 10

        # Check that filters are applied
        for session in result["sessions"]:
            assert session["device_type"] == "EEG"
            assert session["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_get_neural_data_with_downsampling(self, handlers):
        """Test neural data retrieval with downsampling."""
        result = await handlers.get_neural_data(
            session_id="session_001", downsample_factor=10
        )

        assert "sampling_rate" in result
        assert "original_sampling_rate" in result
        assert result["downsample_factor"] == 10

    @pytest.mark.asyncio
    async def test_filter_parameter_validation(self, handlers):
        """Test filter parameter validation."""
        # Test bandpass without required parameters
        with pytest.raises(ValueError) as exc_info:
            await handlers.apply_filter(
                session_id="session_001", filter_type="bandpass", low_freq=None
            )
        assert "requires both low_freq and high_freq" in str(exc_info.value)

        # Test highpass without required parameter
        with pytest.raises(ValueError) as exc_info:
            await handlers.apply_filter(
                session_id="session_001", filter_type="highpass", low_freq=None
            )
        assert "requires low_freq" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_spectral_analysis_default_bands(self, handlers):
        """Test spectral analysis with default frequency bands."""
        result = await handlers.run_spectral_analysis(session_id="session_001")

        assert "frequency_bands" in result
        assert "delta" in result["frequency_bands"]
        assert "theta" in result["frequency_bands"]
        assert "alpha" in result["frequency_bands"]
        assert "beta" in result["frequency_bands"]
        assert "gamma" in result["frequency_bands"]

    @pytest.mark.asyncio
    async def test_artifact_detection_recommendations(self, handlers):
        """Test artifact detection with recommendations."""
        result = await handlers.detect_artifacts(
            session_id="session_001",
            artifact_types=["eye_blink", "muscle", "line_noise"],
            sensitivity="high",
        )

        assert "artifacts_detected" in result
        assert "artifact_summary" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    @pytest.mark.asyncio
    async def test_export_format_support(self, handlers):
        """Test different export formats."""
        formats = ["json", "csv", "edf", "mat", "fif", "parquet"]

        for format in formats:
            result = await handlers.export_neural_data(
                session_id="session_001", format=format
            )
            assert result["format"] == format
            assert "download_url" in result
            assert "estimated_size_mb" in result

    @pytest.mark.asyncio
    async def test_visualization_types(self, handlers):
        """Test different visualization types."""
        plot_types = ["timeseries", "spectrogram", "psd", "topomap", "connectivity"]

        for plot_type in plot_types:
            result = await handlers.create_visualization(
                session_id="session_001", plot_type=plot_type
            )
            assert result["plot_type"] == plot_type
            assert "image_url" in result
            assert "metadata" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
