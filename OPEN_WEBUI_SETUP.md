# PiNet MCP Server - Open WebUI Integration Guide

## Overview

This guide shows how to connect your PiNet MCP Server to Open WebUI using the MCP (Model Context Protocol) Streamable HTTP transport.

## Step 1: Start Your PiNet MCP Server

### Start the Server

```bash
python -m mcp_pinet_server
```

### Expected Output

```
[OK] Configuration loaded: Config(pinet_api_url='http://YOUR_PINET_IP:5000', pinet_api_key='YOUR_...KEY')
[OK] PiNet API client initialized for http://YOUR_PINET_IP:5000

============================================================
Starting PiNet MCP Server on 0.0.0.0:5001...
============================================================

[OK] Server will be accessible at: http://0.0.0.0:5001
[OK] From other machines use: http://YOUR_PC_IP:5001

[OK] Starting uvicorn server...

INFO: Started server process [XXXXX]
INFO: Waiting for application startup.
INFO: StreamableHTTP session manager started
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:5001 (Press CTRL+C to quit)
```

**Note**: The server binds to `0.0.0.0`, which means it's accessible from:
- The same machine: `http://localhost:5001/mcp`
- Other machines on the network: `http://YOUR_MCP_SERVER_IP:5001/mcp`

---

## Step 2: Add Connection in Open WebUI

### 1. Open Open WebUI Admin Panel

- Navigate to your Open WebUI (usually `http://localhost:8080` or your Open WebUI URL)
- Click on your profile/avatar (top right)
- Select **"Admin Panel"**
- Go to **"Settings"**
- Go to **"External Tools"** section

### 2. Add New MCP Connection

Click **"+ Add Connection"** and fill in:

| Field | Value |
|-------|-------|
| **Type** | `MCP Streamable HTTP` |
| **Name** | `PiNet MCP Server` |
| **URL** | See below |
| **Auth** | `None` |
| **Description** | `Network diagnostics tools (ping & Wake-on-LAN)` |

### 3. Choose the Correct URL

**Important**: The URL must include the `/mcp` endpoint path!

- **If Open WebUI is on the same machine as the MCP server:**
  ```
  http://localhost:5001/mcp
  ```

- **If Open WebUI is on a different machine (e.g., Docker container):**
  ```
  http://YOUR_PC_IP:5001/mcp
  ```

  Example:
  ```
  http://YOUR_PC_IP:5001/mcp
  ```

### 4. Test the Connection

Click **"Test Connection"** or **"Check"**

- ✅ **Success**: You'll see a connection confirmed message
- ❌ **Failed**: Check troubleshooting section below

### 5. Save and Enable

- Click **"Save"**
- Make sure the connection is **enabled/active**
- You should now see 2 tools available: `ping_host` and `wake_device`

---

## Step 3: Test Your Tools in Open Webui

### Using Chat Interface

Once connected, you can test by chatting with the LLM.
Enable PiNet MCP in chat window: Intergations > Tools > PiNet MCP.
Enter a prompt:

**Example 1: Ping a host**
```
User: Can you check if 8.8.8.8 is online?

LLM: I'll check that for you.
[Uses ping_host tool]
Result: The host 8.8.8.8 is online.
```

**Example 2: Wake a device**
```
User: Please wake up the device with MAC address AA:BB:CC:DD:EE:FF

LLM: I'll send a Wake-on-LAN packet.
[Uses wake_device tool]
Result: Wake-on-LAN packet sent successfully to AA:BB:CC:DD:EE:FF
```

**Example 3: Combined tasks**
```
User: Check if 192.168.1.100 is online, and if not, wake it up with MAC AA:BB:CC:DD:EE:FF

LLM: Let me check the host status first.
[Uses ping_host tool]
The host is offline. I'll send a Wake-on-LAN packet now.
[Uses wake_device tool]
Done! I've sent the WoL packet.
```

---

## Troubleshooting

### Server Not Starting

**Issue**: Server fails to start
**Solution**:
- Check that `.env` file exists and has correct values
- Verify Python virtual environment is activated
- Check port is not already in use

### Open Webui Can't Connect

**Issue**: "Connection failed" or "Server unreachable"
**Solution**:
1. Make sure the MCP server is running (check terminal)
2. Verify the connection type (stdio vs SSE)
3. Check firewall settings
4. For stdio: Make sure Open Webui can execute Python commands
5. For SSE: Verify the port number matches

### Tools Not Appearing

**Issue**: MCP server connected but tools don't show up
**Solution**:
1. Restart Open Webui
2. Check Open Webui logs for errors
3. Verify the server is sending tool definitions correctly
4. Try reconnecting the MCP server

### Tools Return Errors

**Issue**: Tools execute but return errors
**Solution**:
1. **"PiNet API is unreachable"**:
   - Make sure your PiNet API server (Raspberry Pi) is online
   - Check the `PINET_API_URL` in your `.env` file
   - Test with: `curl http://YOUR_PINET_IP:5000/`

2. **"Authentication failed"**:
   - Verify `PINET_API_KEY` in `.env` matches your PiNet API
   - Check API key hasn't expired

3. **"Invalid IP/MAC format"**:
   - LLM passed incorrect format
   - Tools are working correctly (this is expected error handling)

---

## Finding Your MCP Server Port

If you need to know what port your server is using:

```bash
# On Windows
netstat -ano | findstr python

# Look for the LISTENING line with your Python process
```

Common MCP ports:
- **stdio**: No port (uses standard input/output)
- **SSE**: Usually `5173`, `8000`, or auto-assigned

---

## Alternative: Test Tools Manually First

Before integrating with Open Webui, verify tools work:

```bash
# Run the demo script
python demo_tools.py

# This will test both tools and show you the responses
```

---

## Next Steps

1. ✅ Start your MCP server
2. ✅ Add it to Open Webui
3. ✅ Test with simple queries
4. 🎉 Use it in your workflows!

---

## Recommended Test Sequence

1. **Start simple**: Ask to ping 8.8.8.8
2. **Test error handling**: Ask to ping an invalid IP
3. **Test WoL**: Ask to wake a device
4. **Test combined**: Complex multi-step tasks

---

## Getting Help

If you encounter issues:
1. Check the terminal where the MCP server is running for error messages
2. Check Open Webui logs
3. Verify your `.env` configuration
4. Test the PiNet API directly: `curl http://YOUR_PINET_IP:5000/`