"""
Unit tests for PiNet MCP Server

These tests use mocking to test the tool functions without
requiring an actual PiNet API instance.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_pinet_server.pinet_client import (
    PingResult,
    WakeOnLanResult,
    ValidationError,
    NetworkError,
    AuthenticationError
)


# Mock the server module initialization to avoid loading .env during imports
@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration to avoid requiring .env file for tests"""
    with patch('mcp_pinet_server.server.Config') as mock_config_class:
        mock_config_instance = Mock()
        mock_config_instance.pinet_api_url = "http://test.example.com"
        mock_config_instance.pinet_api_key = "test_key"
        mock_config_class.from_env.return_value = mock_config_instance

        with patch('mcp_pinet_server.server.PiNetClient'):
            yield mock_config_instance


@pytest.fixture
def mock_pinet_client():
    """Fixture to provide a mocked PiNet client"""
    with patch('mcp_pinet_server.server.pinet_client') as mock:
        yield mock


class TestPingHost:
    """Tests for the ping_host tool"""

    def test_ping_host_online(self, mock_pinet_client):
        """Test ping_host when host is online"""
        from mcp_pinet_server.server import ping_host

        # Setup mock
        mock_result = PingResult(
            ip_address="8.8.8.8",
            status="online",
            is_online=True
        )
        mock_pinet_client.is_host_online.return_value = mock_result

        # Call function
        result = ping_host("8.8.8.8")

        # Assertions
        assert result == {
            "ip_address": "8.8.8.8",
            "status": "online"
        }
        mock_pinet_client.is_host_online.assert_called_once_with("8.8.8.8")

    def test_ping_host_offline(self, mock_pinet_client):
        """Test ping_host when host is offline"""
        from mcp_pinet_server.server import ping_host

        # Setup mock
        mock_result = PingResult(
            ip_address="192.168.1.100",
            status="offline",
            is_online=False
        )
        mock_pinet_client.is_host_online.return_value = mock_result

        # Call function
        result = ping_host("192.168.1.100")

        # Assertions
        assert result == {
            "ip_address": "192.168.1.100",
            "status": "offline"
        }
        mock_pinet_client.is_host_online.assert_called_once_with("192.168.1.100")

    def test_ping_host_validation_error(self, mock_pinet_client):
        """Test ping_host with invalid IP address"""
        from mcp_pinet_server.server import ping_host

        # Setup mock to raise ValidationError
        mock_pinet_client.is_host_online.side_effect = ValidationError(
            "Invalid IP address format."
        )

        # Call function
        result = ping_host("999.999.999.999")

        # Assertions
        assert result["status"] == "error"
        assert "Invalid IP address format" in result["message"]

    def test_ping_host_network_error(self, mock_pinet_client):
        """Test ping_host when PiNet API is unreachable"""
        from mcp_pinet_server.server import ping_host

        # Setup mock to raise NetworkError
        mock_pinet_client.is_host_online.side_effect = NetworkError(
            "Failed to connect to http://test.example.com"
        )

        # Call function
        result = ping_host("8.8.8.8")

        # Assertions
        assert result["status"] == "error"
        assert "PiNet API is unreachable" in result["message"]

    def test_ping_host_authentication_error(self, mock_pinet_client):
        """Test ping_host with authentication failure"""
        from mcp_pinet_server.server import ping_host

        # Setup mock to raise AuthenticationError
        mock_pinet_client.is_host_online.side_effect = AuthenticationError(
            "Invalid or missing API key"
        )

        # Call function
        result = ping_host("8.8.8.8")

        # Assertions
        assert result["status"] == "error"
        assert "Authentication failed" in result["message"]

    def test_ping_host_unexpected_error(self, mock_pinet_client):
        """Test ping_host with unexpected exception"""
        from mcp_pinet_server.server import ping_host

        # Setup mock to raise generic exception
        mock_pinet_client.is_host_online.side_effect = Exception("Unexpected error")

        # Call function
        result = ping_host("8.8.8.8")

        # Assertions
        assert result["status"] == "error"
        assert "Unexpected error" in result["message"]


class TestWakeDevice:
    """Tests for the wake_device tool"""

    def test_wake_device_success(self, mock_pinet_client):
        """Test wake_device with successful WoL packet send"""
        from mcp_pinet_server.server import wake_device

        # Setup mock
        mock_result = WakeOnLanResult(
            success=True,
            message="Wake-on-LAN packet sent to AA:BB:CC:DD:EE:FF",
            mac_address="AA:BB:CC:DD:EE:FF"
        )
        mock_pinet_client.wake_host.return_value = mock_result

        # Call function
        result = wake_device("AA:BB:CC:DD:EE:FF")

        # Assertions
        assert result == {
            "status": "success",
            "message": "Wake-on-LAN packet sent to AA:BB:CC:DD:EE:FF"
        }
        mock_pinet_client.wake_host.assert_called_once_with("AA:BB:CC:DD:EE:FF")

    def test_wake_device_failure(self, mock_pinet_client):
        """Test wake_device when WoL fails"""
        from mcp_pinet_server.server import wake_device

        # Setup mock
        mock_result = WakeOnLanResult(
            success=False,
            message="Failed to send WoL packet",
            mac_address="AA:BB:CC:DD:EE:FF"
        )
        mock_pinet_client.wake_host.return_value = mock_result

        # Call function
        result = wake_device("AA:BB:CC:DD:EE:FF")

        # Assertions
        assert result == {
            "status": "error",
            "message": "Failed to send WoL packet"
        }

    def test_wake_device_validation_error(self, mock_pinet_client):
        """Test wake_device with invalid MAC address"""
        from mcp_pinet_server.server import wake_device

        # Setup mock to raise ValidationError
        mock_pinet_client.wake_host.side_effect = ValidationError(
            "Invalid MAC address format."
        )

        # Call function
        result = wake_device("invalid-mac")

        # Assertions
        assert result["status"] == "error"
        assert "Invalid MAC address format" in result["message"]

    def test_wake_device_network_error(self, mock_pinet_client):
        """Test wake_device when PiNet API is unreachable"""
        from mcp_pinet_server.server import wake_device

        # Setup mock to raise NetworkError
        mock_pinet_client.wake_host.side_effect = NetworkError(
            "Failed to connect to http://test.example.com"
        )

        # Call function
        result = wake_device("AA:BB:CC:DD:EE:FF")

        # Assertions
        assert result["status"] == "error"
        assert "PiNet API is unreachable" in result["message"]

    def test_wake_device_authentication_error(self, mock_pinet_client):
        """Test wake_device with authentication failure"""
        from mcp_pinet_server.server import wake_device

        # Setup mock to raise AuthenticationError
        mock_pinet_client.wake_host.side_effect = AuthenticationError(
            "Invalid or missing API key"
        )

        # Call function
        result = wake_device("AA:BB:CC:DD:EE:FF")

        # Assertions
        assert result["status"] == "error"
        assert "Authentication failed" in result["message"]

    def test_wake_device_unexpected_error(self, mock_pinet_client):
        """Test wake_device with unexpected exception"""
        from mcp_pinet_server.server import wake_device

        # Setup mock to raise generic exception
        mock_pinet_client.wake_host.side_effect = Exception("Unexpected error")

        # Call function
        result = wake_device("AA:BB:CC:DD:EE:FF")

        # Assertions
        assert result["status"] == "error"
        assert "Unexpected error" in result["message"]


class TestConfigManagement:
    """Tests for configuration management"""

    def test_config_loads_from_env(self):
        """Test that configuration loads from environment variables"""
        from mcp_pinet_server.config import Config

        with patch('mcp_pinet_server.config.os.getenv') as mock_getenv:
            # Setup mock environment variables
            def getenv_side_effect(key):
                env_vars = {
                    'PINET_API_URL': 'http://192.168.1.50:5000',
                    'PINET_API_KEY': 'test_api_key_12345'
                }
                return env_vars.get(key)

            mock_getenv.side_effect = getenv_side_effect

            # Load configuration
            config = Config.from_env()

            # Assertions
            assert config.pinet_api_url == 'http://192.168.1.50:5000'
            assert config.pinet_api_key == 'test_api_key_12345'

    def test_config_missing_url(self):
        """Test that missing PINET_API_URL raises ValueError"""
        from mcp_pinet_server.config import Config

        with patch('mcp_pinet_server.config.os.getenv') as mock_getenv:
            # Setup mock to return None for URL
            def getenv_side_effect(key):
                if key == 'PINET_API_URL':
                    return None
                return 'test_key'

            mock_getenv.side_effect = getenv_side_effect

            # Should raise ValueError
            with pytest.raises(ValueError, match="PINET_API_URL"):
                Config.from_env()

    def test_config_missing_key(self):
        """Test that missing PINET_API_KEY raises ValueError"""
        from mcp_pinet_server.config import Config

        with patch('mcp_pinet_server.config.os.getenv') as mock_getenv:
            # Setup mock to return None for API key
            def getenv_side_effect(key):
                if key == 'PINET_API_KEY':
                    return None
                return 'http://test.example.com'

            mock_getenv.side_effect = getenv_side_effect

            # Should raise ValueError
            with pytest.raises(ValueError, match="PINET_API_KEY"):
                Config.from_env()

    def test_config_strips_trailing_slash(self):
        """Test that trailing slash is removed from URL"""
        from mcp_pinet_server.config import Config

        with patch('mcp_pinet_server.config.os.getenv') as mock_getenv:
            # Setup mock with trailing slash
            def getenv_side_effect(key):
                env_vars = {
                    'PINET_API_URL': 'http://192.168.1.50:5000/',
                    'PINET_API_KEY': 'test_key'
                }
                return env_vars.get(key)

            mock_getenv.side_effect = getenv_side_effect

            # Load configuration
            config = Config.from_env()

            # Should strip trailing slash
            assert config.pinet_api_url == 'http://192.168.1.50:5000'