# Docker Setup Guide

This guide explains how to run the AI Knowledge Assistant using Docker Compose.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ (included with Docker Desktop)
- `.env` file with required API keys (see below)

## Quick Start

1. **Ensure your `.env` file is configured** with required API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key

# Collection settings (optional, defaults provided)
COLLECTION_NAME=articles
TOP_K_RESULTS=5
MIN_RELEVANCE_SCORE=0.75
HIGH_RELEVANCE_THRESHOLD=0.85
```

2. **Start all services:**

```bash
docker-compose up -d
```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Qdrant Dashboard: http://localhost:6333/dashboard

## Docker Compose Services

### 1. Qdrant (Vector Database)
- **Container**: `ai-knowledge-qdrant`
- **Ports**: 6333 (HTTP API), 6334 (gRPC)
- **Volume**: `qdrant_data` (persistent storage)
- **Health Check**: Every 10s

### 2. Backend (FastAPI)
- **Container**: `ai-knowledge-backend`
- **Port**: 8000
- **Dependencies**: Waits for Qdrant to be healthy
- **Environment**: Loaded from `.env` file
- **Health Check**: Every 30s

### 3. Frontend (React + Nginx)
- **Container**: `ai-knowledge-frontend`
- **Port**: 3000 (maps to internal port 80)
- **Dependencies**: Waits for Backend to be healthy
- **Health Check**: Every 30s

## Common Commands

### Start Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f qdrant
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (deletes Qdrant data)
docker-compose down -v
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Rebuild Containers

```bash
# Rebuild and restart all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

## Data Ingestion

To ingest articles into Qdrant after starting the services:

```bash
# Enter the backend container
docker-compose exec backend bash

# Run ingestion script
python -m app.services.ingestion data/articles --clear

# Exit container
exit
```

Alternatively, run ingestion directly:

```bash
docker-compose exec backend python -m app.services.ingestion data/articles --clear
```

## Troubleshooting

### Services Won't Start

1. **Check if ports are already in use:**
   ```bash
   lsof -i :3000  # Frontend
   lsof -i :8000  # Backend
   lsof -i :6333  # Qdrant
   ```

2. **View service status:**
   ```bash
   docker-compose ps
   ```

3. **Check service health:**
   ```bash
   docker-compose ps
   # Look for "(healthy)" status
   ```

### Backend Can't Connect to Qdrant

- Ensure Qdrant is healthy: `docker-compose ps qdrant`
- Check backend logs: `docker-compose logs backend`
- Verify network: `docker network ls | grep ai-knowledge`

### Frontend Can't Reach Backend

1. **Check if backend is healthy:**
   ```bash
   docker-compose ps backend
   curl http://localhost:8000/health
   ```

2. **Rebuild frontend with correct API URL:**
   ```bash
   docker-compose up -d --build frontend
   ```

### Permission Issues

If you encounter permission errors with volumes:

```bash
# On Linux, ensure proper permissions
sudo chown -R $USER:$USER .
```

### Out of Memory

If services crash due to memory:

```bash
# Increase Docker memory limit in Docker Desktop
# Settings > Resources > Memory > 4GB+
```

## Advanced Configuration

### Custom Ports

Edit `docker-compose.yml` to change port mappings:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change host port to 8080

  backend:
    ports:
      - "5000:8000"  # Change host port to 5000
```

### Production Deployment

For production, consider:

1. **Use environment-specific `.env` files:**
   ```bash
   docker-compose --env-file .env.production up -d
   ```

2. **Enable HTTPS with reverse proxy** (Nginx/Caddy/Traefik)

3. **Set up proper secrets management** (Docker secrets, AWS Secrets Manager)

4. **Configure resource limits:**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

## Architecture Diagram

```
┌─────────────────┐
│   Frontend      │  Port 3000
│  (React+Nginx)  │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│    Backend      │  Port 8000
│    (FastAPI)    │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│    Qdrant       │  Port 6333
│ (Vector Store)  │
└─────────────────┘
```

## Volumes and Data Persistence

- **qdrant_data**: Stores Qdrant vector database
  - Location: Managed by Docker
  - View: `docker volume inspect ai-knowledge-assistant_qdrant_data`
  - Backup: `docker run --rm -v ai-knowledge-assistant_qdrant_data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .`

## Network Configuration

All services communicate through the `ai-knowledge-network` bridge network:

```bash
# Inspect network
docker network inspect ai-knowledge-assistant_ai-knowledge-network

# Test connectivity between services
docker-compose exec backend ping qdrant
docker-compose exec frontend ping backend
```

## Monitoring and Health Checks

View service health status:

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' ai-knowledge-backend | jq
```

## Cleanup

Remove all containers, networks, and volumes:

```bash
# Stop and remove containers + networks
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker-compose down -v --rmi all --remove-orphans
```

## Development vs Production

### Development Mode

```bash
# Use hot-reload by mounting source code
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production Mode

```bash
# Build optimized images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## FAQ

**Q: How do I update the application?**
```bash
git pull
docker-compose up -d --build
```

**Q: How do I access the database?**
```bash
# Qdrant web UI
open http://localhost:6333/dashboard
```

**Q: How do I run tests?**
```bash
docker-compose exec backend pytest
```

**Q: Can I use external Qdrant instance?**
Yes, modify `.env`:
```bash
QDRANT_URL=https://your-qdrant-instance.com
QDRANT_API_KEY=your-api-key
```

Then comment out the `qdrant` service in `docker-compose.yml`.

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review health status: `docker-compose ps`
- Consult main README.md for application-specific details
