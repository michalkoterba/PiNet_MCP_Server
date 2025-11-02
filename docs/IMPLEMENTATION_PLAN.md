# Implementation Plan
## PiNet MCP Server

| | |
| :--- | :--- |
| **Version:** | 1.0 |
| **Status:** | Ready for Implementation |
| **Date:** | 02 November 2025 |

---

## Overview

This document provides a step-by-step implementation plan for the PiNet MCP Server project, as specified in the [SRS.md](SRS.md). The server will bridge Open Webui LLM with the PiNet API using the FastMCP framework.

---

## Implementation Phases

### Phase 1: Project Setup & Structure

#### Task 1.1: Initialize Project Structure
- [ ] Create the `src` layout directory structure:
  ```
  PiNet_MCP_Server/
  ├── src/
  │   └── mcp_pinet_server/
  │       ├── __init__.py
  │       └── server.py
  ├── tests/
  │   ├── __init__.py
  │   └── test_server.py
  ├── .dockerignore
  ├── .env.example
  ├── .gitignore
  ├── Dockerfile
  ├── pyproject.toml
  └── README.md
  ```

#### Task 1.2: Create Configuration Files
- [x] Create `.gitignore` with:
  - `.env`
  - `__pycache__/`
  - `*.pyc`
  - `venv/`
  - `.pytest_cache/`
  - `*.egg-info/`

- [x] Create `.env.example` with template:
  ```bash
  # PiNet API Configuration
  PINET_API_URL=http://192.168.1.50:5000
  PINET_API_KEY=your_api_key_here

  # MCP Server Configuration (Optional)
  MCP_SERVER_PORT=8000
  ```

- [x] Create `.dockerignore` with:
  - `.env`
  - `.git/`
  - `__pycache__/`
  - `*.pyc`
  - `tests/`
  - `docs/`
  - `.gitignore`
  - `README.md`

#### Task 1.3: Create `pyproject.toml`
- [x] Define project metadata:
  - Name: `pinet-mcp-server`
  - Version: `0.1.0`
  - Python version requirement: `>=3.7`

- [x] Add dependencies:
  - `mcp` (FastMCP SDK)
  - `python-dotenv` (environment variable management)
  - `requests` (HTTP client for PiNet API)

- [x] Add optional dev dependencies:
  - `pytest` (testing)
  - `pytest-asyncio` (async testing)
  - `black` (code formatting)
  - `mypy` (type checking)

**Sample pyproject.toml:**
```toml
[project]
name = "pinet-mcp-server"
version = "0.1.0"
description = "MCP server for PiNet API network diagnostics"
requires-python = ">=3.7"
dependencies = [
    "mcp>=0.1.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

---

### Phase 2: Core Implementation

#### Task 2.1: Copy PiNet Client Library
- [x] Copy `pinet_client.py` into `src/mcp_pinet_server/` directory
- [X] Verify all imports work correctly
- [X] Update any relative imports if needed

#### Task 2.2: Implement Configuration Management (`src/mcp_pinet_server/config.py`)
- [X] Create a `config.py` module to handle environment variables
- [X] Load `.env` file using `python-dotenv`
- [X] Validate required variables:
  - `PINET_API_URL` (required)
  - `PINET_API_KEY` (required)
- [X] Provide clear error messages for missing configuration
- [X] Export configuration as a dataclass or dictionary

**Example structure:**
```python
# src/mcp_pinet_server/config.py
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    pinet_api_url: str
    pinet_api_key: str

    @classmethod
    def from_env(cls):
        url = os.getenv('PINET_API_URL')
        key = os.getenv('PINET_API_KEY')

        if not url or not key:
            raise ValueError("Missing required env vars: PINET_API_URL, PINET_API_KEY")

        return cls(pinet_api_url=url, pinet_api_key=key)
```

#### Task 2.3: Initialize FastMCP Server (`src/mcp_pinet_server/server.py`)
- [X] Import FastMCP: `from mcp import FastMCP`
- [X] Create MCP instance: `mcp = FastMCP("PiNet MCP Server")`
- [X] Load configuration from `config.py`
- [X] Initialize PiNetClient with configuration
- [X] Add error handling for initialization failures

**Example structure:**
```python
# src/mcp_pinet_server/server.py
from mcp import FastMCP
from .config import Config
from .pinet_client import PiNetClient, PiNetAPIError

# Initialize MCP server
mcp = FastMCP("PiNet MCP Server")

# Load configuration
config = Config.from_env()

# Initialize PiNet API client
pinet_client = PiNetClient(
    base_url=config.pinet_api_url,
    api_key=config.pinet_api_key
)
```

---

### Phase 3: Tool Implementation

#### Task 3.1: Implement Ping Tool (FR-3.1)
- [X] Create `@mcp.tool` decorated function for ping
- [X] Function name: `ping_host`
- [X] Parameter: `ip_address: str`
- [X] Call `pinet_client.is_host_online(ip_address)`
- [X] Return structured JSON response:
  - Success (online): `{"ip_address": "...", "status": "online"}`
  - Success (offline): `{"ip_address": "...", "status": "offline"}`
  - Error: `{"status": "error", "message": "..."}`
- [X] Handle all exceptions from PiNetClient:
  - `AuthenticationError`
  - `ValidationError`
  - `NetworkError`
  - Generic exceptions
- [X] Add comprehensive docstring for LLM understanding

**Example implementation:**
```python
@mcp.tool
def ping_host(ip_address: str) -> dict:
    """
    Check if a host is reachable on the network by pinging it.

    Args:
        ip_address: The IP address or hostname to ping (e.g., "8.8.8.8" or "192.168.1.100")

    Returns:
        A dictionary with the ping result:
        - {"ip_address": "8.8.8.8", "status": "online"} if the host responds
        - {"ip_address": "192.168.1.100", "status": "offline"} if the host doesn't respond
        - {"status": "error", "message": "..."} if an error occurs
    """
    try:
        result = pinet_client.is_host_online(ip_address)
        return {
            "ip_address": result.ip_address,
            "status": result.status
        }
    except ValidationError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except NetworkError as e:
        return {
            "status": "error",
            "message": f"PiNet API is unreachable: {str(e)}"
        }
    except AuthenticationError as e:
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
```

#### Task 3.2: Implement Wake-on-LAN Tool (FR-3.2)
- [x] Create `@mcp.tool` decorated function for WoL
- [x] Function name: `wake_device`
- [x] Parameter: `mac_address: str`
- [x] Call `pinet_client.wake_host(mac_address)`
- [x] Return structured JSON response:
  - Success: `{"status": "success", "message": "Wake-on-LAN packet sent to ..."}`
  - Error: `{"status": "error", "message": "..."}`
- [x] Handle all exceptions from PiNetClient
- [x] Add comprehensive docstring for LLM understanding

**Example implementation:**
```python
@mcp.tool
def wake_device(mac_address: str) -> dict:
    """
    Send a Wake-on-LAN (WoL) magic packet to wake up a sleeping network device.

    Args:
        mac_address: The MAC address of the device to wake (e.g., "AA:BB:CC:DD:EE:FF")

    Returns:
        A dictionary with the result:
        - {"status": "success", "message": "Wake-on-LAN packet sent to ..."} on success
        - {"status": "error", "message": "..."} if an error occurs

    Note:
        The target device must:
        - Have Wake-on-LAN enabled in BIOS/UEFI
        - Be connected via Ethernet (WiFi WoL is unreliable)
        - Have a network card that supports WoL
    """
    try:
        result = pinet_client.wake_host(mac_address)
        if result.success:
            return {
                "status": "success",
                "message": result.message
            }
        else:
            return {
                "status": "error",
                "message": result.message
            }
    except ValidationError as e:
        return {
            "status": "error",
            "message": str(e)
        }
    except NetworkError as e:
        return {
            "status": "error",
            "message": f"PiNet API is unreachable: {str(e)}"
        }
    except AuthenticationError as e:
        return {
            "status": "error",
            "message": f"Authentication failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
```

#### Task 3.3: Add Main Entry Point
- [x] Add server startup code using SSE transport
- [x] Configure for remote HTTP connections
- [x] Add proper error handling for server startup

**Example:**
```python
if __name__ == "__main__":
    # Run MCP server with SSE transport for Open Webui
    mcp.run(transport="sse")
```

---

### Phase 4: Dockerization (NFR-4.3)

#### Task 4.1: Create Dockerfile
- [ ] Use official Python 3.9+ base image (lightweight)
- [ ] Set working directory to `/app`
- [ ] Copy only necessary files (use `.dockerignore`)
- [ ] Install dependencies from `pyproject.toml`
- [ ] Install the package in editable mode or via pip
- [ ] Set environment variables (document required ones)
- [ ] Expose the MCP server port (default: 8000)
- [ ] Set entrypoint to run the server

**Example Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Expose port for SSE transport
EXPOSE 8000

# Set environment variables (these should be overridden at runtime)
ENV PINET_API_URL=""
ENV PINET_API_KEY=""

# Run the MCP server
CMD ["python", "-m", "mcp_pinet_server.server"]
```

#### Task 4.2: Update `__init__.py` for Module Execution
- [ ] Create `src/mcp_pinet_server/__init__.py`
- [ ] Add version information
- [ ] Ensure module can be run with `python -m`

**Example:**
```python
# src/mcp_pinet_server/__init__.py
__version__ = "0.1.0"
```

#### Task 4.3: Create `__main__.py` for Module Entry Point
- [ ] Create `src/mcp_pinet_server/__main__.py`
- [ ] Import and run server

**Example:**
```python
# src/mcp_pinet_server/__main__.py
from .server import mcp

if __name__ == "__main__":
    mcp.run(transport="sse")
```

---

### Phase 5: Testing & Validation

#### Task 5.1: Manual Testing with MCP Inspector
- [x] Install MCP development tools: `pip install mcp[dev]`
- [x] Run server in development mode: `mcp dev src/mcp_pinet_server/server.py`
- [ ] Test ping tool with various inputs:
  - Valid online IP (e.g., `8.8.8.8`)
  - Valid offline IP (e.g., `192.168.1.200`)
  - Invalid IP format (e.g., `999.999.999.999`)
  - Hostname (e.g., `google.com`)
- [x] Test wake_device tool with various inputs:
  - Valid MAC address (e.g., `AA:BB:CC:DD:EE:FF`)
  - Invalid MAC format (e.g., `invalid-mac`)
- [x] Verify error handling:
  - Incorrect API key
  - Unreachable PiNet API (stop the API)
  - Network timeouts

#### Task 5.2: Create Unit Tests
- [x] Create `tests/test_server.py`
- [x] Mock PiNetClient responses
- [x] Test successful ping (online/offline)
- [x] Test successful wake_device
- [x] Test error scenarios (auth, validation, network)
- [x] Verify JSON response structure

#### Task 5.3: Integration Testing
- [x] Test with actual PiNet API instance
- [x] Verify real ping operations
- [x] Verify real WoL operations (if possible)
- [x] Test concurrent requests
- [x] Test with Open Webui (end-to-end)

---

### Phase 6: Documentation

#### Task 6.1: Create README.md
- [x] Project overview and purpose
- [x] Features list
- [x] Prerequisites
- [x] Installation instructions (local & Docker)
- [x] Configuration guide (.env setup)
- [x] Usage examples with MCP Inspector
- [x] Integration with Open Webui
- [x] Troubleshooting guide
- [x] Contributing guidelines
- [x] License information

#### Task 6.2: Code Documentation
- [x] Add docstrings to all functions
- [x] Add type hints throughout
- [x] Add inline comments for complex logic
- [x] Document configuration options
- [x] Document error responses

#### Task 6.3: Create Deployment Guide
- [x] Docker build instructions
- [x] Docker run command with environment variables
- [x] Docker Compose example (optional)
- [x] Integration with Open Webui deployment
- [x] Security considerations

---

### Phase 7: Deployment & Release

#### Task 7.1: Build Docker Image
- [ ] Build image: `docker build -t pinet-mcp-server:latest .`
- [ ] Test container locally
- [ ] Verify environment variable passing
- [ ] Test network connectivity to PiNet API

#### Task 7.2: Create Docker Compose Configuration (Optional)
- [ ] Create `docker-compose.yml` for easy deployment
- [ ] Include environment variable template
- [ ] Add network configuration
- [ ] Document usage

**Example docker-compose.yml:**
```yaml
version: '3.8'

services:
  pinet-mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PINET_API_URL=${PINET_API_URL}
      - PINET_API_KEY=${PINET_API_KEY}
    restart: unless-stopped
```

#### Task 7.3: Final Testing
- [ ] End-to-end test with Open Webui
- [ ] Test LLM natural language commands:
  - "Check if 8.8.8.8 is online"
  - "Wake up the device with MAC address AA:BB:CC:DD:EE:FF"
  - "Ping 192.168.1.100"
- [ ] Verify error messages are LLM-friendly
- [ ] Test server restart/recovery

---

## Error Handling Checklist (NFR-4.5)

Ensure all tools handle these scenarios gracefully:

- [x] **PiNet API unreachable** → Return: `{"status": "error", "message": "PiNet API is unreachable"}`
- [x] **Authentication failure (401)** → Return: `{"status": "error", "message": "Authentication failed"}`
- [x] **Validation error (400)** → Return: `{"status": "error", "message": "<specific validation error>"}`
- [x] **Network timeout** → Return: `{"status": "error", "message": "Request timeout..."}`
- [x] **Invalid input format** → Return: `{"status": "error", "message": "<specific error>"}`
- [x] **Generic exceptions** → Return: `{"status": "error", "message": "Unexpected error..."}`

---

## Security Considerations (NFR-4.1)

- [ ] MCP server has no authentication (trusted internal service)
- [ ] API key stored in environment variable (not hardcoded)
- [ ] `.env` file in `.gitignore` (never committed)
- [ ] Docker container uses environment variables at runtime
- [ ] Network security managed at infrastructure level:
  - Private Docker network
  - Firewall rules
  - Network segmentation

---

## Performance Considerations

- [ ] Use connection pooling in PiNetClient (already implemented via `requests.Session`)
- [ ] Set reasonable timeout values (default: 10 seconds)
- [ ] Handle concurrent requests gracefully
- [ ] Log errors for debugging (consider adding logging module)

---

## Future Enhancements (Out of Current Scope)

- [ ] Add more PiNet API endpoints as tools
- [ ] Implement caching for frequent ping requests
- [ ] Add metrics/monitoring endpoint
- [ ] Support multiple PiNet API instances
- [ ] Add authentication for MCP server (if needed)
- [ ] Create comprehensive test suite
- [ ] Add CI/CD pipeline

---

## Implementation Order Recommendation

1. **Phase 1** (Setup) → Essential foundation
2. **Phase 2** (Core Implementation) → Server initialization
3. **Phase 3** (Tool Implementation) → Main functionality
4. **Phase 5.1** (MCP Inspector Testing) → Early validation
5. **Phase 4** (Dockerization) → Deployment packaging
6. **Phase 5.2-5.3** (Comprehensive Testing) → Quality assurance
7. **Phase 6** (Documentation) → User guidance
8. **Phase 7** (Deployment) → Production release

---

## Success Criteria

The implementation is complete when:

- ✅ Both tools (`ping_host` and `wake_device`) work correctly
- ✅ Error handling is robust and returns clear messages
- ✅ Configuration via environment variables works
- ✅ Docker container builds and runs successfully
- ✅ Integration with Open Webui is verified
- ✅ MCP Inspector shows tools correctly
- ✅ Documentation is complete and accurate
- ✅ All functional requirements (FR-3.1, FR-3.2) are met
- ✅ All non-functional requirements (NFR-4.1 through NFR-4.5) are met

---

## Notes

- Keep the implementation simple and focused on the requirements
- Prioritize error handling and clear error messages (critical for LLM understanding)
- Test thoroughly with MCP Inspector before Open Webui integration
- Document any deviations from the SRS
- Keep security in mind (API key management)