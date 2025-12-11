# Backend Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Update API Keys (REQUIRED)

Your current API keys are invalid/leaked. Get new ones:

1. **Gemini API Key** (FREE):
   - Visit: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Qdrant API Key** (FREE):
   - Visit: https://cloud.qdrant.io/
   - Sign in to your account
   - Go to your cluster → API Keys
   - Copy the key

3. **Update `.env` file**:
   ```bash
   cd backend
   # Edit .env file and replace these values:
   GEMINI_API_KEY="your-new-gemini-key-here"
   QDRANT_API_KEY="your-new-qdrant-key-here"
   ```

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**What gets installed**:
- FastAPI - Web framework
- Uvicorn - ASGI server
- Qdrant Client - Vector database
- httpx - HTTP client for Gemini API
- Pydantic - Data validation
- Other auth/security packages

### Step 3: Run the Backend

```bash
# From the backend directory
python main.py
```

**Expected output**:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ✅ Verify It's Working

### Test the health endpoint:
```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{"status":"healthy","service":"backend-api"}
```

### Test user signup:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123",
    "full_name": "Test User",
    "software_background": "Python, JavaScript",
    "hardware_background": "Arduino, Raspberry Pi"
  }'
```

**Expected response**:
```json
{
  "user_id": "uuid-here",
  "software_background": "Python, JavaScript",
  "hardware_background": "Arduino, Raspberry Pi",
  "token": "secure-token-here"
}
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🔌 Available Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login existing user
- `GET /auth/me` - Get user profile (requires token)
- `POST /auth/logout` - Logout user

### RAG Chatbot (`/rag`)
- `POST /rag/query` - Ask questions about the book
- `POST /rag/embed-content` - Add content to knowledge base
- `GET /rag/health` - RAG service health check

### Translation (`/translate`)
- `POST /translate/chapter` - Translate chapter to Urdu
- `GET /translate/chapter/{id}/cached` - Get cached translation
- `GET /translate/health` - Translation service health check

### Personalization (`/personalize`)
- `POST /personalize/chapter` - Personalize content for user
- `GET /personalize/chapter/{id}/cached` - Get cached personalization
- `GET /personalize/health` - Personalization service health check

## 🐛 Troubleshooting

### Problem: "Gemini API error"
**Solution**: Check your `GEMINI_API_KEY` in `.env` file

### Problem: "Qdrant 403 Forbidden"
**Solution**: Verify your `QDRANT_API_KEY` is correct and active

### Problem: "Module not found"
**Solution**: Run `pip install -r requirements.txt` again

### Problem: "Port 8000 already in use"
**Solution**:
```bash
# Change port in .env file
PORT=8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

## 🔧 Development Tips

### Run with auto-reload (for development):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Check logs:
The backend logs all errors to console. Watch for:
- `WARNING:` - Non-critical issues
- `ERROR:` - Things that need fixing
- `INFO:` - Normal operation

### Test with curl:
```bash
# Save token from signup/login
TOKEN="your-token-here"

# Use token for authenticated requests
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## 📦 What Changed from Previous Version?

1. ✅ **Removed forbidden dependency**: No more `google-generativeai`
2. ✅ **Direct REST API**: Now uses Gemini REST API via `httpx`
3. ✅ **Better security**: Added proper password hashing
4. ✅ **Fixed model name**: Changed to `gemini-pro` (v1beta compatible)
5. ✅ **Cleaner code**: Removed unnecessary dependencies

## 🎯 Next Steps

1. Update your API keys (see Step 1)
2. Start the backend server
3. Test all endpoints
4. Connect your Docusaurus frontend
5. Deploy to production (Render/Vercel/Railway)

## 💡 Need Help?

Check these files for more info:
- `FIXES_APPLIED.md` - Detailed list of fixes
- `IMPLEMENTATION_SUMMARY.md` - Original implementation details
- `README.md` - General backend information

---

**Ready to go?** Start with Step 1 above! 🚀
