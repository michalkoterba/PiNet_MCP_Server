"""
PiNet MCP Server - Main application entry point

This module implements the FastMCP server that bridges LLM applications
with the PiNet API for network diagnostics and control.
"""

import logging
import json
import os
from mcp.server import FastMCP
from .config import Config
from .pinet_client import (
    PiNetClient,
    PiNetAPIError,
    AuthenticationError,
    ValidationError,
    NetworkError
)

# Configure logging with environment variable support
log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("PiNet-MCP")
logger.info(f"Logging level set to: {log_level_name}")

# Initialize MCP server
mcp = FastMCP("PiNet MCP Server")

# Load configuration and initialize PiNet API client
try:
    config = Config.from_env()
    print(f"[OK] Configuration loaded: {config}")

    pinet_client = PiNetClient(
        base_url=config.pinet_api_url,
        api_key=config.pinet_api_key,
        timeout=10
    )
    print(f"[OK] PiNet API client initialized for {config.pinet_api_url}")

except ValueError as e:
    print(f"[ERROR] Configuration error: {e}")
    raise
except Exception as e:
    print(f"[ERROR] Initialization error: {e}")
    raise


@mcp.tool()
def ping_host(ip_address: str) -> dict:
    """
    Check if a host is reachable on the network by pinging it.

    This tool uses ICMP ping to determine if a network device is online.
    It works with both internet hosts and local network addresses (e.g., 192.168.x.x, 10.x.x.x).
    Perfect for checking if devices on your local network are online and responsive.

    The tool communicates with the PiNet API to perform the actual ping operation.

    Args:
        ip_address: The IP address or hostname to ping.
                   Works with:
                   - Local network addresses: "192.168.1.100", "192.168.0.1", "10.0.0.1"
                   - Internet addresses: "8.8.8.8", "1.1.1.1"
                   - Hostnames: "google.com", "router.local"

    Returns:
        A dictionary with the ping result:
        - {"ip_address": "192.168.1.100", "status": "online"} if the host responds
        - {"ip_address": "192.168.1.200", "status": "offline"} if the host doesn't respond
        - {"status": "error", "message": "..."} if an error occurs

    Examples:
        >>> ping_host("192.168.1.1")
        {"ip_address": "192.168.1.1", "status": "online"}

        >>> ping_host("192.168.0.100")
        {"ip_address": "192.168.0.100", "status": "offline"}

        >>> ping_host("8.8.8.8")
        {"ip_address": "8.8.8.8", "status": "online"}
    """
    # Log incoming request from LLM
    logger.info("="*70)
    logger.info("TOOL CALL: ping_host")
    logger.info(f"  Parameter received from LLM:")
    logger.info(f"    ip_address: '{ip_address}' (type: {type(ip_address).__name__}, length: {len(ip_address)})")
    logger.info(f"    repr: {repr(ip_address)}")

    try:
        logger.debug(f"  Calling PiNet API: is_host_online('{ip_address}')")
        result = pinet_client.is_host_online(ip_address)

        response = {
            "ip_address": result.ip_address,
            "status": result.status
        }
        logger.info(f"  Response: {json.dumps(response)}")
        logger.info("="*70)
        return response

    except ValidationError as e:
        logger.error(f"  ValidationError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Invalid IP address format: {str(e)}"
        }
    except NetworkError as e:
        logger.error(f"  NetworkError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"PiNet API is unreachable: {str(e)}"
        }
    except AuthenticationError as e:
        logger.error(f"  AuthenticationError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"  Unexpected error: {str(e)}", exc_info=True)
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def wake_device(mac_address: str) -> dict:
    """
    Send a Wake-on-LAN (WoL) magic packet to wake up a sleeping network device.

    This tool sends a special network packet that can wake up computers and devices
    that support Wake-on-LAN. The device must be configured to respond to WoL packets.

    Args:
        mac_address: The MAC address of the device to wake.
                    Accepts both colon-separated and dash-separated formats:
                    - Colon format: "AA:BB:CC:DD:EE:FF"
                    - Dash format: "AA-BB-CC-DD-EE-FF"
                    Both formats work identically.

    Returns:
        A dictionary with the result:
        - {"status": "success", "message": "Wake-on-LAN packet sent to ..."} on success
        - {"status": "error", "message": "..."} if an error occurs

    Important Notes:
        The target device must meet these requirements:
        - Have Wake-on-LAN enabled in BIOS/UEFI settings
        - Be connected via Ethernet (WiFi WoL is unreliable)
        - Have a network card that supports Wake-on-LAN
        - Be on the same local network/subnet

    Examples:
        >>> wake_device("AA:BB:CC:DD:EE:FF")
        {"status": "success", "message": "Wake-on-LAN packet sent to AA:BB:CC:DD:EE:FF"}

        >>> wake_device("AA-BB-CC-DD-EE-FF")
        {"status": "success", "message": "Wake-on-LAN packet sent to AA-BB-CC-DD-EE-FF"}

        >>> wake_device("invalid-mac")
        {"status": "error", "message": "Invalid MAC address format"}
    """
    # Log incoming request from LLM
    logger.info("="*70)
    logger.info("TOOL CALL: wake_device")
    logger.info(f"  Parameter received from LLM:")
    logger.info(f"    mac_address: '{mac_address}' (type: {type(mac_address).__name__}, length: {len(mac_address)})")
    logger.info(f"    repr: {repr(mac_address)}")

    try:
        logger.debug(f"  Calling PiNet API: wake_host('{mac_address}')")
        result = pinet_client.wake_host(mac_address)

        if result.success:
            response = {
                "status": "success",
                "message": result.message
            }
            logger.info(f"  Response: {json.dumps(response)}")
            logger.info("="*70)
            return response
        else:
            response = {
                "status": "error",
                "message": result.message
            }
            logger.warning(f"  Response (failed): {json.dumps(response)}")
            logger.info("="*70)
            return response

    except ValidationError as e:
        logger.error(f"  ValidationError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Invalid MAC address format: {str(e)}"
        }
    except NetworkError as e:
        logger.error(f"  NetworkError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"PiNet API is unreachable: {str(e)}"
        }
    except AuthenticationError as e:
        logger.error(f"  AuthenticationError: {str(e)}")
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"  Unexpected error: {str(e)}", exc_info=True)
        logger.info("="*70)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    import os

    # Get port from environment or use default
    port = int(os.getenv('MCP_SERVER_PORT', '5001'))

    # Run MCP server with streamable-http transport for Open Webui
    print("\n" + "="*60)
    print(f"Starting PiNet MCP Server on port {port}...")
    print("="*60 + "\n")

    # Use streamable-http transport (compatible with Open WebUI)
    import uvicorn
    from starlette.applications import Starlette
    from mcp.server.sse import SseServerTransport

    # Create transport and run
    sse = SseServerTransport("/messages")
    app = sse.create_app(mcp._server)

    print(f"[OK] Server ready at: http://localhost:{port}")
    print(f"[OK] API Base URL: http://localhost:{port}/messages")
    print()

    uvicorn.run(app, host="0.0.0.0", port=port)