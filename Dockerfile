# PiNet MCP Server Dockerfile
# This creates a containerized version of the PiNet MCP Server

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata and source files
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
# Using -e installs in editable mode which is good for development
# For production, you might want to remove -e
RUN pip install --no-cache-dir -e .

# Expose port for MCP Streamable HTTP transport
# Default port is 8000, but can be overridden via MCP_SERVER_PORT env var
EXPOSE 8000

# Environment variables (these should be overridden at runtime)
# Do not set actual values here - use docker run -e or docker-compose
ENV PINET_API_URL=""
ENV PINET_API_KEY=""
ENV MCP_SERVER_PORT=8000
ENV MCP_SERVER_HOST=0.0.0.0

# Health check (optional but recommended)
# Checks if the server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${MCP_SERVER_PORT}/', timeout=5)" || exit 1

# Run the MCP server as a module
CMD ["python", "-m", "mcp_pinet_server"]