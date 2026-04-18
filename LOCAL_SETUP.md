# Local Development Setup for Cerbos

This guide explains how to build and run Cerbos locally using Docker Desktop.

## Prerequisites

- Docker Desktop installed and running
- Git (to clone the repository)

## Quick Start

### 1. Build the Docker Image

```bash
cd conqrse-cerbos
docker build -t cerbos:local .
```

Expected output:
```
[+] Building 15.3s (10/10) FINISHED
 => => writing image sha256:abc123... 0.0s
 => => naming to docker.io/library/cerbos:local 0.0s
```

### 2. Run the Container

```bash
docker run -d \
  --name cerbos-dev \
  -p 3592:3592 \
  -p 3593:3593 \
  -p 3591:3591 \
  -v $(pwd)/k8s/base/policies:/policies \
  cerbos:local
```

On Windows (PowerShell):
```powershell
docker run -d `
  --name cerbos-dev `
  -p 3592:3592 `
  -p 3593:3593 `
  -p 3591:3591 `
  -v "$PWD/k8s/base/policies:/policies" `
  cerbos:local
```

### 3. Verify It's Running

```bash
# Check container status
docker ps | grep cerbos-dev

# Health check
curl http://localhost:3592/health

# Expected response:
# {"status":"OK"}
```

### 4. Access Cerbos

- **Admin UI**: http://localhost:3592
- **gRPC Endpoint**: localhost:3593
- **Metrics**: http://localhost:3591/metrics

## Common Commands

### View Logs

```bash
# Real-time logs
docker logs -f cerbos-dev

# Last 100 lines
docker logs --tail 100 cerbos-dev
```

### Stop Container

```bash
docker stop cerbos-dev
```

### Start Stopped Container

```bash
docker start cerbos-dev
```

### Remove Container

```bash
docker rm cerbos-dev
```

### Remove Image

```bash
docker rmi cerbos:local
```

## Hot Reload (Update Policies)

The container volume-mounts the policies directory, so changes are reflected automatically:

```bash
# Edit a policy file
vim k8s/base/policies/resource_product.yaml

# Save the file - Cerbos picks up changes automatically (watchForChanges: true)
curl http://localhost:3592/policies | jq .
```

## Testing Authorization

### Test Allow Scenario (Retailer Member listing QR campaigns)

```bash
curl -X POST http://localhost:3592/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "principal": {
      "id": "user-123",
      "userLevel": "retailer",
      "userType": "member",
      "name": "john.doe",
      "products": ["qr"],
      "agencyId": "agency-456",
      "retailerId": "retail-789"
    },
    "resource": {
      "name": "qr:campaigns",
      "product": "qr",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    },
    "action": "resource:list"
  }'
```

Expected: `{"cerbosVersion":"0.51.0","status":"EFFECT_ALLOW"}`

### Test Deny Scenario (Collaborator creating resource)

```bash
curl -X POST http://localhost:3592/api/check \
  -H "Content-Type: application/json" \
  -d '{
    "principal": {
      "id": "user-456",
      "userLevel": "retailer",
      "userType": "collaborator",
      "name": "guest@retailer.com",
      "products": ["qr"],
      "agencyId": "agency-456",
      "retailerId": "retail-789"
    },
    "resource": {
      "name": "qr:campaigns",
      "product": "qr",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    },
    "action": "resource:create"
  }'
```

Expected: `{"cerbosVersion":"0.51.0","status":"EFFECT_DENY"}`

## Troubleshooting

### Container won't start

```bash
# Check for detailed error logs
docker logs cerbos-dev

# Common issues:
# - Port already in use: Change -p 3592:XXXX where XXXX is a free port
# - File permissions: Ensure k8s/base/policies directory exists and is readable
```

### Health check fails

```bash
# Wait a few seconds for startup
sleep 5
curl http://localhost:3592/health

# If still failing, check logs
docker logs cerbos-dev
```

### Volume mount issues

```bash
# Verify volume mount
docker inspect cerbos-dev | grep -A 10 Mounts

# Manually mount with full path
docker run -d --name cerbos-dev \
  -p 3592:3592 \
  -p 3593:3593 \
  -p 3591:3591 \
  -v /full/path/to/k8s/base/policies:/policies \
  cerbos:local
```

### gRPC not responding

Install grpcurl for testing:
```bash
# macOS
brew install grpcurl

# Linux
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Test
grpcurl -plaintext localhost:3593 list
```

## Development Workflow

1. **Make policy changes** → Edit files in `k8s/base/policies/`
2. **Check validity** → Policies auto-reload (no container restart needed)
3. **Test changes** → Use curl commands above or Cerbos UI at http://localhost:3592
4. **View audit logs** → `docker logs -f cerbos-dev`
5. **Commit changes** → `git add k8s/base/policies && git commit`

## Connecting from Other Services

If you're running frontend or backend services locally:

### From Docker containers on same network

Create a shared network:
```bash
docker network create conqrse-dev

# Rebuild container on network
docker run -d \
  --name cerbos-dev \
  --network conqrse-dev \
  -p 3592:3592 \
  -p 3593:3593 \
  -v $(pwd)/k8s/base/policies:/policies \
  cerbos:local

# Run other services on same network
docker run --network conqrse-dev myapp:latest
```

### From host machine

- gRPC: `localhost:3593`
- HTTP: `localhost:3592`

### From WSL (Windows Subsystem for Linux)

```bash
# Get Docker Desktop IP from Windows
# Usually: 172.17.0.1 (default Docker network gateway)

# Use in WSL
curl http://172.17.0.1:3592/health
```

## Production Deployment

For Kubernetes deployment, see [README.md](./README.md#kubernetes-deployment)
