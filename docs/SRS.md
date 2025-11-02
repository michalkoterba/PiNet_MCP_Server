# Software Requirements Specification (SRS)
## for MCP PiNet Server

| | |
| :--- | :--- |
| **Version:** | 1.0 |
| **Status:** | Draft |
| **Date:** | 02 November 2025 |

---

## 1. Introduction

### 1.1 Project Purpose
The "MCP PiNet Server" is a Python server that acts as a bridge between a Large Language Model (LLM) framework (specifically Open Webui) and the existing `PiNet API`.

The primary goal is to expose the `PiNet API`'s network diagnostic functions (`ping` and `wol`) as "tools" compatible with the MCP (Modular Component Platform) framework. This will allow an LLM to understand and execute these network tasks via natural language commands issued within Open Webui.

### 1.2 Intended Audience
This document is for the project developer(s) and maintainers. It defines the requirements, features, and constraints of the MCP server.

### 1.3 Project Scope

#### In Scope
* Development of a Python server using the `FastMCP` framework.
* Implementation of "tools" corresponding to the `PiNet API`'s `ping` and `wol` endpoints.
* Integration of the `pinet_client.py` library to communicate with the `PiNet API`.
* Configuration management via environment variables and a `.env` file.
* Creation of a `Dockerfile` for containerized deployment.
* Adherence to the `src` layout for the project structure.

#### Out of Scope
* The `PiNet API` itself (this is treated as a pre-existing external system).
* The Open Webui application (this is treated as the client consumer).
* The training or configuration of the LLM.

### 1.4 Acronyms & Definitions
* **MCP:** Modular Component Platform. A framework for building and exposing Python tools to other applications.
* **PiNet API:** The target REST API running on a Raspberry Pi for network control.
* **LLM:** Large Language Model.
* **WoL:** Wake-on-LAN.
* **SSE:** Server-Sent Events. An HTTP-based transport mechanism.
* **SRS:** Software Requirements Specification.
* **API:** Application Programming Interface.

---

## 2. System Overview

This project is an **adapter** (or "bridge"). Its architecture consists of three main parts:

1.  **Client (Open Webui):** An LLM host that supports MCP for tool/function calling.
2.  **MCP PiNet Adapter (This Project):** A Python server that listens for MCP requests via SSE. It translates these requests into calls to the `PiNet API`.
3.  **External Service (PiNet API):** The existing API on the Raspberry Pi that executes the actual network commands.

The data flow is as follows:
`LLM (in Open Webui)` &rarr; `MCP PiNet Adapter` &rarr; `PiNet API (on Raspberry Pi)`

### Technology Stack
* **Language:** Python 3.7+
* **Framework:** `FastMCP` (using the `python-mcp-sdk`)
* **Server Transport:** Server-Sent Events (SSE) over HTTP
* **Client Library:** `pinet_client.py` (for communicating with `PiNet API`)
* **Deployment:** Docker

---

## 3. Functional Requirements (FR)

The server shall expose its functionalities as "tools" using the `@mcp.tool` decorator.

### FR-3.1: Tool: Ping Host
* **Description:** A tool to check if a given IP address or hostname is reachable on the network.
* **Decorator:** `@mcp.tool`
* **Input:** `ip_address` (string) - The IP or hostname to ping.
* **Process:**
    1.  The tool shall receive the `ip_address` argument.
    2.  It shall use the `pinet_client.PiNetClient` to call the `is_host_online()` method.
    3.  This client will handle the authenticated `GET` request to the `PiNet API`'s `/ping/{ip_address}` endpoint.
* **Output (to LLM):** A JSON object (or dictionary) representing the result from the `PiNet API`.
    * **Success (Online):** `{"ip_address": "8.8.8.8", "status": "online"}`
    * **Success (Offline):** `{"ip_address": "192.168.1.100", "status": "offline"}`
    * **Error:** `{"status": "error", "message": "Invalid IP address format."}`

### FR-3.2: Tool: Wake Device (Wake-on-LAN)
* **Description:** A tool to send a Wake-on-LAN (WoL) magic packet to a device with a specified MAC address.
* **Decorator:** `@mcp.tool`
* **Input:** `mac_address` (string) - The target device's MAC address (e.g., `AA:BB:CC:DD:EE:FF`).
* **Process:**
    1.  The tool shall receive the `mac_address` argument.
    2.  It shall use the `pinet_client.PiNetClient` to call the `wake_host()` method.
    3.  This client will handle the authenticated `POST` request to the `PiNet API`'s `/wol` endpoint.
* **Output (to LLM):** A JSON object (or dictionary) representing the result from the `PiNet API`.
    * **Success:** `{"status": "success", "message": "Wake-on-LAN packet sent to AA:BB:CC:DD:EE:FF"}`
    * **Error:** `{"status": "error", "message": "Invalid MAC address format."}`

---

## 4. Non-Functional Requirements (NFR)

### NFR-4.1: Security & Authentication
* **MCP Server Authentication:** The MCP server itself **shall not** implement any authentication. It is considered a trusted internal service, and access control will be managed at the network level (e.g., private Docker network, firewall rules).
* **`PiNet API` Credentials:** The server must securely handle the credentials for the downstream `PiNet API`.

### NFR-4.2: Configuration
* The server must be configurable via environment variables, which can be loaded from a `.env` file during development.
* The following variables are **required** for the server to function:
    * `PINET_API_URL`: The full base URL of the `PiNet API` (e.g., `http://192.168.1.50:5000`).
    * `PINET_API_KEY`: The secret API key used to authenticate with the `PiNet API`.

### NFR-4.3: Deployment & Transport
* The project must include a `Dockerfile` that packages the application and its Python dependencies into a container image.
* The server shall be initiated using `mcp.run()`.
* The server must be configured to use the **Server-Sent Events (SSE)** transport mechanism to allow for remote HTTP-based connections from Open Webui.

### NFR-4.4: Project Structure
* The project must follow the standard Python **`src` layout** to separate packageable source code from other files (like tests, docs, and scripts).
* The high-level structure shall be:
    ```
    mcp-pinet-adapter/
    ├── src/
    │   └── mcp_pinet_adapter/  <-- Python package
    │       ├── __init__.py
    │       └── server.py       <-- Main application, FastMCP, and tools
    ├── tests/
    │   └── ...
    ├── .dockerignore
    ├── .env.example            <-- Template for environment variables
    ├── .gitignore
    ├── Dockerfile
    ├── pyproject.toml          <-- Or requirements.txt
    └── README.md
    ```

### NFR-4.5: Reliability & Error Handling
* The server must be resilient to failures from the downstream `PiNet API`.
* If the `PiNet API` is unreachable (e.g., connection timeout), the MCP tool shall return a clear error message to the LLM (e.g., `{"status": "error", "message": "PiNet API is unreachable."}`).
* All errors from the `PiNet API` (e.g., 401 Unauthorized, 400 Bad Request) must be captured and propagated as the tool's output, so the LLM can understand what went wrong.

---

## 5. Development & Testing

* Local development and debugging shall be primarily conducted using the **MCP Inspector** utility (`mcp devaf server.py`).
* The `pinet_client.py` and its dependencies (from the `PiNet API` project) should be included as a library or dependency in this project.