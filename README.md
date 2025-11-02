# PiNet MCP Server

A Model Context Protocol (MCP) server that bridges Open WebUI LLMs with the PiNet API, enabling AI assistants to perform real-world network diagnostics through natural language commands.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange)](https://modelcontextprotocol.io/)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Local Development](#local-development)
  - [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Testing Tools](#testing-tools)
  - [Integration with Open WebUI](#integration-with-open-webui)
- [Available Tools](#available-tools)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

PiNet MCP Server enables LLMs (Large Language Models) to interact with network devices through the PiNet API. It exposes network diagnostic capabilities as MCP tools, allowing AI assistants to:

- Check if network hosts are online (ping)
- Wake up devices using Wake-on-LAN

**Use Case Example:**
```
User: "Check if 192.168.1.100 is online, and if not, wake it up"

LLM: *Uses ping_host tool* → Host is offline
     *Uses wake_device tool* → Wake-on-LAN packet sent successfully
```

This server acts as a bridge between:
- **Open WebUI** (or other MCP-compatible LLM interfaces)
- **PiNet API** (network diagnostics API running on Raspberry Pi)

---

## Features

- **Two MCP Tools:**
  - `ping_host` - Check network connectivity to any IP/hostname
  - `wake_device` - Send Wake-on-LAN magic packets

- **Streamable HTTP Transport:**
  - Compatible with Open WebUI
  - RESTful MCP endpoint at `/mcp`
  - Network-accessible (binds to 0.0.0.0)

- **Robust Error Handling:**
  - Clear, LLM-friendly error messages
  - Comprehensive exception handling
  - Validation for IP addresses and MAC addresses

- **Easy Deployment:**
  - Docker support with Docker Compose
  - Tailscale variant for secure remote access
  - Environment-based configuration

- **Production Ready:**
  - Full test coverage (16 unit tests)
  - Health checks
  - Resource limits
  - Log rotation

---

## Architecture

```
┌─────────────────┐
│   Open WebUI    │  (LLM Interface)
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  PiNet MCP      │  (This Server)
│    Server       │  Port 8000/5001
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   PiNet API     │  (Network API)
│ (Raspberry Pi)  │  Port 5000
└─────────────────┘
         │
         ▼
   Network Devices
```

**Data Flow:**
1. User asks LLM: "Is 192.168.1.100 online?"
2. LLM recognizes the need to use `ping_host` tool
3. Open WebUI calls MCP server via HTTP
4. MCP server forwards request to PiNet API
5. PiNet API pings the host
6. Response flows back through the chain to user

---

## Prerequisites

### Required
- **Python 3.7+** (for local development)
- **Docker** (for containerized deployment)
- **PiNet API instance** running and accessible
  - Default port: 5000
  - API key required

### For Open WebUI Integration
- **Open WebUI** installed and running
- Network connectivity to MCP server
- MCP Streamable HTTP support enabled

---

## Installation

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PiNet_MCP_Server.git
   cd PiNet_MCP_Server
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your PiNet API details
   ```

5. **Start the server:**
   ```bash
   python -m mcp_pinet_server
   ```

### Docker Deployment

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for comprehensive Docker deployment instructions.

**Quick Start:**
```bash
# Create .env file with your configuration
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f pinet-mcp-server
```

---

## Configuration

Configuration is managed via environment variables. Create a `.env` file in the project root:

```bash
# PiNet API Configuration (Required)
PINET_API_URL=http://YOUR_PINET_IP:5000
PINET_API_KEY=your_api_key_here

# MCP Server Configuration (Optional)
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0

# Logging Configuration (Optional)
LOG_LEVEL=INFO

# Tailscale Configuration (Only for docker-compose-tailscale.yml)
# TS_AUTHKEY=tskey-auth-xxxxxxxxxxxxxxxxxxxxx
```

### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PINET_API_URL` | Yes | - | Base URL of your PiNet API server (include port 5000) |
| `PINET_API_KEY` | Yes | - | API key for authenticating with PiNet API |
| `MCP_SERVER_PORT` | No | `8000` | Port for the MCP server to listen on |
| `MCP_SERVER_HOST` | No | `0.0.0.0` | Host interface to bind to (0.0.0.0 for all) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity: DEBUG, INFO, WARNING, or ERROR |

**Security Note:** Never commit your `.env` file to version control. The `.gitignore` file excludes it automatically.

---

## Usage

### Starting the Server

**Local:**
```bash
python -m mcp_pinet_server
```

**Docker:**
```bash
docker-compose up -d
```

**Expected Output:**
```
============================================================
Starting PiNet MCP Server on 0.0.0.0:8000...
============================================================

[OK] Server will be accessible at: http://0.0.0.0:8000
[OK] From other machines use: http://YOUR_PC_IP:8000

[OK] Starting uvicorn server...

INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Testing Tools

**Run the demo script:**
```bash
python demo_tools.py
```

This tests both tools with various scenarios and displays results.

**Manual testing:**
```python
from mcp_pinet_server.server import ping_host, wake_device

# Test ping
result = ping_host("8.8.8.8")
print(result)  # {"ip_address": "8.8.8.8", "status": "online"}

# Test wake-on-LAN
result = wake_device("AA:BB:CC:DD:EE:FF")
print(result)  # {"status": "success", "message": "Wake-on-LAN packet sent..."}
```

### Integration with Open WebUI

See [OPEN_WEBUI_SETUP.md](OPEN_WEBUI_SETUP.md) for detailed integration instructions.

**Quick Summary:**
1. Start the MCP server
2. Open WebUI Admin Panel → Settings → External Tools
3. Add Connection:
   - Type: `MCP Streamable HTTP`
   - URL: `http://localhost:8000/mcp` (or your server IP)
   - Auth: None
4. Save and enable the connection
5. Start chatting with your LLM - it now has network diagnostic capabilities!

**Example Prompts:**
- "Can you check if 8.8.8.8 is online?"
- "Please wake up the device with MAC address AA:BB:CC:DD:EE:FF"
- "Check if 192.168.1.100 is reachable, and if not, try to wake it"

---

## Available Tools

### 1. `ping_host`

**Description:** Check if a network host is reachable by pinging it.

**Parameters:**
- `ip_address` (string): IP address or hostname to ping
  - Supports: `8.8.8.8`, `192.168.1.100`, `google.com`

**Returns:**
```json
// Success (online)
{
  "ip_address": "8.8.8.8",
  "status": "online"
}

// Success (offline)
{
  "ip_address": "192.168.1.250",
  "status": "offline"
}

// Error
{
  "status": "error",
  "message": "Invalid IP address format"
}
```

**Use Cases:**
- Check if a device is online before attempting SSH/RDP
- Monitor network device availability
- Troubleshoot network connectivity issues

### 2. `wake_device`

**Description:** Send a Wake-on-LAN magic packet to wake up a sleeping network device.

**Parameters:**
- `mac_address` (string): MAC address of the device to wake
  - Formats accepted: `AA:BB:CC:DD:EE:FF` or `AA-BB-CC-DD-EE-FF`

**Returns:**
```json
// Success
{
  "status": "success",
  "message": "Wake-on-LAN packet sent to AA:BB:CC:DD:EE:FF"
}

// Error
{
  "status": "error",
  "message": "Invalid MAC address format"
}
```

**Requirements:**
- Target device must have Wake-on-LAN enabled in BIOS/UEFI
- Device should be connected via Ethernet (WiFi WoL is unreliable)
- Network card must support WoL

---

## Troubleshooting

### Server Won't Start

**Issue:** Server fails to start or exits immediately

**Solutions:**
1. Check `.env` file exists and has correct values
2. Verify Python version is 3.7+
3. Check port is not already in use:
   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Linux/Mac
   lsof -i :8000
   ```
4. Check PiNet API is reachable:
   ```bash
   curl http://YOUR_PINET_IP:5000/
   ```

### Open WebUI Can't Connect

**Issue:** "Connection failed" or "Server unreachable" in Open WebUI

**Solutions:**
1. Verify MCP server is running (check terminal/logs)
2. Check firewall settings allow port 8000
3. Use correct URL format: `http://SERVER_IP:8000/mcp` (note the `/mcp` endpoint)
4. Test connectivity:
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

### Tools Return Errors

**Issue:** Tools execute but return error messages

**Common Errors:**

1. **"PiNet API is unreachable"**
   - Check PiNet API is running: `curl http://YOUR_PINET_IP:5000/`
   - Verify `PINET_API_URL` in `.env`
   - Check network connectivity

2. **"Authentication failed"**
   - Verify `PINET_API_KEY` in `.env` is correct
   - Check API key hasn't expired

3. **"Invalid IP/MAC format"**
   - LLM passed incorrect format
   - This is expected validation - tools are working correctly
   - See [Debugging LLM Parameter Issues](#debugging-llm-parameter-issues) below

### Debugging LLM Parameter Issues

**Issue:** LLM sometimes sends incorrect IP/MAC address formats to the MCP server

The MCP server includes detailed logging to help you debug parameter formatting issues from the LLM.

**Enable Debug Logging:**

1. **Edit your `.env` file:**
   ```bash
   LOG_LEVEL=DEBUG
   ```

2. **Restart the server:**
   ```bash
   python -m mcp_pinet_server
   ```

3. **Watch the logs when LLM calls a tool:**
   ```
   2025-11-02 14:30:45 [INFO] PiNet-MCP: ======================================================================
   2025-11-02 14:30:45 [INFO] PiNet-MCP: TOOL CALL: ping_host
   2025-11-02 14:30:45 [INFO] PiNet-MCP:   Parameter received from LLM:
   2025-11-02 14:30:45 [INFO] PiNet-MCP:     ip_address: '192.168.1.100 ' (type: str, length: 15)
   2025-11-02 14:30:45 [INFO] PiNet-MCP:     repr: '192.168.1.100 '
   2025-11-02 14:30:45 [ERROR] PiNet-MCP:   ValidationError: Invalid IP address format
   2025-11-02 14:30:45 [INFO] PiNet-MCP: ======================================================================
   ```

**What to Look For:**
- **Trailing spaces**: `'192.168.1.1 '` - LLM added extra whitespace
- **Wrong separators**: `'192-168-1-1'` - Dashes instead of dots
- **Quotes included**: `'"192.168.1.1"'` - LLM wrapped in quotes
- **Special characters**: `'192.168.1.1\n'` - Newlines or other hidden chars
- **MAC format issues**: `'AA BB CC DD EE FF'` - Spaces instead of colons/dashes

**Save Logs to File:**
```bash
# Both console and file
python -m mcp_pinet_server 2>&1 | tee mcp_debug.log

# File only
python -m mcp_pinet_server > mcp_debug.log 2>&1
```

**Available Log Levels:**
- `DEBUG` - Most detailed, shows all API calls and internal operations
- `INFO` - Normal operations, tool calls and responses (default)
- `WARNING` - Only warnings and errors
- `ERROR` - Only error messages

### Docker Container Issues

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md#troubleshooting) for Docker-specific troubleshooting.

---

## Project Structure

```
PiNet_MCP_Server/
├── src/
│   └── mcp_pinet_server/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point for module execution
│       ├── server.py            # Main MCP server with tools
│       ├── config.py            # Configuration management
│       └── pinet_client.py      # PiNet API client
├── tests/
│   ├── __init__.py
│   └── test_server.py           # Unit tests
├── docs/
│   ├── IMPLEMENTATION_PLAN.md   # Development roadmap
│   ├── SRS.md                   # Software Requirements Specification
│   └── PiNet_API_README.md      # PiNet API documentation
├── .env.example                 # Environment template
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
├── demo_tools.py               # Demo script
├── docker-compose.yml          # Standard Docker deployment
├── docker-compose-tailscale.yml # Tailscale deployment
├── Dockerfile                  # Container image definition
├── DOCKER_DEPLOYMENT.md        # Docker guide
├── OPEN_WEBUI_SETUP.md        # Open WebUI integration guide
├── pyproject.toml             # Python project configuration
└── README.md                  # This file
```

---

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_pinet_server

# Run specific test
pytest tests/test_server.py::test_ping_host_online
```

### Code Style

```bash
# Format code
black src/ tests/

# Type checking
mypy src/
```

### Adding New Tools

1. Add tool function in `src/mcp_pinet_server/server.py`:
   ```python
   @mcp.tool()
   def your_tool(param: str) -> dict:
       """Tool description for LLM"""
       try:
           # Implementation
           return {"status": "success", "result": "..."}
       except Exception as e:
           return {"status": "error", "message": str(e)}
   ```

2. Add tests in `tests/test_server.py`
3. Update documentation

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Add tests for new features
   - Update documentation
   - Follow existing code style
4. **Run tests:**
   ```bash
   pytest
   ```
5. **Commit with clear messages:**
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include unit tests for new functionality
- Update README if adding features
- Keep commits atomic and focused

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Integrates with [Open WebUI](https://github.com/open-webui/open-webui)
- Connects to [PiNet API](docs/PiNet_API_README.md)

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [OPEN_WEBUI_SETUP.md](OPEN_WEBUI_SETUP.md) for integration issues
3. Review [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for Docker issues
4. Check server logs for error messages
5. Verify PiNet API connectivity

### For Developers Building Similar MCP Servers

If you're implementing your own MCP server for Open WebUI, see our comprehensive implementation guide:

📘 **[MCP + Open WebUI Integration Guide](docs/MCP_OPEN_WEBUI_INTEGRATION_GUIDE.md)**

This guide documents:
- ✅ What works and what doesn't (transport mechanisms, network configuration)
- ✅ All problems encountered during development and their solutions
- ✅ Step-by-step implementation with code examples
- ✅ Testing strategy before Open WebUI integration
- ✅ Common pitfalls and how to avoid them

Based on real-world implementation experience with this project.

---

## Roadmap

Future enhancements (not in current scope):

- [ ] Add more PiNet API endpoints as tools
- [ ] Implement caching for frequent ping requests
- [ ] Add metrics/monitoring endpoint
- [ ] Support multiple PiNet API instances
- [ ] Add authentication for MCP server
- [ ] Create web dashboard
- [ ] Add CI/CD pipeline
