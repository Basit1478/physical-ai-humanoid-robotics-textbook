# Physical AI & Humanoid Robotics Book Platform Backend

This is the backend API for the educational book platform with AI features, user authentication, and content personalization.

## Features

- **Authentication System**: User signup/login with background information
- **RAG Chatbot**: AI-powered Q&A system with book content
- **Translation**: Urdu translation of book content
- **Personalization**: Content tailored to user's background

## Tech Stack

- **Framework**: FastAPI (Python)
- **Vector Database**: Qdrant
- **AI Service**: Google Gemini
- **Authentication**: Better-Auth

## API Endpoints

### Authentication (`/auth/**`)
- `POST /auth/signup` - User registration with background info
- `POST /auth/login` - User login
- `GET /auth/me` - Get user profile

### RAG Chatbot (`/rag/**`)
- `POST /rag/query` - Chat with book content
- `POST /rag/embed-content` - Add content to knowledge base

### Translation (`/translate/**`)
- `POST /translate/chapter` - Translate chapter to Urdu
- `GET /translate/chapter/{id}/cached` - Get cached translation

### Personalization (`/personalize/**`)
- `POST /personalize/chapter` - Personalize chapter content
- `GET /personalize/chapter/{id}/cached` - Get cached personalization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
QDRANT_URL=https://your-qdrant-cluster.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key
GEMINI_API_KEY=your-gemini-api-key
BETTER_AUTH_SECRET=your-better-auth-secret
JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://yourdomain.github.io
PORT=8000
```

3. Run the application:
```bash
python main.py
```

## Environment Variables

- `QDRANT_URL` - URL for your Qdrant cluster
- `QDRANT_API_KEY` - API key for Qdrant
- `GEMINI_API_KEY` - Google Gemini API key
- `BETTER_AUTH_SECRET` - Secret for authentication
- `JWT_SECRET` - Secret for JWT tokens
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
- `PORT` - Port to run the server on (default: 8000)

## Development

The backend is structured as follows:

```
backend/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── auth/               # Authentication system
├── rag-chatbot/        # RAG chatbot system
├── translate-urdu/     # Urdu translation API
└── personalize/        # Content personalization API
```

## Deployment

The application can be deployed to any platform that supports Python/FastAPI applications (Railway, Render, Vercel, etc.).