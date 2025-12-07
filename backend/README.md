# Physical AI & Humanoid Robotics Textbook Backend

This is the backend service for the Physical AI & Humanoid Robotics Textbook project, built with FastAPI. It provides APIs for content management, RAG chatbot, authentication, personalization, and translation.

**Live Site**: [https://basit1478.github.io/physical-ai-humanoid-robotics-textbook/](https://basit1478.github.io/physical-ai-humanoid-robotics-textbook/)

## Features

- **Module Management**: Create, update, and manage textbook modules and chapters
- **RAG Chatbot**: AI-powered chatbot with Retrieval-Augmented Generation for answering textbook-related questions
- **Authentication**: JWT-based authentication system with user registration and login
- **Personalization**: User profiles and personalized learning experiences
- **Translation**: Multi-language support with focus on Urdu translation
- **Content Ingestion**: APIs for uploading and processing new content
- **Reusable Intelligence**: Agent system with skill-based architecture

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints
- **SQLAlchemy**: SQL toolkit and Object Relational Mapping (ORM) library
- **LangChain**: Framework for developing applications powered by language models
- **Pydantic**: Data validation and settings management using Python type hints
- **PassLib**: Password hashing library
- **PyJWT**: JSON Web Token implementation in Python

## Installation

1. Clone the repository:
```bash
git clone https://github.com/basit1478/physical-ai-humanoid-robotics-textbook.git
cd physical-ai-humanoid-robotics-textbook/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Environment Variables

Copy `.env.example` to `.env` and update the values as needed:

- `SECRET_KEY`: Secret key for JWT tokens (use a strong random string)
- `DATABASE_URL`: Database connection string (SQLite by default)
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)
- `QDRANT_URL`: URL for Qdrant vector database (if using)
- Other configuration options as documented in `.env.example`

## Running the Application

### Development

```bash
# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Production

```bash
# Run the production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Modules & Chapters
- `GET /api/modules` - Get all modules
- `GET /api/modules/{id}` - Get specific module
- `GET /api/modules/{id}/chapters` - Get chapters for a module
- `GET /api/chapters/{id}` - Get specific chapter

### Chat
- `POST /api/chat` - Chat with the AI tutor
- `POST /api/chat/start-session` - Start a new chat session
- `GET /api/chat/sessions/{id}/history` - Get chat history
- `GET /api/chat/sessions` - Get user's chat sessions

### Personalization
- `POST /api/personalization/profile` - Set user profile
- `GET /api/personalization/profile` - Get user profile
- `GET /api/personalization/content` - Get personalized content
- `GET /api/personalization/path` - Get adaptive learning path

### Translation
- `POST /api/translation/translate` - Translate content
- `GET /api/translation/chapter/{id}` - Translate a chapter
- `GET /api/translation/module/{id}` - Translate a module
- `GET /api/translation/languages` - Get supported languages

### Content Ingestion
- `POST /api/ingestion/module` - Create a new module
- `POST /api/ingestion/chapter` - Create a new chapter
- `POST /api/ingestion/chapters/bulk` - Bulk create chapters
- `POST /api/ingestion/upload` - Upload and ingest content
- `PUT /api/ingestion/chapter/{id}` - Update a chapter

### Agents
- `POST /api/agents/query` - Query the AI agent
- `GET /api/agents/skills` - Get available skills
- `POST /api/agents/personalized-query` - Query with personalization
- `GET /api/agents/learning-path/{topic}` - Get learning path
- `GET /api/agents/table-of-contents` - Get table of contents
- `POST /api/agents/translate-query` - Query with translation

## Project Structure

```
backend/
├── app/                    # Main application
│   └── main.py            # FastAPI application
├── models/                 # Database models and schemas
│   ├── database.py        # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
├── routes/                 # API route definitions
│   ├── modules.py         # Module/chapter routes
│   ├── chat.py            # Chatbot routes
│   ├── auth.py            # Authentication routes
│   ├── personalization.py # Personalization routes
│   ├── translation.py     # Translation routes
│   ├── ingestion.py       # Content ingestion routes
│   └── agents.py          # Agent system routes
├── services/               # Business logic
│   ├── modules_service.py # Module/chapter services
│   ├── chat_service.py    # Chatbot services
│   ├── personalization_service.py # Personalization services
│   ├── translation_service.py # Translation services
│   └── ingestion_service.py # Ingestion services
├── auth/                   # Authentication utilities
│   └── better_auth.py     # JWT authentication
├── agents/                 # Agent and skill system
│   ├── main.py            # Agent system
│   ├── skills/            # Individual skills
│   │   └── content_retrieval_skill.py
│   └── registry/          # Skill registry
│       └── skill_registry.py
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables example
└── README.md              # This file
```

## Database Models

The application uses SQLAlchemy ORM with the following main models:

- **User**: User account information
- **UserProfile**: User profile with learning preferences
- **Module**: Textbook modules (e.g., "ROS 2", "Digital Twin")
- **Chapter**: Individual chapters within modules
- **UserProgress**: User progress tracking
- **Translation**: Translated content
- **ChatSession**: Chat session history
- **ChatMessage**: Individual chat messages
- **Embedding**: Vector embeddings for RAG system

## Skills System

The agent system implements a reusable intelligence approach with skills:

- **ContentRetrievalSkill**: Retrieves relevant content from the textbook
- **ChapterRetrievalSkill**: Retrieves specific chapters
- **ModuleRetrievalSkill**: Retrieves module information

Skills are registered in the `SkillRegistry` and can be extended with additional functionality.

## Translation System

The translation system supports multiple languages with a focus on Urdu:

- **Urdu (ur)**: Primary target language
- **Spanish (es)**: Secondary language
- **French (fr)**: Additional language support

The system caches translations and can be integrated with professional translation APIs.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8 .
```

## Deployment

For production deployment, consider:

1. Using a production WSGI server like Gunicorn
2. Setting `DEBUG=False` in production
3. Using a proper database (PostgreSQL recommended)
4. Setting up SSL certificates
5. Configuring proper CORS origins
6. Securing API keys and secrets

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.