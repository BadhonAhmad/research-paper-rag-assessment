# 🚀 Quick Start Guide

## Complete RAG System Setup

You now have a full-stack RAG system with:
- ✅ FastAPI backend (Python)
- ✅ Next.js frontend (TypeScript + Tailwind)
- ✅ Qdrant vector database
- ✅ Ollama LLM integration

---

## Start the System

### 1. Start Backend (Terminal 1)

```powershell
# Navigate to backend
cd "C:\Users\Nobel\Desktop\Projects\Intern Project\research-paper-rag-assessment\src"

# Start the API server
python main.py
```

**Wait for**:
```
🚀 Starting Research Paper RAG System
📡 API: http://0.0.0.0:8000
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (Terminal 2)

```powershell
# Navigate to frontend
cd "C:\Users\Nobel\Desktop\Projects\Intern Project\research-paper-rag-assessment\frontend"

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

**Wait for**:
```
ready - started server on 0.0.0.0:3000
```

### 3. Open Browser

Go to: **http://localhost:3000**

---

## Test the System

### Option 1: Use the Web UI

1. **Upload Papers**
   - Click "Upload Papers" in nav
   - Upload one or more PDFs from `../sample_papers/`
   - Wait for processing to complete

2. **Query**
   - Click "Query Papers" in nav
   - Ask: "What methodology was used in the transformer paper?"
   - View answer with citations

3. **View Papers**
   - Click "All Papers" to see uploaded papers
   - Delete papers if needed

4. **History**
   - Click "Query History" to see past queries

### Option 2: Use the API Directly

```powershell
# Upload a paper
curl -X POST "http://localhost:8000/api/papers/upload" `
  -F "file=@sample_papers/paper_1.pdf"

# List papers
curl "http://localhost:8000/api/papers"

# Query
$body = @{
  question = "What is machine learning?"
  top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# View API docs
# Open: http://localhost:8000/docs
```

---

## Troubleshooting

### Ollama 500 Errors or GPU OOM

If queries return empty answers with messages like "Ollama API error: 500" or you see "unable to load full model on GPU":

```powershell
# 1) Check if Ollama is running
curl http://localhost:11434

# 2) Start the server if needed (keep this terminal open)
ollama serve

# 3) Pull a small model (one-time)
ollama pull llama3.2:1b

# 4) Test generation with CPU only
ollama run llama3.2:1b -o num_gpu=0 "Say hello"

# 5) Ensure backend uses the small model
# Edit src/.env and set:
# OLLAMA_MODEL=llama3.2:1b

# 6) Restart backend for env changes to take effect
```

Notes:
- The backend now automatically retries generation with CPU-only if a GPU error occurs.
- You can force CPU-only at the CLI with: `-o num_gpu=0`.

### Port Already in Use

```powershell
# Backend (8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Frontend Can't Connect to Backend

1. Ensure backend is running on port 8000
2. Check CORS is enabled (already configured)
3. Try: `curl http://localhost:8000/` (should return JSON)

---

## System Architecture

```
┌─────────────────┐
│   Browser       │
│  localhost:3000 │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Next.js        │
│  Frontend       │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐      ┌──────────┐      ┌──────────┐
│  FastAPI        │─────▶│  Qdrant  │      │  Ollama  │
│  Backend        │      │  :6333   │      │  :11434  │
│  :8000          │      └──────────┘      └──────────┘
└─────────────────┘            │
         │                     │
         ▼                     ▼
    SQLite DB          Vector Store
    (metadata)         (embeddings)
```

---

## Available Endpoints

### Backend API (port 8000)
- `GET /` - Health check
- `GET /docs` - Interactive API docs
- `POST /api/papers/upload` - Upload PDF
- `GET /api/papers` - List all papers
- `GET /api/papers/{id}` - Get paper details
- `DELETE /api/papers/{id}` - Delete paper
- `POST /api/query` - Query papers
- `GET /api/queries/history` - Query history
- `GET /api/analytics/popular` - Popular topics

### Frontend (port 3000)
- `/` - Home
- `/upload` - Upload papers
- `/papers` - View all papers
- `/query` - Query interface
- `/history` - Query history

---

## Next Steps

1. ✅ Upload all 5 sample papers
2. ✅ Test with queries from `test_queries.json`
3. ✅ Check query history and analytics
4. 📝 Document your approach in `APPROACH.md`
5. 📝 Update root `README.md` with your implementation details
6. 🚀 Submit your work

---

## Performance Tips

- First upload is slower (model loading)
- First query per session is slower (model loading)
- Adjust `top_k` for faster queries (lower = faster)
- Use smaller Ollama model for speed (llama3.2:1b)

Enjoy your RAG system! 🎉
