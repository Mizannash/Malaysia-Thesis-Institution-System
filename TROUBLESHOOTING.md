# MTIS Lecturer Troubleshooting Guide

This guide covers the top 5 most common environmental and operational issues encountered when evaluating MTIS on a fresh machine, along with exact diagnostic commands and one-line terminal fixes.

---

## 1. Port 3000 (Frontend) or Port 5432 (PostgreSQL) Already in Use

### Symptom
```
Error response from daemon: driver failed programming external connectivity on endpoint mtis-postgres-db: 
Bind for 0.0.0.0:5432 failed: port is already allocated
```
Or similar failure for port `3000` (`mtis-frontend-web`).

### Cause
A local PostgreSQL service (`pg_ctl`, system service) or another Node.js/Next.js application is already occupying port 5432 or 3000 on your host machine.

### Exact Fix
**Option A: Free the conflicting port (Recommended)**
- **macOS / Linux**:
  ```bash
  # Terminate process occupying port 5432
  sudo lsof -i :5432 -t | xargs -r sudo kill -9
  # Terminate process occupying port 3000
  sudo lsof -i :3000 -t | xargs -r sudo kill -9
  ```
- **Windows (PowerShell as Admin)**:
  ```powershell
  # Kill process using port 5432
  Stop-Process -Id (Get-NetTCPConnection -LocalPort 5432).OwningProcess -Force
  # Kill process using port 3000
  Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force
  ```

**Option B: Re-map host ports in `docker-compose.yml`**
Change the external port mappings in `docker-compose.yml`:
```yaml
db:
  ports:
    - "5433:5432"   # Map host 5433 to container 5432
frontend:
  ports:
    - "3001:3000"   # Open http://localhost:3001
```

---

## 2. Docker Daemon Not Running / Docker Desktop Stopped

### Symptom
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```
Or `error during connect: This error may indicate that the docker daemon is not running.`

### Cause
Docker Desktop or the Docker system engine is stopped.

### Exact Fix
- **macOS**:
  ```bash
  open -a Docker
  ```
  Wait until the whale icon in the status bar becomes steady.
- **Linux (systemd)**:
  ```bash
  sudo systemctl start docker && sudo systemctl enable docker
  ```
- **Windows**:
  Launch Docker Desktop from the Start menu, or run in PowerShell:
  ```powershell
  Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  ```

---

## 3. Playwright Image Pull Slow or Institutional Firewall Timeout

### Symptom
`docker compose up` hangs or fails with network timeout pulling `mcr.microsoft.com/playwright:v1.49.0-jammy` (~1.5GB image) on campus or throttled Wi-Fi.

### Cause
Institutional firewalls or bandwidth throttles blocking large Microsoft Container Registry (MCR) layers.

### Exact Fix
The Playwright headless browser service is isolated behind the Docker Compose `scraper` profile. The MTIS core system boots and runs **100% offline** on verified HTML search fixtures (`tests/fixtures/utm_search_fixture.html`) per Rubric D5.

Run Docker Compose without the optional live scraper profile:
```bash
docker compose up -d db backend frontend
```
*(This is already the automated default executed by `make demo`).*

---

## 4. Apple Silicon (M1/M2/M3/M4 ARM64) vs x86_64 Architecture

### Symptom
```
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)
```
Or container segmentation fault on older macOS Docker versions.

### Cause
Docker emulation mismatch between AMD64 binaries and ARM64 Apple Silicon.

### Exact Fix
MTIS images (`python:3.12-slim` and `postgres:17-alpine`) are official multi-platform images with native ARM64 support.
If Docker Desktop forces Rosetta AMD64 translation, set the default platform:
```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
make demo
```
In Docker Desktop for Mac: go to **Settings $\rightarrow$ General**, and ensure **"Use Rosetta for x86/amd64 emulation on Apple Silicon"** is enabled.

---

## 5. First-Boot Database Initialization Latency / Race Condition

### Symptom
Backend logs indicate:
```
OperationalError: could not connect to server: Connection refused
Is the server running on host "db" (172.x.x.x) and accepting TCP/IP connections on port 5432?
```

### Cause
On a cold boot, PostgreSQL takes 3–5 seconds to initialize its initial tables and seed data from `init.sql`.

### Exact Fix
MTIS prevents race conditions automatically through:
1. `docker-compose.yml` healthcheck on `db` service (`condition: service_healthy`).
2. An automatic retry loop in `scripts/seed.sh` that polls socket readiness for up to 30 seconds before executing migrations.

If your machine was exceptionally slow during first-time image building:
```bash
# Restart the backend service once database is ready
docker compose restart backend
# Confirm readiness via health check
curl http://localhost:8000/health
```
You should receive `{"status":"ok","service":"mtis-backend"}`.
