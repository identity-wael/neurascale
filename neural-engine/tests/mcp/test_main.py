"""Tests for MCP main entry point and server manager."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys

from src.mcp.main import MCPServerManager, main, cli_neural_data, cli_device_control


class TestMCPServerManager:
    """Test cases for MCP Server Manager."""

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            "servers": {
                "neural_data": {"port": 9001},
                "device_control": {"port": 9002},
            },
            "logging": {"level": "INFO", "format": "%(message)s"},
            "auth": {"enabled": False},
            "permissions": {"check_enabled": False},
            "rate_limits": {"enabled": False},
        }

    @pytest.fixture
    def manager(self, config):
        """Create test manager instance."""
        return MCPServerManager(config)

    @pytest.mark.asyncio
    async def test_manager_initialization(self, config):
        """Test manager initialization."""
        manager = MCPServerManager(config)
        assert manager.config == config
        assert manager.servers == {}
        assert manager.running is False
        assert manager.http_app is None
        assert manager.http_runner is None

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, manager):
        """Test health check endpoint."""
        # Setup HTTP server
        await manager.setup_http_server(8080)

        # Create mock request
        mock_request = Mock()

        # Call health check
        response = await manager.health_check(mock_request)

        assert response.status == 200
        data = response.body.decode()
        assert "healthy" in data
        assert "servers" in data

        # Cleanup
        await manager.http_runner.cleanup()

    @pytest.mark.asyncio
    async def test_start_servers(self, manager):
        """Test starting MCP servers."""
        # Mock the server instances
        with patch.object(
            manager, "_start_server", new_callable=AsyncMock
        ) as mock_start:
            await manager.start_servers(["neural_data", "device_control"], 8080)

            assert manager.running is True
            assert mock_start.call_count == 2
            mock_start.assert_any_call("neural_data")
            mock_start.assert_any_call("device_control")

        # Cleanup
        await manager.http_runner.cleanup()

    @pytest.mark.asyncio
    async def test_start_server_neural_data(self, manager):
        """Test starting neural data server."""
        with patch("src.mcp.main.NeuralDataMCPServer") as MockServer:
            mock_instance = Mock()
            mock_instance.start = AsyncMock()
            MockServer.return_value = mock_instance

            await manager._start_server("neural_data")

            assert "neural_data" in manager.servers
            assert manager.servers["neural_data"] == mock_instance
            mock_instance.start.assert_called_once_with(9001)

    @pytest.mark.asyncio
    async def test_start_server_device_control(self, manager):
        """Test starting device control server."""
        with patch("src.mcp.main.DeviceControlMCPServer") as MockServer:
            mock_instance = Mock()
            mock_instance.start = AsyncMock()
            MockServer.return_value = mock_instance

            await manager._start_server("device_control")

            assert "device_control" in manager.servers
            assert manager.servers["device_control"] == mock_instance
            mock_instance.start.assert_called_once_with(9002)

    @pytest.mark.asyncio
    async def test_start_server_unknown_type(self, manager):
        """Test starting unknown server type."""
        with pytest.raises(ValueError) as exc_info:
            await manager._start_server("unknown_server")

        assert "Unknown server type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stop_servers(self, manager):
        """Test stopping all servers."""
        # Setup mock servers
        mock_server1 = Mock()
        mock_server1.stop = AsyncMock()
        mock_server2 = Mock()
        mock_server2.stop = AsyncMock()

        manager.servers = {
            "neural_data": mock_server1,
            "device_control": mock_server2,
        }
        manager.running = True

        # Setup mock HTTP runner
        manager.http_runner = Mock()
        manager.http_runner.cleanup = AsyncMock()

        await manager.stop_servers()

        assert manager.running is False
        assert len(manager.servers) == 0
        mock_server1.stop.assert_called_once()
        mock_server2.stop.assert_called_once()
        manager.http_runner.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_servers_with_error(self, manager):
        """Test stopping servers with error handling."""
        # Setup mock server that raises error
        mock_server = Mock()
        mock_server.stop = AsyncMock(side_effect=Exception("Stop failed"))

        manager.servers = {"neural_data": mock_server}
        manager.running = True

        # Should not raise exception
        await manager.stop_servers()

        assert manager.running is False
        assert len(manager.servers) == 0

    @pytest.mark.asyncio
    async def test_run_forever(self, manager):
        """Test run_forever method."""
        manager.running = True

        # Simulate interrupt after short delay
        async def stop_after_delay():
            await asyncio.sleep(0.1)
            manager.running = False

        # Mock stop_servers
        manager.stop_servers = AsyncMock()

        # Run both coroutines
        await asyncio.gather(
            manager.run_forever(),
            stop_after_delay(),
        )

        manager.stop_servers.assert_called_once()

    def test_setup_signal_handlers(self, manager):
        """Test signal handler setup."""
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.add_signal_handler = Mock()

            manager.setup_signal_handlers()

            # Should set up handlers for SIGINT and SIGTERM
            assert mock_loop.return_value.add_signal_handler.call_count >= 1


class TestMainEntryPoints:
    """Test main entry points and CLI functions."""

    @pytest.mark.asyncio
    async def test_main_function(self):
        """Test main function with arguments."""
        test_args = [
            "mcp_main.py",
            "--servers",
            "neural_data",
            "--log-level",
            "DEBUG",
            "--port",
            "8081",
        ]

        with patch.object(sys, "argv", test_args):
            with patch("src.mcp.main.load_config") as mock_load_config:
                mock_load_config.return_value = {
                    "servers": {
                        "neural_data": {"port": 9001},
                        "device_control": {"port": 9002},
                    },
                    "logging": {"level": "INFO"},
                }

                with patch("src.mcp.main.MCPServerManager") as MockManager:
                    mock_instance = Mock()
                    mock_instance.start_servers = AsyncMock()
                    mock_instance.run_forever = AsyncMock()
                    MockManager.return_value = mock_instance

                    await main()

                    # Check that config was loaded
                    mock_load_config.assert_called_once()

                    # Check that manager was created with updated config
                    config = MockManager.call_args[0][0]
                    assert config["logging"]["level"] == "DEBUG"

                    # Check that servers were started with correct arguments
                    mock_instance.start_servers.assert_called_once_with(
                        ["neural_data"], 8081
                    )

    @pytest.mark.asyncio
    async def test_main_config_error(self):
        """Test main function with config loading error."""
        with patch("src.mcp.main.load_config") as mock_load_config:
            mock_load_config.side_effect = Exception("Config error")

            with patch("sys.exit") as mock_exit:
                await main()
                mock_exit.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_main_runtime_error(self):
        """Test main function with runtime error."""
        with patch("src.mcp.main.load_config") as mock_load_config:
            mock_load_config.return_value = {"servers": {}}

            with patch("src.mcp.main.MCPServerManager") as MockManager:
                mock_instance = Mock()
                mock_instance.start_servers = AsyncMock(
                    side_effect=Exception("Start failed")
                )
                MockManager.return_value = mock_instance

                with patch("sys.exit") as mock_exit:
                    await main()
                    mock_exit.assert_called_once_with(1)

    def test_cli_neural_data(self):
        """Test CLI entry point for neural data server."""
        with patch("src.mcp.main.load_config") as mock_load_config:
            mock_load_config.return_value = {"servers": {"neural_data": {"port": 9001}}}

            with patch("src.mcp.main.MCPServerManager") as MockManager:
                mock_instance = Mock()
                mock_instance.start_servers = AsyncMock()
                mock_instance.run_forever = AsyncMock()
                MockManager.return_value = mock_instance

                with patch("asyncio.run") as mock_run:
                    cli_neural_data()

                    # Check that asyncio.run was called
                    mock_run.assert_called_once()

                    # Get the coroutine that was passed to asyncio.run
                    coro = mock_run.call_args[0][0]

                    # Run it to test
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(coro)

                    # Verify correct server was started
                    mock_instance.start_servers.assert_called_once_with(["neural_data"])

    def test_cli_device_control(self):
        """Test CLI entry point for device control server."""
        with patch("src.mcp.main.load_config") as mock_load_config:
            mock_load_config.return_value = {
                "servers": {"device_control": {"port": 9002}}
            }

            with patch("src.mcp.main.MCPServerManager") as MockManager:
                mock_instance = Mock()
                mock_instance.start_servers = AsyncMock()
                mock_instance.run_forever = AsyncMock()
                MockManager.return_value = mock_instance

                with patch("asyncio.run") as mock_run:
                    cli_device_control()

                    # Check that asyncio.run was called
                    mock_run.assert_called_once()

                    # Get the coroutine that was passed to asyncio.run
                    coro = mock_run.call_args[0][0]

                    # Run it to test
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(coro)

                    # Verify correct server was started
                    mock_instance.start_servers.assert_called_once_with(
                        ["device_control"]
                    )

    def test_uvloop_import_error(self):
        """Test handling of uvloop import error."""
        # Mock uvloop import to raise ImportError
        with patch("builtins.__import__", side_effect=ImportError("No uvloop")):
            # Should not raise error, just fall back to default loop
            try:
                cli_neural_data()
            except ImportError:
                pytest.fail("Should handle uvloop ImportError gracefully")


class TestConfigLoading:
    """Test configuration loading."""

    def test_load_config_default(self):
        """Test loading default configuration."""
        from src.mcp.config import load_config

        with patch(
            "builtins.open",
            mock_open(read_data="servers:\n  neural_data:\n    port: 9001"),
        ):
            with patch("os.path.exists", return_value=True):
                config = load_config()
                assert "servers" in config
                assert "neural_data" in config["servers"]

    def test_load_config_custom_path(self):
        """Test loading configuration from custom path."""
        from src.mcp.config import load_config

        with patch("builtins.open", mock_open(read_data="test: value")):
            with patch("os.path.exists", return_value=True):
                config = load_config("/custom/path/config.yaml")
                assert "test" in config

    def test_load_config_file_not_found(self):
        """Test loading configuration when file not found."""
        from src.mcp.config import load_config

        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                load_config("/nonexistent/config.yaml")


# Helper function for mocking file open
def mock_open(read_data=""):
    """Create a mock for open() that returns read_data."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(
        return_value=MagicMock(read=MagicMock(return_value=read_data))
    )
    mock.__exit__ = MagicMock(return_value=None)
    return MagicMock(return_value=mock)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
