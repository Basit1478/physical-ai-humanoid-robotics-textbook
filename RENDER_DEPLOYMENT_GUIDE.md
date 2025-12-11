# Render Deployment Guide

This guide provides step-by-step instructions to deploy your backend application to Render.

## Prerequisites

Before deploying, ensure you have:

1. A [Render](https://render.com) account
2. Your Google Gemini API key
3. Qdrant Cloud account (or self-hosted Qdrant instance) with URL and API key
4. A secure JWT secret

## Environment Variables Required

Before deploying, you need to set the following environment variables in your Render dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | `AIzaSy...` |
| `QDRANT_URL` | Your Qdrant Cloud URL | `https://your-cluster.xxxx.xxxx.cloud.qdrant.io:6333` |
| `QDRANT_API_KEY` | Your Qdrant API key (if applicable) | `your-secure-api-key` |
| `JWT_SECRET` | Secure secret for JWT tokens (32+ characters) | `a-very-long-and-secure-random-string` |
| `ENVIRONMENT` | Set to `production` | `production` |
| `DEBUG` | Set to `false` for production | `false` |

## Deployment Steps

### Option 1: Deploy via GitHub Integration (Recommended)

1. **Push your code to GitHub**
   - Make sure your repository is public or you have granted Render access to your private repository
   - Ensure the `backend/` directory contains your FastAPI application

2. **Create a new Web Service on Render**
   - Go to your Render dashboard
   - Click "New +" → "Web Service"
   - Connect to your GitHub repository
   - Select the repository containing your backend code

3. **Configure the build and deployment**
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile.render`
   - **Root Directory**: `/` (root of the repository)
   - **Build Command**: Leave blank (Dockerfile handles building)
   - **Start Command**: Leave blank (Dockerfile handles this)

4. **Set Environment Variables**
   - In the "Environment Variables" section, add all the required variables listed above

5. **Review and Create**
   - Review your configuration
   - Click "Create Web Service"

### Option 2: Manual Deployment

1. **Prepare your repository**
   - Ensure your code is in a Git repository
   - Make sure `backend/Dockerfile.render` exists and is properly configured

2. **Create a new Web Service**
   - Go to your Render dashboard
   - Click "New +" → "Web Service"
   - Connect to your Git provider
   - Select your repository

3. **Configure the service**
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile.render`
   - **Root Directory**: `/`
   - **Branch**: `main` (or your default branch)

4. **Set Environment Variables**
   - Add all required environment variables in the "Environment Variables" section

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

## Configuration Details

### Dockerfile.render
The provided `Dockerfile.render` is optimized for Render deployment:
- Uses Python 3.11-slim base image
- Installs system dependencies (gcc, g++)
- Copies backend files
- Exposes port 8000
- Uses Render's PORT environment variable
- Starts the application with uvicorn

### Application Settings
- The application listens on `0.0.0.0` and the port specified by the `PORT` environment variable
- CORS is configured to allow all origins (adjust for production as needed)
- All sensitive configuration is handled through environment variables

## Environment Variables Setup

### 1. GEMINI_API_KEY
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create an API key
- Add it as `GEMINI_API_KEY` in Render

### 2. QDRANT Configuration
- For Qdrant Cloud:
  - Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
  - Create a cluster
  - Get the URL and API key
- For self-hosted Qdrant:
  - Deploy your own Qdrant instance
  - Ensure it's accessible from the internet
  - Use the public URL

### 3. JWT_SECRET
Generate a secure secret using one of these methods:

```bash
# Using OpenSSL (Linux/Mac)
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Health Check

Once deployed, you can check if your service is running by visiting:
`https://<your-service-name>.onrender.com/`

You should receive a response like:
```json
{
  "message": "Textbook Project Backend API",
  "version": "1.0.0"
}
```

## API Endpoints

After successful deployment, your API endpoints will be available at:
- `https://<your-service-name>.onrender.com/auth/` - Authentication endpoints
- `https://<your-service-name>.onrender.com/rag/` - RAG system endpoints
- `https://<your-service-name>.onrender.com/translate/` - Translation endpoints
- `https://<your-service-name>.onrender.com/personalize/` - Personalization endpoints

## Troubleshooting

### Common Issues:

1. **Application fails to start**
   - Check that all required environment variables are set
   - Verify that your Qdrant instance is accessible
   - Check that your Gemini API key is valid

2. **Qdrant connection errors**
   - Ensure your Qdrant URL is correct
   - Verify your Qdrant API key is valid
   - Check that your Qdrant instance allows external connections

3. **API rate limits**
   - Monitor your Gemini API usage
   - Consider implementing rate limiting for production

### Logs
- Check application logs in your Render dashboard
- Look for environment variable errors
- Verify all dependencies are installed correctly

## Scaling

Render automatically handles basic scaling. For high-traffic applications, consider:
- Upgrading to higher-tier instances
- Implementing caching for expensive operations
- Optimizing database queries

## Security Notes

- Never expose your API keys in client-side code
- Use HTTPS for all API calls
- Regularly rotate your API keys
- Monitor your API usage for unusual patterns