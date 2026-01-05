"""Unit tests for the process_utils module."""

import os
import signal
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest
import typer

from raindropio_mcp.utils.process_utils import ServerManager


def test_server_manager_init():
    """Test ServerManager initialization."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            manager = ServerManager("test_project")
            assert manager.project_name == "test_project"
            assert manager.pid_file == Path("/home/testuser/.cache/mcp/test_project.pid")
            # Verify that mkdir was called to create the directory
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_server_manager_pid_file_creation():
    """Test PID file creation during initialization."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            manager = ServerManager("test_project")

            # Verify that mkdir was called to create the directory
            expected_path = Path("/home/testuser/.cache/mcp")
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_pid_file_not_exists():
    """Test get_pid when PID file doesn't exist."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = False
            manager.pid_file = mock_pid_file

            assert manager.get_pid() is None
            mock_pid_file.exists.assert_called_once()


def test_get_pid_file_empty():
    """Test get_pid when PID file is empty."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = ""
            manager.pid_file = mock_pid_file

            assert manager.get_pid() is None
            mock_pid_file.exists.assert_called_once()
            mock_pid_file.read_text.assert_called_once()


def test_get_pid_file_invalid_content():
    """Test get_pid when PID file contains invalid content."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "invalid"
            manager.pid_file = mock_pid_file

            assert manager.get_pid() is None
            mock_pid_file.exists.assert_called_once()
            mock_pid_file.read_text.assert_called_once()


def test_get_pid_file_valid_content():
    """Test get_pid when PID file contains valid content."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            assert manager.get_pid() == 12345
            mock_pid_file.exists.assert_called_once()
            mock_pid_file.read_text.assert_called_once()


@patch("raindropio_mcp.utils.process_utils.os.kill")
def test_is_running_true(mock_kill):
    """Test is_running when process is running."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            mock_kill.return_value = None  # No exception means process exists
            assert manager.is_running() is True
            mock_kill.assert_called_once_with(12345, 0)


@patch("raindropio_mcp.utils.process_utils.os.kill")
def test_is_running_false_no_pid(mock_kill):
    """Test is_running when no PID is found."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = ""  # Empty content
            manager.pid_file = mock_pid_file

            assert manager.is_running() is False
            mock_kill.assert_not_called()


@patch("raindropio_mcp.utils.process_utils.os.kill")
def test_is_running_false_exception(mock_kill):
    """Test is_running when process is not running (exception raised)."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            mock_kill.side_effect = OSError("No such process")
            assert manager.is_running() is False
            mock_kill.assert_called_once_with(12345, 0)


@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_start_server_already_running(mock_echo):
    """Test start_server when server is already running."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return True
            with patch.object(manager, 'is_running', return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    manager.start_server("localhost", 8000, False, False)

                mock_echo.assert_called_once_with("Server 'test_project' is already running.")
                assert exc_info.value.code == 0


@patch("raindropio_mcp.utils.process_utils.subprocess.Popen")
@patch("raindropio_mcp.utils.process_utils.os.environ.copy", return_value={})
@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_start_server_success(mock_echo, mock_environ, mock_popen):
    """Test start_server success case."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            mock_process = Mock()
            mock_process.pid = 98765
            mock_popen.return_value = mock_process

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            manager.pid_file = mock_pid_file

            with patch.object(manager, 'is_running', return_value=False):
                manager.start_server("localhost", 8000, True, False)

                # Verify environment variables were set
                mock_environ.assert_called()
                mock_popen.assert_called_once()
                args, kwargs = mock_popen.call_args
                env = kwargs.get('env', {})
                assert env.get("MCP_SERVER_HOST") == "localhost"
                assert env.get("MCP_SERVER_PORT") == "8000"
                assert env.get("MCP_DEBUG") == "true"
                assert env.get("MCP_RELOAD") == "false"

                # Verify PID file was written
                mock_pid_file.write_text.assert_called_once_with("98765")

                # Verify echo was called with correct message
                mock_echo.assert_called_with("Started UniFi MCP server on localhost:8000 (PID: 98765)")


@patch("raindropio_mcp.utils.process_utils.subprocess.Popen")
@patch("raindropio_mcp.utils.process_utils.os.environ.copy", return_value={})
@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_start_server_pid_write_error(mock_echo, mock_environ, mock_popen):
    """Test start_server when PID file write fails."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            mock_process = Mock()
            mock_process.pid = 98765
            mock_popen.return_value = mock_process

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.write_text.side_effect = OSError("Permission denied")
            manager.pid_file = mock_pid_file

            with patch.object(manager, 'is_running', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    manager.start_server("localhost", 8000, False, False)

                # Verify process was killed
                mock_process.kill.assert_called_once()
                assert exc_info.value.code == 1


@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_stop_server_not_running(mock_echo):
    """Test stop_server when server is not running."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return False
            with patch.object(manager, 'is_running', return_value=False):
                manager.stop_server()

                mock_echo.assert_any_call("Server 'test_project' is not running.")


@patch("raindropio_mcp.utils.process_utils.os.kill")
@patch("raindropio_mcp.utils.process_utils.time.sleep")
@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_stop_server_success(mock_echo, mock_sleep, mock_kill):
    """Test stop_server success case."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return True
            with patch.object(manager, 'is_running', return_value=True):
                with patch.object(mock_pid_file, 'unlink') as mock_unlink:
                    manager.stop_server()

                    mock_echo.assert_any_call("Stopping server 'test_project' (PID: 12345)...")
                    mock_kill.assert_called_once_with(12345, signal.SIGTERM)
                    mock_sleep.assert_called_once_with(1)
                    mock_unlink.assert_called_once()


@patch("raindropio_mcp.utils.process_utils.os.kill")
@patch("raindropio_mcp.utils.process_utils.time.sleep")
@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_stop_server_kill_error(mock_echo, mock_sleep, mock_kill):
    """Test stop_server when kill raises an error."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return True
            with patch.object(manager, 'is_running', return_value=True):
                with patch.object(mock_pid_file, 'unlink') as mock_unlink:
                    # Mock the kill to raise an exception, but the suppress context manager
                    # should catch it and allow sleep to continue
                    with patch('raindropio_mcp.utils.process_utils.suppress') as mock_suppress:
                        # Create a mock context manager that will call the block
                        mock_ctx = Mock()
                        mock_suppress.return_value = mock_ctx
                        enter_mock = Mock()
                        exit_mock = Mock(return_value=True)  # Suppress exceptions
                        mock_ctx.__enter__ = enter_mock
                        mock_ctx.__exit__ = exit_mock

                        manager.stop_server()  # Should not raise exception

                        mock_echo.assert_any_call("Stopping server 'test_project' (PID: 12345)...")
                        mock_kill.assert_called_once_with(12345, signal.SIGTERM)
                        # Sleep should still be called even if kill raises an exception
                        mock_sleep.assert_called_once_with(1)
                        # Unlink should still happen
                        mock_unlink.assert_called_once()

                        # Verify that suppress was called with OSError
                        mock_suppress.assert_called_once_with(OSError)


@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_get_status_running(mock_echo):
    """Test get_status when server is running."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return True
            with patch.object(manager, 'is_running', return_value=True):
                manager.get_status()

                mock_echo.assert_called_once_with("UniFi MCP server is RUNNING (PID: 12345)")


@patch("raindropio_mcp.utils.process_utils.typer.echo")
def test_get_status_stopped(mock_echo):
    """Test get_status when server is stopped."""
    with patch("pathlib.Path.home", return_value=Path("/home/testuser")):
        with patch("pathlib.Path.mkdir"):
            manager = ServerManager("test_project")

            # Create a mock Path object for the pid_file
            mock_pid_file = Mock()
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "12345"
            manager.pid_file = mock_pid_file

            # Mock is_running to return False
            with patch.object(manager, 'is_running', return_value=False):
                manager.get_status()

                mock_echo.assert_called_once_with("UniFi MCP server is STOPPED.")
