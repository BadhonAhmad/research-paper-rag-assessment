# Free LLM Provider Options for RAG System

## Current Issue
The DeepSeek API key has insufficient balance (payment required).

## Solution Options

### Option 1: Use Ollama (Local, Free) ✅ RECOMMENDED
**Pros:**
- Completely free
- No API limits
- Works offline
- Privacy-focused (data stays local)

**Setup:**
```powershell
# 1. Ensure Ollama is installed (already done)

# 2. Pull a small model for CPU usage
ollama pull llama3.2:1b

# 3. Force CPU-only to avoid GPU memory errors
$env:OLLAMA_NUM_GPU="0"

# 4. Verify it works
ollama run llama3.2:1b "Say hello"

# 5. Keep Ollama running (leave this terminal open)
ollama serve
```

**In your .env:**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

---

### Option 2: OpenRouter (Free Tier Available)
**Pros:**
- Free tier with daily limits
- Access to multiple models (GPT-3.5, Claude, etc.)
- Simple API

**Setup:**
1. Sign up at https://openrouter.ai/
2. Get free API key (includes free credits)
3. Update code to use OpenRouter endpoint

**Would need code changes:**
```python
# In llm_service.py, add openrouter support
OPENROUTER_API_KEY=your-key-here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

---

### Option 3: Groq (Free Tier)
**Pros:**
- Fast inference
- Free tier available
- Good for testing

**Setup:**
1. Sign up at https://groq.com/
2. Get API key
3. Similar code structure to DeepSeek

---

### Option 4: Local LLM with Ollama (Alternative Models)
If llama3.2:1b is too slow or inaccurate, try:

```powershell
# Faster, smaller models
ollama pull tinyllama:1.1b
ollama pull phi3:mini

# Better quality (needs more RAM)
ollama pull mistral:7b-instruct
```

---

## Quick Fix (Use Ollama Now)

**I've already updated your .env to use Ollama.** 

Now do this:

1. **Set CPU-only mode for Ollama**
```powershell
$env:OLLAMA_NUM_GPU="0"
```

2. **Ensure Ollama is running** (in a separate terminal)
```powershell
ollama serve
```

3. **Restart your backend**
```powershell
cd src
python main.py
```

You should see:
```
🤖 LLM: Ollama at http://localhost:11434 (model: llama3.2:1b)
```

4. **Test a query**
- The backend will now use Ollama (free, local)
- If GPU memory errors occur, it automatically retries with CPU-only
- Answers will be generated successfully

---

## Future: Add Top-Up to DeepSeek

If you want to use DeepSeek later:
1. Add credits at https://platform.deepseek.com/
2. Change .env: `LLM_PROVIDER=deepseek`
3. Restart backend

---

## Performance Comparison

| Provider | Cost | Speed | Quality | Setup |
|----------|------|-------|---------|-------|
| Ollama (llama3.2:1b) | Free | Slow (CPU) | Good | Local |
| Ollama (mistral:7b) | Free | Medium | Better | Local (needs RAM) |
| DeepSeek | Paid | Fast | Great | API (needs credits) |
| OpenRouter | Free tier | Fast | Great | API (signup) |
| Groq | Free tier | Very fast | Good | API (signup) |

---

**Current recommendation: Stick with Ollama (already configured) for free, working solution.**
