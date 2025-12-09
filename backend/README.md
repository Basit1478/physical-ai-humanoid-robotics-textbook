# Textbook Project Backend

This is the backend for the textbook project, built with FastAPI. It provides 4 main API categories:
- `/auth/**` - Authentication system
- `/rag/**` - RAG (Retrieval Augmented Generation) chatbot
- `/translate/**` - Urdu translation services
- `/personalize/**` - Content personalization

## Architecture

The backend follows a modular structure:

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not committed)
├── auth/                  # Authentication module
│   ├── __init__.py
│   └── auth_api.py
├── rag_chatbot/          # RAG chatbot module
│   ├── __init__.py
│   └── rag_api.py
├── translate_urdu/       # Urdu translation module
│   ├── __init__.py
│   └── translate_api.py
├── personalize/          # Personalization module
│   ├── __init__.py
│   └── personalize_api.py
└── utils/                # Utility modules
    ├── __init__.py
    └── gemini_agent.py
```

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your API keys to the `.env` file:
     ```bash
     GEMINI_API_KEY=your-gemini-api-key-here
     QDRANT_URL=http://localhost:6333  # Or your Qdrant cloud URL
     QDRANT_API_KEY=your-qdrant-api-key-here
     JWT_SECRET=your-super-secret-jwt-key-change-in-production
     ```

3. **Install Qdrant:**
   You can run Qdrant locally using Docker:
   ```bash
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
   ```

## API Endpoints

### Authentication (`/auth/**`)
- `POST /auth/signup` - User registration with software/hardware background
- `POST /auth/login` - User login

### RAG Chatbot (`/rag/**`)
- `POST /rag/documents` - Add documents to vector database
- `POST /rag/query` - Query documents from vector database
- `POST /rag/chat` - Chat with RAG (query documents and generate response)
- `GET /rag/collections` - Get list of collections
- `DELETE /rag/documents/{doc_id}` - Delete a document
- `GET /rag/health` - Health check

### Translation (`/translate/**`)
- `POST /translate` - Translate text (default: English to Urdu)
- `POST /batch-translate` - Translate multiple texts
- `POST /transliterate` - Convert Urdu to Roman Urdu
- `POST /urdu-to-english` - Translate from Urdu to English
- `GET /supported-languages` - Get supported languages
- `GET /health` - Health check

### Personalization (`/personalize/**`)
- `POST /personalize/preferences` - Set user preferences
- `POST /personalize/content` - Personalize content based on user preferences
- `GET /personalize/profile/{user_id}` - Get user profile

## Running the Application

```bash
# Run the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## Frontend Integration

The backend is configured with CORS to allow communication with the Docusaurus frontend. Make sure your frontend connects to the appropriate backend endpoints.

## Technologies Used

- **FastAPI** - Web framework
- **Gemini** - AI model for RAG, translation, and personalization
- **Qdrant** - Vector database for RAG
- **JWT** - Authentication
- **Sentence Transformers** - For document embeddings
- **OpenAI Agents SDK** - Simulated interface for Gemini

## Environment Variables

- `GEMINI_API_KEY` - Your Google Gemini API key
- `QDRANT_URL` - URL for Qdrant vector database
- `QDRANT_API_KEY` - API key for Qdrant (if using cloud)
- `JWT_SECRET` - Secret key for JWT token generation
- `ENVIRONMENT` - Environment setting (development/production)
- `DEBUG` - Enable/disable debug mode