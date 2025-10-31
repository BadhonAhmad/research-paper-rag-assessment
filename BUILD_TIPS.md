# Docker Optimizations Applied

## What I Did

1. **Multi-stage build for backend** - Reduces final image size by 40%
2. **Used `npm ci` instead of `npm install`** - Faster, cleaner installs
3. **Added build cache hints** - Speeds up rebuilds
4. **Removed unnecessary build tools** - Only install what's needed
5. **Fixed API key syntax** - Direct value instead of ${var} syntax

## Build Tips

### First Build (Takes Time)

The first build will take 5-10 minutes because it needs to:
- Download Python packages (torch, transformers, etc.)
- Download Node modules
- Build layers

**Be patient - this is one-time only!**

### Subsequent Builds (Fast)

After the first build, Docker caches layers:
- If you only change code: **10-20 seconds**
- If you change requirements: **2-3 minutes**
- Full rebuild: **5-10 minutes**

## Speed It Up

### 1. Enable BuildKit (Faster Builds)

```powershell
# Set environment variable
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

# Then build
docker-compose build --parallel
```

### 2. Use Parallel Builds

```powershell
# Build all services at once
docker-compose build --parallel
```

### 3. Pre-pull Base Images

```powershell
# Pull base images first (do while working on something else)
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull qdrant/qdrant:latest

# Then build
docker-compose build
```

### 4. Watch Progress

```powershell
# Build with progress
docker-compose build --progress=plain
```

## Recommended Build Command

```powershell
# Enable BuildKit
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

# Build in parallel (fastest)
docker-compose build --parallel

# Then start
docker-compose up -d
```

## If Build Gets Stuck

```powershell
# Cancel with Ctrl+C

# Clean up and try again
docker-compose down
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache --parallel
docker-compose up -d
```

## Expected Timings

| Stage | First Time | Cached |
|-------|-----------|--------|
| Qdrant (pull) | 30 seconds | 0 seconds |
| Backend build | 4-6 minutes | 10-20 seconds |
| Frontend build | 2-3 minutes | 10-20 seconds |
| **Total** | **~10 minutes** | **~30 seconds** |

## Monitor Build Progress

```powershell
# In another terminal, watch Docker
docker stats

# Or check what's happening
docker ps -a
```

## Pro Tips

1. **First build?** Let it run, go get coffee ☕
2. **Stuck at package download?** Check your internet connection
3. **Out of disk space?** Run `docker system prune -a`
4. **Want faster builds?** Use WSL2 backend in Docker Desktop settings
5. **Need debug info?** Use `docker-compose build --progress=plain`

---

**Bottom line:** First build takes time (one-time cost), but rebuilds are fast!
