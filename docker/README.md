# lmelp - Docker Deployment

This directory contains Docker configuration files for deploying lmelp (Le Masque et la Plume) on multiple environments.

## 📦 Quick Start

### PC Local Deployment

1. **Copy environment template:**
   ```bash
   cd docker/
   cp .env.template .env
   ```

2. **Edit `.env` and fill in your API keys:**
   - At least one LLM API key is required (Azure, OpenAI, or Gemini)
   - Google services are optional

3. **Start containers:**
   ```bash
   ./scripts/start.sh
   ```

4. **Access the application:**
   - Open http://localhost:8501 in your browser

### NAS Synology Deployment

Use `docker-compose.nas.yml` with Portainer:
- See [NAS Deployment Guide](../docs/deployment/nas-deployment.md) (to be created)

## 📂 Files Overview

| File | Description |
|------|-------------|
| `Dockerfile` | Multi-stage build for lmelp application |
| `docker-compose.yml` | PC local deployment (includes MongoDB) |
| `docker-compose.nas.yml` | NAS deployment (uses existing MongoDB) |
| `.env.template` | Environment variables template |
| `entrypoint.sh` | Container entrypoint supporting multiple modes |
| `scripts/start.sh` | Start containers |
| `scripts/stop.sh` | Stop containers |
| `scripts/update.sh` | Update to latest version |
| `scripts/logs.sh` | View container logs |
| `scripts/backup-db.sh` | Backup MongoDB database |

## 🔧 Environment Variables

### Required

```bash
# Database (auto-configured in docker-compose)
DB_HOST=mongodb              # or 'mongo' for NAS
DB_NAME=masque_et_la_plume

# At least ONE of these API keys:
AZURE_API_KEY=...
AZURE_ENDPOINT=...
# OR
OPENAI_API_KEY=...
# OR
GEMINI_API_KEY=...
```

### Optional

```bash
# Google Services
GOOGLE_PROJECT_ID=...
GOOGLE_CUSTOM_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...
```

## 🚀 Usage

### Web Interface (default)

```bash
# Start the application
./scripts/start.sh

# View logs
./scripts/logs.sh

# Stop the application
./scripts/stop.sh
```

### Batch Processing

Run scripts in container for batch operations:

**Update RSS episodes:**
```bash
docker run --rm --network lmelp-network \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-update \
  ghcr.io/castorfou/lmelp:latest
```

**Transcribe all episodes:**
```bash
docker run --rm --network lmelp-network \
  -v lmelp-audios:/app/audios \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-transcribe \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  ghcr.io/castorfou/lmelp:latest
```

**Transcribe specific episode:**
```bash
docker run --rm --network lmelp-network \
  -v lmelp-audios:/app/audios \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-transcribe \
  -e EPISODE_ID=20240120 \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  ghcr.io/castorfou/lmelp:latest
```

**Extract authors:**
```bash
docker run --rm --network lmelp-network \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-authors \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  ghcr.io/castorfou/lmelp:latest
```

## 📊 Container Modes

The container supports multiple modes via `LMELP_MODE` environment variable:

| Mode | Description | Environment Variables |
|------|-------------|----------------------|
| `web` | Streamlit web interface (default) | - |
| `batch-update` | Update episodes from RSS | - |
| `batch-transcribe` | Transcribe episodes | `EPISODE_ID` (optional) |
| `batch-authors` | Extract authors from episodes | `EPISODE_ID` (optional) |

## 💾 Volumes

The following volumes are created for data persistence:

| Volume | Path | Contents | Size Estimate |
|--------|------|----------|---------------|
| `lmelp-mongodb-data` | `/data/db` | MongoDB database | 1-5 GB |
| `lmelp-audios` | `/app/audios` | Downloaded audio files | 50-100 GB |
| `lmelp-db-backup` | `/app/db` | Database backups | 1-5 GB |
| `lmelp-logs` | `/app/logs` | Application logs | < 100 MB |

## 🔄 Maintenance

### Update to latest version

```bash
./scripts/update.sh
```

This will:
1. Pull the latest image from ghcr.io
2. Restart containers with the new image
3. Preserve all data in volumes

### Backup database

```bash
./scripts/backup-db.sh
```

### View logs

```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh app
./scripts/logs.sh mongodb
```

### Inspect containers

```bash
# Check status
docker compose ps

# Check resource usage
docker stats lmelp-app lmelp-mongodb

# Access container shell
docker exec -it lmelp-app bash
docker exec -it lmelp-mongodb mongosh
```

## 🐛 Troubleshooting

### Application won't start

```bash
# Check logs
./scripts/logs.sh app

# Common issues:
# - Missing .env file
# - Invalid API keys
# - MongoDB not ready (wait 30s for healthcheck)
```

### MongoDB connection failed

```bash
# Check MongoDB is running
docker ps | grep mongodb

# Check MongoDB logs
./scripts/logs.sh mongodb

# Test connection
docker exec lmelp-app python -c "
from nbs.mongo import get_mongodb_client
client = get_mongodb_client()
print(client.server_info())
"
```

### Out of disk space

```bash
# Check volume sizes
docker system df -v

# Clean up old data
docker volume prune
docker image prune -a
```

### Slow performance / High RAM usage

- ML models (Whisper, Transformers) are memory-intensive
- Normal RAM usage: 2-4 GB
- During transcription: 4-8 GB
- Adjust memory limits in docker-compose.yml if needed

## 🏗️ Building from source

To build the Docker image locally:

```bash
# From project root
docker build -f docker/Dockerfile -t lmelp:local .

# Run locally built image
docker run -p 8501:8501 \
  -e DB_HOST=host.docker.internal \
  -e GEMINI_API_KEY=your_key \
  lmelp:local
```

## 📚 Documentation

For detailed documentation, see:
- [Docker Setup Guide](../docs/deployment/docker-setup.md) (to be created)
- [Local Deployment Guide](../docs/deployment/local-deployment.md) (to be created)
- [NAS Deployment Guide](../docs/deployment/nas-deployment.md) (to be created)
- [Troubleshooting Guide](../docs/deployment/troubleshooting.md) (to be created)

## ⚙️ Technical Specifications

**Image:**
- Base: Python 3.11-slim
- Size: ~2.5-3 GB (includes ML models)
- Build: Multi-stage with uv dependency manager

**Resource Limits:**
- CPU: 2 cores (limit), 1 core (reservation)
- Memory: 4 GB (limit), 2 GB (reservation)

**Healthchecks:**
- Interval: 30s
- Timeout: 10s
- Retries: 3
- Start period: 40s (ML model loading time)

## 🔗 References

- [GitHub Container Registry](https://github.com/castorfou/lmelp/pkgs/container/lmelp)
- [Issue #64 - Dockerization](https://github.com/castorfou/lmelp/issues/64)
- [CLAUDE.md - Project Documentation](../CLAUDE.md)
