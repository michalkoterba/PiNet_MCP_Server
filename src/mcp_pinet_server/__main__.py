"""
Entry point for running PiNet MCP Server as a module.

This allows the server to be run with:
    python -m mcp_pinet_server
"""

import os
from .server import mcp

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv('MCP_SERVER_PORT', '8000'))
    host = os.getenv('MCP_SERVER_HOST', '0.0.0.0')

    print("\n" + "="*60)
    print(f"Starting PiNet MCP Server on {host}:{port}...")
    print("="*60 + "\n")

    print(f"[OK] Server will be accessible at: http://{host}:{port}")
    if host == "0.0.0.0":
        print(f"[OK] From other machines use: http://YOUR_PC_IP:{port}")
    print()

    # Get the FastMCP streamable-http app
    # This gives us full control over host binding with uvicorn
    app = mcp.streamable_http_app

    print(f"[OK] Starting uvicorn server...")
    print()
    uvicorn.run(app, host=host, port=port)