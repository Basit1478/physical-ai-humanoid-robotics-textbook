# Backend Setup Instructions

## Environment Configuration

Before running the backend, you need to configure your environment variables in the `.env` file:

```env
# API Keys and Configuration
GEMINI_API_KEY=your-actual-gemini-api-key-here
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-actual-qdrant-api-key-here

# JWT Secret for Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

### Getting Required API Keys

1. **Gemini API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create an account or sign in
   - Create a new API key
   - Copy the key and replace `your-actual-gemini-api-key-here` in the `.env` file

2. **Qdrant API Key**:
   - If using a local Qdrant instance (default), you can leave the API key empty or remove it
   - If using Qdrant Cloud, get your API key from the Qdrant Cloud dashboard

## Running the Backend

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the Qdrant database (if not already running):
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

3. Start the backend server:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## API Endpoints

The backend provides the following API categories:

- `/auth/**` - Authentication (signup, login)
- `/rag/**` - RAG system (documents, query, chat)
- `/translate/**` - Translation services (English to Urdu)
- `/personalize/**` - Content personalization

## Frontend Integration

The Docusaurus frontend is configured to automatically connect to the backend based on the environment:
- In development (localhost): connects to `http://localhost:8001`
- In production: connects to the deployed backend URL

The frontend API utilities are located in `my-website/src/api/` and handle all communication with the backend.