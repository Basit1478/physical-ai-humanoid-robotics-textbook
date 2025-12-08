# Backend Deployment Guide

This guide explains how to deploy the Physical AI & Humanoid Robotics Textbook backend API for production.

## Prerequisites

1. Docker and Docker Compose installed
2. Git (for cloning the repository)
3. At least 4GB RAM available for all services

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathon-book-1
```

### 2. Configure Environment Variables

Copy the production environment file and customize it:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file to set your actual values for:
- `SECRET_KEY` - Generate a strong secret key
- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_API_KEY` - Your Qdrant API key (if using cloud Qdrant)
- Database credentials
- Allowed origins for CORS

### 3. Deploy Using Docker Compose

From the root directory of the project:

```bash
# On Linux/Mac:
./deploy-backend.sh

# On Windows:
deploy-backend.bat
```

Or manually:

```bash
docker-compose up -d --build
```

### 4. Verify Deployment

Check if services are running:

```bash
docker-compose ps
```

Access the API:
- API Base URL: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## Services Overview

The deployment includes:

1. **Backend API** (FastAPI application)
2. **PostgreSQL Database** for user data and profiles
3. **Qdrant Vector Database** for RAG functionality

## Configuration Options

### Environment Variables

Key environment variables that should be customized for production:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `your-secret-key-change-in-production` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `QDRANT_URL` | Qdrant service URL | `http://qdrant:6333` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/textbook_db` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,https://yourdomain.com` |

### Scaling Options

To scale the backend service:

```bash
docker-compose up -d --scale backend=3
```

## Monitoring and Maintenance

### View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### Update Deployment

To update the deployment after making changes:

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 8000, 5432, or 6333 are already in use, modify the docker-compose.yml file to use different ports.

2. **Insufficient memory**: Ensure your system has at least 4GB RAM available.

3. **Permission issues**: Make sure Docker has necessary permissions to access the project directory.

### Health Checks

Use the built-in health check endpoint:

```bash
curl http://localhost:8000/health
```

## Security Considerations

1. Always change the default passwords in production
2. Use strong, randomly generated SECRET_KEY
3. Restrict ALLOWED_ORIGINS to your actual frontend domains
4. Use HTTPS in production (not configured in this basic setup)
5. Regularly update dependencies

## Integration Testing

Run the integration test script to verify frontend-backend communication:

```bash
python test-integration.py
```

This will test:
- Backend health status
- Root endpoint functionality
- API documentation accessibility
- Frontend access to backend configuration