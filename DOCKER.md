# Docker Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Invisible Bank API using Docker and Docker Compose. It covers local development, production deployment, security hardening, and orchestration options.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Architecture](#docker-architecture)
- [Building the Image](#building-the-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Health Checks & Monitoring](#health-checks--monitoring)
- [Security Hardening](#security-hardening)
- [Orchestration](#orchestration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Quick Start

### Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- 2GB free disk space
- Port 8443 available

### Run in 3 Commands

```bash
# 1. Clone and navigate to project
cd invisible-bank-api

# 2. Copy environment configuration
cp .env.example .env

# 3. Start the application
docker-compose up -d
```

**Access the API:**
- Base URL: `https://localhost:8443`
- API Docs: `https://localhost:8443/docs`
- Health Check: `https://localhost:8443/health`

**Note:** Your browser will warn about the self-signed certificate. This is expected for local development.

---

## Docker Architecture

### Container Structure

```
┌─────────────────────────────────────────┐
│         invisible-bank-api              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Uvicorn ASGI Server (HTTPS)     │ │
│  │   Port: 8443                      │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │   FastAPI Application             │ │
│  │   - Authentication                │ │
│  │   - Business Logic                │ │
│  │   - Rate Limiting                 │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │   SQLAlchemy ORM                  │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │   SQLite Database                 │ │
│  │   Location: /app/runtime/bank.db  │ │
│  └───────────────────────────────────┘ │
│                                         │
│  Volumes:                               │
│  - ./runtime:/app/runtime (persistent) │
│                                         │
└─────────────────────────────────────────┘
```

### Dockerfile Overview

The Dockerfile uses a **single-stage build** optimized for simplicity:

```dockerfile
FROM python:3.12-slim           # Base image
WORKDIR /app                     # Working directory
RUN apt-get update && ...        # Install system dependencies
COPY requirements.txt .          # Copy dependencies
RUN pip install ...              # Install Python packages
COPY app/ scripts/ .env          # Copy application code
RUN mkdir -p runtime/...         # Create runtime directories
RUN openssl req ...              # Generate TLS certificates
RUN python scripts/init_db.py    # Initialize database
EXPOSE 8443                      # Expose HTTPS port
CMD ["uvicorn", ...]             # Start server
```

---

## Building the Image

### Standard Build

```bash
# Build with default tag
docker build -t invisible-bank-api:latest .

# Build with specific version tag
docker build -t invisible-bank-api:1.0.0 .

# Build without cache (fresh build)
docker build --no-cache -t invisible-bank-api:latest .
```

### Build Arguments

```bash
# Build with custom Python version
docker build --build-arg PYTHON_VERSION=3.11 -t invisible-bank-api:latest .
```

### Build Output

Successful build should show:

```
[+] Building 45.3s (15/15) FINISHED
 => [internal] load build definition
 => [internal] load .dockerignore
 => [1/10] FROM python:3.12-slim
 => [2/10] WORKDIR /app
 => [3/10] RUN apt-get update && apt-get install...
 => [4/10] COPY requirements.txt .
 => [5/10] RUN pip install --no-cache-dir -r requirements.txt
 => [6/10] COPY app/ ./app/
 => [7/10] COPY scripts/ ./scripts/
 => [8/10] COPY .env .env
 => [9/10] RUN mkdir -p runtime/log runtime/certs
 => [10/10] RUN openssl req -x509...
 => exporting to image
 => => writing image sha256:abc123...
 => => naming to invisible-bank-api:latest
```

### Verify Image

```bash
# List images
docker images | grep invisible-bank-api

# Inspect image
docker inspect invisible-bank-api:latest

# Check image size
docker images invisible-bank-api:latest --format "{{.Size}}"
```

**Expected size:** ~500-600 MB

---

## Running with Docker Compose

### Docker Compose File Structure

**docker-compose.yml** defines services, networks, and volumes:

```yaml
version: '3.8'

services:
  api:
    build: .                          # Build from Dockerfile
    ports:
      - "8443:8443"                   # Map host:container ports
    environment:
      - ENVIRONMENT=development       # Runtime environment
      - DEBUG=true
      - SECRET_KEY=${SECRET_KEY}      # From .env file
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./runtime:/app/runtime        # Persistent storage
      - ./app:/app/app                # Hot reload (dev only)
    env_file:
      - .env                          # Load environment variables
    restart: unless-stopped           # Restart policy
```

### Starting Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Start with build (rebuild image if changed)
docker-compose up -d --build

# Start with logs visible (foreground)
docker-compose up

# Scale service (run multiple instances)
docker-compose up -d --scale api=3
```

### Viewing Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100

# View logs since timestamp
docker-compose logs --since 2025-12-05T10:00:00
```

### Stopping Services

```bash
# Stop containers (keep data)
docker-compose stop

# Stop and remove containers (keep volumes)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v

# Stop with timeout
docker-compose stop -t 30
```

### Service Management

```bash
# Restart service
docker-compose restart api

# Execute command in running container
docker-compose exec api bash

# Run one-off command
docker-compose run --rm api python scripts/init_db.py

# View running processes
docker-compose ps

# View resource usage
docker-compose stats
```

---

## Environment Configuration

### Environment Variables Reference

**Required Variables:**

| Variable | Description | Example | Security |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT signing key | `5flrL5eG6PYcvj...` | ⚠️ Critical |
| `ENCRYPTION_KEY` | Fernet encryption key | `J7ic6F-TEW5Eas...` | ⚠️ Critical |
| `DATABASE_URL` | Database connection | `sqlite:///./runtime/bank.db` | ℹ️ Internal |

**Optional Variables:**

| Variable | Description | Default | Production |
|----------|-------------|---------|------------|
| `ENVIRONMENT` | Runtime environment | `development` | `production` |
| `DEBUG` | Enable debug mode | `true` | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | Specific domains |
| `ROUTING_NUMBER` | Bank routing number | `123456789` | Bank-specific |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token TTL | `15` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token TTL | `7` | `7` |
| `LOG_FILE` | Log file path | `./runtime/log/bank-api.log` | Volume path |

### Generating Secrets

**Never commit secrets to version control!**

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Environment File (.env)

**Development (.env):**
```bash
# Security Keys (CHANGE THESE!)
SECRET_KEY=5flrL5eG6PYcvj26v8yFH0A5CihFBD-EGAOQQabx-ss
ENCRYPTION_KEY=J7ic6F-TEW5EaszyOLTCrC4qLnmzsVqFQlAJ47SJATU=

# Database
DATABASE_URL=sqlite:///./runtime/bank.db

# TLS Certificates
SSL_CERT_PATH=./runtime/certs/cert.pem
SSL_KEY_PATH=./runtime/certs/key.pem

# Application
ENVIRONMENT=development
DEBUG=true
APP_NAME="Invisible Bank API"
APP_VERSION=1.0.0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Bank Configuration
ROUTING_NUMBER=123456789

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_FILE=./runtime/log/bank-api.log
LOG_LEVEL=INFO
```

**Production (.env.production):**
```bash
# Security Keys (Use secrets manager in production!)
SECRET_KEY=${AWS_SECRET_KEY}  # From AWS Secrets Manager
ENCRYPTION_KEY=${AWS_ENCRYPTION_KEY}

# Database (PostgreSQL in production)
DATABASE_URL=postgresql://user:pass@postgres:5432/bank_db

# TLS Certificates (CA-signed)
SSL_CERT_PATH=/etc/ssl/certs/api.invisiblebank.com.pem
SSL_KEY_PATH=/etc/ssl/private/api.invisiblebank.com.key

# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME="Invisible Bank API"
APP_VERSION=1.0.0

# CORS (Specific origins only!)
CORS_ORIGINS=https://app.invisiblebank.com

# Bank Configuration
ROUTING_NUMBER=123456789

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting (Stricter in production)
RATE_LIMIT_PER_MINUTE=30

# Logging
LOG_FILE=/var/log/bank-api/api.log
LOG_LEVEL=WARNING
```

---

## Production Deployment

### Production Docker Compose

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  api:
    image: invisible-bank-api:${VERSION:-latest}
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - ENVIRONMENT=production
    ports:
      - "8443:8443"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env.production
    volumes:
      - api-runtime:/app/runtime
      - api-logs:/var/log/bank-api
    restart: always
    networks:
      - bank-network
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "https://localhost:8443/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Future: Add PostgreSQL service
  # postgres:
  #   image: postgres:15-alpine
  #   environment:
  #     POSTGRES_DB: bank_db
  #     POSTGRES_USER: bank_api
  #     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   networks:
  #     - bank-network

  # Future: Add Redis service
  # redis:
  #   image: redis:7-alpine
  #   command: redis-server --requirepass ${REDIS_PASSWORD}
  #   volumes:
  #     - redis-data:/data
  #   networks:
  #     - bank-network

volumes:
  api-runtime:
    driver: local
  api-logs:
    driver: local
  # postgres-data:
  # redis-data:

networks:
  bank-network:
    driver: bridge
```

### Running Production

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Check health status
docker-compose -f docker-compose.prod.yml ps
```

### Multi-Stage Build (Optimized)

For production, use a multi-stage build to reduce image size:

**Dockerfile.multistage:**

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl curl && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY .env .env

# Create runtime directories
RUN mkdir -p runtime/log runtime/certs

# Generate self-signed certificates
RUN openssl req -x509 -newkey rsa:4096 -nodes \
    -out runtime/certs/cert.pem \
    -keyout runtime/certs/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Invisible Bank/CN=localhost"

# Initialize database
RUN python scripts/init_db.py

# Create non-root user
RUN useradd -m -u 1000 bankapi && \
    chown -R bankapi:bankapi /app
USER bankapi

EXPOSE 8443

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f -k https://localhost:8443/health || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8443", \
     "--ssl-keyfile", "./runtime/certs/key.pem", \
     "--ssl-certfile", "./runtime/certs/cert.pem", \
     "--workers", "4", \
     "--log-config", "logging.conf"]
```

**Build:**
```bash
docker build -f Dockerfile.multistage -t invisible-bank-api:1.0.0-slim .
```

**Size comparison:**
- Standard build: ~600 MB
- Multi-stage build: ~400 MB (33% reduction)

---

## Health Checks & Monitoring

### Built-in Health Check

The API includes a `/health` endpoint:

```bash
# Check health
curl -k https://localhost:8443/health

# Response
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2025-12-05T12:00:00Z"
}
```

### Docker Health Check

Docker automatically monitors container health:

```bash
# View health status
docker ps

# Output shows health status
CONTAINER ID   STATUS                    PORTS
abc123         Up 2 hours (healthy)      0.0.0.0:8443->8443/tcp
```

### Monitoring with Docker Stats

```bash
# Real-time resource usage
docker stats

# Output
CONTAINER ID   CPU %   MEM USAGE / LIMIT   MEM %   NET I/O
abc123         1.5%    200MiB / 2GiB       10%     5MB / 3MB
```

### Logging Integration

**Prometheus Metrics (Future Enhancement):**

Add to docker-compose.yml:

```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - bank-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - bank-network
```

---

## Security Hardening

### 1. Run as Non-Root User

**Add to Dockerfile:**
```dockerfile
RUN useradd -m -u 1000 bankapi && \
    chown -R bankapi:bankapi /app
USER bankapi
```

### 2. Read-Only Root Filesystem

**docker-compose.yml:**
```yaml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp
      - /app/runtime/log
```

### 3. Resource Limits

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. Network Isolation

```yaml
networks:
  bank-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### 5. Secrets Management

**Docker Secrets (Swarm mode):**
```yaml
secrets:
  secret_key:
    external: true
  encryption_key:
    external: true

services:
  api:
    secrets:
      - secret_key
      - encryption_key
```

**Create secrets:**
```bash
echo "your-secret-key" | docker secret create secret_key -
echo "your-encryption-key" | docker secret create encryption_key -
```

### 6. Security Scanning

```bash
# Scan image for vulnerabilities
docker scan invisible-bank-api:latest

# Trivy scanning
trivy image invisible-bank-api:latest
```

### 7. TLS Certificate Best Practices

**Development:**
- Self-signed certificates (auto-generated)

**Production:**
- Use Let's Encrypt for free CA-signed certificates
- Mount certificates as volumes (don't bake into image)

```yaml
services:
  api:
    volumes:
      - /etc/letsencrypt/live/api.invisiblebank.com:/app/certs:ro
```

---

## Orchestration

### Docker Swarm Deployment

**Initialize Swarm:**
```bash
docker swarm init
```

**Deploy Stack:**
```bash
docker stack deploy -c docker-compose.prod.yml bank-api
```

**Scale Services:**
```bash
docker service scale bank-api_api=5
```

**Update Service:**
```bash
docker service update --image invisible-bank-api:1.1.0 bank-api_api
```

### Kubernetes Deployment

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: invisible-bank-api
  labels:
    app: bank-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bank-api
  template:
    metadata:
      labels:
        app: bank-api
    spec:
      containers:
      - name: api
        image: invisible-bank-api:1.0.0
        ports:
        - containerPort: 8443
          name: https
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: bank-api-secrets
              key: secret-key
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: bank-api-secrets
              key: encryption-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8443
            scheme: HTTPS
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8443
            scheme: HTTPS
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: runtime
          mountPath: /app/runtime
      volumes:
      - name: runtime
        persistentVolumeClaim:
          claimName: bank-api-runtime-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: bank-api-service
spec:
  selector:
    app: bank-api
  ports:
  - protocol: TCP
    port: 443
    targetPort: 8443
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: bank-api-secrets
type: Opaque
data:
  secret-key: <base64-encoded-secret>
  encryption-key: <base64-encoded-key>
```

**Deploy to Kubernetes:**
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl get services
```

---

## Troubleshooting

### Common Issues

#### 1. Port 8443 Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8443: bind: address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8443

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "8444:8443"
```

#### 2. Permission Denied on Volumes

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/app/runtime/bank.db'
```

**Solution:**
```bash
# Fix permissions
chmod -R 777 runtime/

# Or run container as root (not recommended)
user: root
```

#### 3. Database Lock Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# SQLite doesn't handle concurrent writes well
# Use PostgreSQL for production (see ROADMAP.md)

# Or ensure only one container instance
docker-compose up -d --scale api=1
```

#### 4. Certificate Verification Failed

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```bash
# For development, use -k flag to skip verification
curl -k https://localhost:8443/health

# For production, use proper CA-signed certificates
```

#### 5. Container Exits Immediately

**Check logs:**
```bash
docker-compose logs api

# Common causes:
# - Missing .env file
# - Invalid environment variables
# - Database initialization failure
```

**Solution:**
```bash
# Run interactively to see errors
docker-compose run --rm api bash
python scripts/init_db.py
```

#### 6. Out of Memory

**Error:**
```
Container killed due to memory limit
```

**Solution:**
```yaml
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Debugging Commands

```bash
# Enter running container
docker-compose exec api bash

# View container logs with timestamps
docker-compose logs -f --timestamps api

# Inspect container
docker inspect <container-id>

# Check environment variables
docker-compose exec api env

# Test database connection
docker-compose exec api python -c "from app.db.session import engine; print(engine.connect())"

# Test API internally
docker-compose exec api curl -k https://localhost:8443/health
```

---

## Best Practices

### Development

1. **Use docker-compose for local development**
   - Fast iteration with volume mounts
   - Easy debugging with `docker-compose logs`
   - Consistent environment across team

2. **Mount source code as volume for hot reload**
   ```yaml
   volumes:
     - ./app:/app/app
   ```

3. **Use .env.local for local overrides**
   ```bash
   # .gitignore
   .env.local

   # Load in docker-compose
   env_file:
     - .env
     - .env.local
   ```

### Production

1. **Never use SQLite in production**
   - Migrate to PostgreSQL (see ROADMAP.md Phase 1)

2. **Use secrets manager for sensitive data**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Implement proper logging**
   - Centralized log aggregation (ELK, CloudWatch)
   - Structured JSON logging
   - Log rotation

4. **Use health checks**
   - Database connectivity
   - External service availability
   - Disk space

5. **Resource limits**
   - Always set CPU and memory limits
   - Prevent resource exhaustion

6. **Automated backups**
   - Daily database backups
   - Store in S3/Azure Blob
   - Test restore procedures

7. **Monitoring & Alerting**
   - Prometheus + Grafana
   - Uptime monitoring
   - Alert on failures

### Security

1. **Never commit secrets to Git**
   - Use .env files (in .gitignore)
   - Use secrets managers

2. **Run as non-root user**
   - Create dedicated user in Dockerfile

3. **Keep images updated**
   - Regularly update base images
   - Scan for vulnerabilities

4. **Use CA-signed certificates**
   - Let's Encrypt for free certs
   - Auto-renewal with certbot

5. **Network isolation**
   - Use Docker networks
   - Restrict external access

---

## Additional Resources

### Docker Documentation
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

### Project Documentation
- [README.md](./README.md) - Setup and API documentation
- [SECURITY.md](./SECURITY.md) - Security considerations
- [ROADMAP.md](./ROADMAP.md) - Future enhancements

### Tools
- [Dive](https://github.com/wagoodman/dive) - Analyze Docker image layers
- [Trivy](https://github.com/aquasecurity/trivy) - Vulnerability scanner
- [Hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter

---

## Quick Reference

### Common Commands Cheatsheet

```bash
# Build
docker-compose build                    # Build all services
docker-compose build --no-cache         # Build from scratch

# Start/Stop
docker-compose up -d                    # Start in background
docker-compose down                     # Stop and remove
docker-compose restart                  # Restart all services

# Logs
docker-compose logs -f                  # Follow all logs
docker-compose logs -f api              # Follow API logs
docker-compose logs --tail=50 api       # Last 50 lines

# Exec
docker-compose exec api bash            # Enter container shell
docker-compose exec api python -V       # Run command

# Cleanup
docker-compose down -v                  # Remove volumes
docker system prune -a                  # Remove unused resources
docker volume prune                     # Remove unused volumes

# Health
docker-compose ps                       # Service status
docker-compose top                      # Running processes
docker stats                            # Resource usage
```

---

**Version:** 1.0.0
**Last Updated:** 2025-12-05
**Maintained By:** Invisible Bank Development Team
