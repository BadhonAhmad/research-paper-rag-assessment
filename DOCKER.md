# 🐳 Docker Compose Quick Start

Complete one-command setup for the RAG system using Docker.

## 📋 Prerequisites

- Docker Desktop installed and running
- Docker Compose v2+
- 4GB+ RAM available
- Gemini API key

## 🚀 Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.docker .env

# Edit with your API key
# GEMINI_API_KEY=your-actual-key-here
```

Or on Windows:
```powershell
Copy-Item .env.docker .env
# Then edit .env with your Gemini API key
```

### 2. Start Everything

```bash
docker-compose up -d
```

That's it! The system will:
- Start Qdrant on port 6333
- Build and start the backend on port 8000
- Build and start the frontend on port 3000

### 3. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## 📊 Check Status

```bash
# View logs
docker-compose logs -f

# Check specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f qdrant

# Check running containers
docker-compose ps
```

## 🛑 Stop/Restart

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

## 🔧 Development Workflow

### Code Changes

The services use volume mounts, so changes are reflected automatically:

**Backend:**
- Edit files in `src/`
- Press Ctrl+C in terminal
- Run `docker-compose restart backend`

**Frontend:**
- Edit files in `frontend/`
- Changes are hot-reloaded automatically

### View Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Access Container Shell

```bash
# Backend
docker exec -it rag-backend /bin/bash

# Frontend
docker exec -it rag-frontend /bin/sh

# Qdrant
docker exec -it rag-qdrant /bin/sh
```

## 🗄️ Data Persistence

Data is persisted in Docker volumes:
- `qdrant_storage` - Vector database
- `backend_data` - SQLite database and uploaded files

Even if you stop containers, your data remains.

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing GEMINI_API_KEY in .env
# - Port 8000 already in use
# - Qdrant not ready yet (wait 10s and check again)
```

### Frontend build fails
```bash
# Rebuild without cache
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Qdrant connection issues
```bash
# Verify Qdrant is healthy
curl http://localhost:6333/health

# Restart Qdrant
docker-compose restart qdrant
```

### Port conflicts
```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000
netstat -ano | findstr :6333

# Kill the process or change ports in docker-compose.yml
```

## 🧹 Clean Up

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all -v

# Complete cleanup
docker system prune -a --volumes
```

## 🔄 Update After Changes

```bash
# After modifying requirements.txt or package.json
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or just rebuild specific service
docker-compose build --no-cache backend
docker-compose up -d backend
```

## 📝 Environment Variables

Override defaults by editing `.env`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Gemini (REQUIRED)
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Database
DATABASE_URL=sqlite:///./research_papers.db
```

## 🎯 Production Deployment

For production, modify `docker-compose.yml`:

1. Remove volume mounts
2. Set `NODE_ENV=production` for frontend
3. Add proper secrets management
4. Configure reverse proxy (nginx)
5. Enable HTTPS
6. Set restart policy to `always`

## 📦 What's Running?

| Service | Port | Purpose |
|---------|------|---------|
| frontend | 3000 | Next.js UI |
| backend | 8000 | FastAPI server |
| qdrant | 6333 | Vector DB API |
| qdrant | 6334 | Vector DB gRPC |

## 🚀 Quick Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild
docker-compose up -d --build

# Clean slate
docker-compose down -v && docker-compose up -d --build
```

---

**Need help?** Check logs with `docker-compose logs -f` or open an issue.
