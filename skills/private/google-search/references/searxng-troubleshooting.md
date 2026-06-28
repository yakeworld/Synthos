# SearXNG Troubleshooting Guide

## Common Failure Modes

### 1. Granian Worker Silent Crash

**Symptom**: Logs show `[ERROR] Unexpected exit from worker-1` with no Python traceback.

**Root Cause**: Error happens during module import (e.g., missing `msgspec`) before Python can write to stdout/stderr.

**Diagnosis**:
```bash
# Check if webapp module imports correctly
docker exec <container> python3 -c "import searx.webapp"
# If this shows ImportError/ModuleNotFoundError, that's the root cause
```

**Fix**: Install missing dependencies inside the container:
```bash
docker exec <container> /usr/local/searxng/.venv/bin/pip install <missing-package>
```

### 2. Settings File Extension

**Symptom**: Container starts but search returns no results or error 404.

**Root Cause**: SearXNG 2026+ expects `settings.yml` (not `.yaml`).

**Fix**: Rename file and update docker-compose.yaml:
```bash
mv settings.yaml settings.yml
# Update docker-compose.yaml volumes section
```

### 3. Limiter.toml Schema

**Symptom**: Container crashes with `TypeError: schema of /etc/searxng/limiter.toml is invalid!`

**Root Cause**: Simple format `[limiter]\nenabled = false` may not satisfy newer schema validation.

**Fix**: Check SearXNG version-specific limiter.toml schema requirements. See upstream docs for exact format.

### 4. Volume Mount Conflicts

**Symptom**: Configuration files not visible in container despite bind mount.

**Root Cause**: Docker volume and bind mount to same path — volume takes precedence.

**Diagnosis**:
```bash
docker inspect --format '{{json .Mounts}}' <container>
```

**Fix**: Remove conflicting volume definition from docker-compose.yaml.

### 5. Container Restart Loop

**Symptom**: Container status shows `restarting` repeatedly.

**Root Cause**: Any of the above issues cause continuous restart cycle.

**Fix**: Stop container, fix root cause, restart:
```bash
docker compose down
# Fix issue
docker compose up -d
```

## Quick Reference

| Symptom | Check | Fix |
|---------|-------|-----|
| `Unexpected exit from worker-1` | `docker exec python3 -c "import searx.webapp"` | Install missing deps |
| No search results | `ls /etc/searxng/settings.*` | Rename to `.yml` |
| `TypeError` on limiter.toml | Check schema format | Update to correct format |
| Config files not visible | `docker inspect --format '{{json .Mounts}}'` | Remove volume conflict |
| Continuous restarts | `docker logs --tail 50` | Fix root cause above |
