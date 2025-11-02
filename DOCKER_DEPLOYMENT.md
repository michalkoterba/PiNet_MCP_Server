# Docker Deployment Guide
## PiNet MCP Server

This guide explains how to deploy the PiNet MCP Server using Docker.

---

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 1.29 or higher, optional but recommended)
- Your `.env` file configured with PiNet API credentials

---

## Quick Start with Docker Compose (Recommended)

### 1. Configure Environment Variables

Ensure your `.env` file exists with the following values:

```bash
# PiNet API Configuration (Required)
PINET_API_URL=http://YOUR_PINET_IP:5000
PINET_API_KEY=your_api_key_here

# MCP Server Configuration (Optional)
MCP_SERVER_PORT=8000
```

### 2. Start the Server

```bash
docker-compose up -d
```

### 3. Check Status

```bash
docker-compose ps
docker-compose logs -f pinet-mcp-server
```

### 4. Stop the Server

```bash
docker-compose down
```

---

## Manual Docker Build and Run

### Build the Image

```bash
docker build -t pinet-mcp-server:latest .
```

### Run the Container

```bash
docker run -d \
  --name pinet-mcp-server \
  -p 8000:8000 \
  -e PINET_API_URL=http://YOUR_PINET_IP:5000 \
  -e PINET_API_KEY=your_api_key_here \
  -e MCP_SERVER_PORT=8000 \
  pinet-mcp-server:latest
```

### Or use the .env file:

```bash
docker run -d \
  --name pinet-mcp-server \
  -p 8000:8000 \
  --env-file .env \
  pinet-mcp-server:latest
```

---

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PINET_API_URL` | Yes | - | Base URL of your PiNet API server |
| `PINET_API_KEY` | Yes | - | API key for authentication |
| `MCP_SERVER_PORT` | No | `8000` | Port the MCP server listens on |
| `MCP_SERVER_HOST` | No | `0.0.0.0` | Host interface to bind to |

### Port Mapping

The default port is `8000`. To use a different host port:

```bash
# Map host port 9000 to container port 8000
docker run -p 9000:8000 ...
```

Or in `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"
```

---

## Accessing from Open WebUI

### If Open WebUI is on the Same Docker Host

Use the container name or localhost:

```
http://pinet-mcp-server:8000/mcp
```

or

```
http://localhost:8000/mcp
```

### If Open WebUI is on a Different Machine

Use the host machine's IP address:

```
http://YOUR_SERVER_IP:8000/mcp
```

### If Using Docker Compose with Custom Network

Add Open WebUI to the same network in your docker-compose.yml:

```yaml
services:
  pinet-mcp-server:
    # ... existing config ...
    networks:
      - pinet-network

  open-webui:
    # ... Open WebUI config ...
    networks:
      - pinet-network

networks:
  pinet-network:
    driver: bridge
```

Then use: `http://pinet-mcp-server:8000/mcp`

---

## Monitoring and Logs

### View Logs

```bash
# With docker-compose
docker-compose logs -f pinet-mcp-server

# With docker
docker logs -f pinet-mcp-server
```

### Check Health

```bash
# Container status
docker ps | grep pinet-mcp-server

# Health check
docker inspect --format='{{.State.Health.Status}}' pinet-mcp-server
```

### Access Container Shell

```bash
# With docker-compose
docker-compose exec pinet-mcp-server /bin/bash

# With docker
docker exec -it pinet-mcp-server /bin/bash
```

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs pinet-mcp-server
```

**Common issues:**
- Missing environment variables → Check `.env` file
- Port already in use → Change `MCP_SERVER_PORT` or stop conflicting service
- PiNet API unreachable → Verify `PINET_API_URL` and network connectivity

### Cannot Connect from Open WebUI

**1. Check if container is running:**
```bash
docker ps | grep pinet-mcp-server
```

**2. Verify port mapping:**
```bash
docker port pinet-mcp-server
```

**3. Test connectivity:**
```bash
# From host machine
curl http://localhost:8000/

# From Open WebUI container (if using Docker)
docker exec open-webui curl http://pinet-mcp-server:8000/
```

**4. Check firewall:**
Ensure port 8000 is open on the host machine.

### Environment Variables Not Loading

**Verify they're being passed:**
```bash
docker exec pinet-mcp-server env | grep PINET
```

**If using .env file, ensure:**
- File is named `.env` exactly
- File is in the same directory as docker-compose.yml
- No quotes around values in .env file

---

## Updating the Server

### With Docker Compose

```bash
# Pull latest code changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### With Docker

```bash
# Stop and remove old container
docker stop pinet-mcp-server
docker rm pinet-mcp-server

# Rebuild image
docker build -t pinet-mcp-server:latest .

# Start new container
docker run -d --name pinet-mcp-server -p 8000:8000 --env-file .env pinet-mcp-server:latest
```

---

## Production Considerations

### Security

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use Docker secrets** for production:
   ```yaml
   secrets:
     pinet_api_key:
       file: ./secrets/api_key.txt
   ```

3. **Run as non-root user** (add to Dockerfile):
   ```dockerfile
   RUN useradd -m -u 1000 mcpuser
   USER mcpuser
   ```

### Performance

1. **Resource limits** (already configured in docker-compose.yml):
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

2. **Restart policy**:
   ```yaml
   restart: unless-stopped
   ```

### Monitoring

1. **Health checks** (already configured in Dockerfile)

2. **Log rotation** (already configured in docker-compose.yml):
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

---

## Multi-Architecture Builds

To build for different architectures (e.g., ARM for Raspberry Pi):

```bash
# Enable buildx
docker buildx create --use

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t pinet-mcp-server:latest .
```

---

## Advanced: Integration with Existing Open WebUI Docker Setup

If Open WebUI is already running in Docker, add PiNet MCP Server to the same setup:

**Option 1: Add to existing docker-compose.yml**

```yaml
services:
  open-webui:
    # ... existing Open WebUI config ...

  pinet-mcp-server:
    build: ./PiNet_MCP_Server
    environment:
      - PINET_API_URL=${PINET_API_URL}
      - PINET_API_KEY=${PINET_API_KEY}
    networks:
      - webui_network

networks:
  webui_network:
    external: true  # Use existing network
```

**Option 2: Use Docker network**

```bash
# Create shared network
docker network create webui_network

# Run PiNet MCP Server on that network
docker run -d \
  --name pinet-mcp-server \
  --network webui_network \
  --env-file .env \
  pinet-mcp-server:latest

# Open WebUI can now access at: http://pinet-mcp-server:8000/mcp
```

---

## Testing the Deployment

### 1. Test server is running

```bash
curl http://localhost:8000/
# Expected: 404 (this is correct - server only responds to /mcp endpoint)
```

### 2. Test MCP endpoint (requires MCP client)

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### 3. Integration test with Open WebUI

Follow the steps in `OPEN_WEBUI_SETUP.md` to connect Open WebUI to:
```
http://pinet-mcp-server:8000/mcp
```
or
```
http://localhost:8000/mcp
```

---

## Backup and Restore

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup

# Backup docker-compose.yml (if customized)
cp docker-compose.yml docker-compose.yml.backup
```

### Restore

```bash
# Stop current container
docker-compose down

# Restore configuration
cp .env.backup .env

# Restart with restored config
docker-compose up -d
```

---

## Cleaning Up

### Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi pinet-mcp-server:latest

# Remove volumes (if any)
docker volume prune
```

### Remove Just the Container

```bash
docker-compose down
# or
docker stop pinet-mcp-server && docker rm pinet-mcp-server
```

---

## Getting Help

If you encounter issues:

1. Check container logs: `docker-compose logs pinet-mcp-server`
2. Verify environment variables: `docker exec pinet-mcp-server env`
3. Test PiNet API connectivity: `docker exec pinet-mcp-server curl http://YOUR_PINET_IP:5000/`
4. Check Open WebUI logs for MCP connection errors

---

## Next Steps

1. ✅ Build and start the container
2. ✅ Verify it's running with `docker ps`
3. ✅ Connect from Open WebUI
4. ✅ Test with ping and wake-on-LAN commands