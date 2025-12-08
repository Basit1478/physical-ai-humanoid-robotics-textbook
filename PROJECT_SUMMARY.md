# Physical AI & Humanoid Robotics Textbook - Complete Setup Guide

## Project Overview

This project provides a complete educational platform for Physical AI & Humanoid Robotics with the following features:

1. **Interactive Textbook** - Docusaurus-based frontend with multilingual support
2. **RAG Chatbot** - Retrieval-Augmented Generation chatbot for answering questions
3. **Personalization** - Adaptive learning paths based on user profiles
4. **Translation** - Real-time translation to Urdu and other languages
5. **Authentication** - Secure user registration and login
6. **Content Management** - Module and chapter management system

## System Architecture

```
Frontend (Docusaurus) ←→ Backend API (FastAPI) ←→ Database (PostgreSQL + Qdrant)
                              ↓
                        OpenAI Models
```

### Components

1. **Frontend** (`my-website/`)
   - Docusaurus website hosted on GitHub Pages
   - Responsive design with mobile support
   - Urdu language support with RTL layout
   - Interactive modules and chapters

2. **Backend** (`backend/`)
   - FastAPI REST API
   - PostgreSQL database for user data
   - Qdrant vector database for RAG
   - JWT-based authentication
   - OpenAI integration for chat and embeddings

3. **Services**
   - Authentication and user management
   - Content delivery and personalization
   - RAG chatbot with vector search
   - Real-time translation
   - Adaptive learning paths

## Deployment Architecture

### Production Deployment

The system is designed for containerized deployment using Docker Compose:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Services      │
│   (GitHub       │◄──►│   (FastAPI)      │◄──►│   (OpenAI,      │
│    Pages)       │    │                  │    │    Qdrant)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       │   (User Data)    │
                       └──────────────────┘
```

### Container Services

1. **Backend API** - Main application service
2. **PostgreSQL** - User data and profiles
3. **Qdrant** - Vector storage for RAG
4. **Frontend** - Static site on GitHub Pages

## Setup Instructions

### Prerequisites

- Node.js 16+
- Python 3.8+
- Docker and Docker Compose
- Git
- OpenAI API key
- Qdrant account (optional, can use local)

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd my-website
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

4. Build for production:
   ```bash
   npm run build
   ```

5. Deploy to GitHub Pages:
   ```bash
   npm run deploy
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. Start development server:
   ```bash
   python -m app.main
   ```

### Production Deployment

1. From the root directory:
   ```bash
   # On Linux/Mac:
   ./deploy-backend.sh

   # On Windows:
   deploy-backend.bat
   ```

2. Or manually with Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Personalization
- `POST /api/personalization/profile` - Set user profile
- `GET /api/personalization/profile` - Get user profile
- `GET /api/personalization/content` - Get personalized content
- `GET /api/personalization/path` - Get adaptive learning path
- `POST /api/personalization/urdu-mode` - Enable Urdu personalization
- `GET /api/personalization/urdu-status` - Check Urdu mode status

### Translation
- `POST /api/translate` - Translate text
- `POST /api/translate/batch` - Batch translate texts

### Chat
- `POST /api/chat/query` - Ask question with RAG
- `POST /api/chat/reset` - Reset chat session

### Modules
- `GET /api/modules` - List all modules
- `GET /api/modules/{module_id}` - Get specific module
- `GET /api/modules/{module_id}/chapters` - Get chapters for module
- `GET /api/chapters/{chapter_id}` - Get specific chapter

## Features Implemented

### ✅ Core Features
- [x] Interactive textbook with modular content
- [x] User authentication and profile management
- [x] RAG chatbot with Qdrant vector store
- [x] Personalization engine with adaptive learning
- [x] Real-time translation (Urdu, Spanish, French, etc.)
- [x] Responsive design for all devices

### ✅ Advanced Features
- [x] Urdu language support with RTL layout
- [x] OpenAI Agents SDK integration
- [x] Docker containerization for easy deployment
- [x] GitHub Pages deployment for frontend
- [x] Comprehensive API documentation

### ✅ Security Features
- [x] JWT-based authentication
- [x] Password hashing with bcrypt
- [x] CORS protection
- [x] Input validation and sanitization

## Testing

### Backend Integration Test
Run the integration test script to verify all services work together:

```bash
python test-integration.py
```

### Manual Testing
1. Visit the frontend at your deployed URL
2. Register a new user account
3. Log in and set up your profile
4. Enable Urdu personalization
5. Navigate through modules and chapters
6. Use the chatbot to ask questions
7. Test translation features

## Maintenance

### Updates
1. Pull latest changes from repository
2. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Monitoring
- Check service status: `docker-compose ps`
- View logs: `docker-compose logs -f`

### Backup
- Database backups: Use standard PostgreSQL backup procedures
- Vector store: Qdrant snapshots

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Ensure 4GB+ RAM available
3. **API key errors**: Verify OpenAI/Qdrant keys in .env
4. **Database connection**: Check database credentials

### Getting Help
- Check logs: `docker-compose logs`
- API documentation: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

## Future Enhancements

### Planned Features
- Mobile app development
- Additional language support
- Advanced analytics dashboard
- Offline mode for content
- Collaborative features
- Assessment and quizzes

### Scalability Improvements
- Load balancing for high traffic
- CDN for content delivery
- Caching layer for improved performance
- Microservice architecture

## Conclusion

This project provides a complete educational platform for Physical AI & Humanoid Robotics with modern web technologies, AI integration, and multilingual support. The system is production-ready with containerized deployment and follows security best practices.