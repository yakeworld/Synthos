# SearXNG Docker Troubleshooting Playbook

## Diagnosis Flow

```
docker ps --filter name=searxng
  → running + port 8080 → 000
    → docker logs --tail 50
      → "Unexpected exit from worker-1"
        → check msgspec: docker exec searxng python3 -c "import msgspec"
        → check limiter.toml schema validity
        → check settings.yml existence
          → "settings.yml does not exist, creating from template"
            → volume mount overwriting bind mount
```

## Symptoms → Causes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Container restarting loop | limiter.toml schema invalid | Remove/fix limiter.toml |
| 403 Forbidden on /search | settings.yml missing engines | Add engines config |
| Worker crash after start | Missing msgspec module | pip install msgspec in entrypoint |
| Worker crash after start | External fetch (clearurls/wikidata) timeout | Set outgoing.timeout in settings.yml |
| No output from search | Volume mount overwriting bind mount | Use named volume for /etc/searxng |
| docker ps running but port 000 | Worker silently crashed | docker logs --tail 50 |

## Key File Paths

- **Host config**: `/home/yakeworld/searxng/settings.yml`
- **Host compose**: `/home/yakeworld/searxng/docker-compose.yaml`
- **Container config**: `/etc/searxng/settings.yml`
- **Container entrypoint**: `/usr/local/searxng/entrypoint.sh`
- **Container webapp**: `/usr/local/searxng/searx/webapp.py`

## Docker Compose (Known-Good)

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./settings.yml:/etc/searxng/settings.yml:ro
    command: /bin/sh -c "pip install msgspec && /usr/local/searxng/entrypoint.sh"
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
      - SEARXNG_SECRET=<random>
    cap_drop:
      - NET_RAW
    networks:
      - searxng
```

## Network Notes

- Server IP blocked by Google/DuckDuckGo HTML endpoints (CAPTCHA)
- Docker Hub mirror `https://docker.1ms.run` may fail (connection reset)
- Baidu reachable from container, Google may timeout
- IPv6 path to Docker Hub gets "read: connection reset by peer"
- Fix: ensure container network can reach search engine APIs
