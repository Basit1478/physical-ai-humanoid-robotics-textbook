# Backend Deployment to Railway

## Deployment Steps

1. **Prepare for Deployment**
   - Ensure all environment variables are properly set in Railway:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `QDRANT_URL`: Your Qdrant URL
     - `QDRANT_API_KEY`: Your Qdrant API key (if applicable)
     - `JWT_SECRET`: A secure JWT secret key
     - `ENVIRONMENT`: Set to "production"

2. **Deploy to Railway**
   - Go to [Railway](https://railway.app)
   - Click "New Project"
   - Connect to your GitHub repository (or upload the backend folder)
   - Select the backend folder for deployment
   - Railway will automatically detect the Dockerfile and deploy the application
   - After deployment, you'll get a URL like: `https://your-project-name.up.railway.app`

3. **Get the Deployment URL**
   - Once deployed, copy the public URL from the Railway dashboard
   - It will typically look like: `https://your-project-name-production.up.railway.app`

## Update Frontend with Deployment URL

After deploying the backend to Railway, you need to update the frontend's API configuration:

1. Open `my-website/src/api/config.ts`
2. Replace the production URL with your Railway deployment URL:

```typescript
// API Configuration
const API_BASE_URL = typeof window !== 'undefined'
  ? window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'  // For local development
    : 'https://your-project-name-production.up.railway.app'  // Your Railway URL
  : 'http://localhost:8001';  // For server-side rendering
```

3. Rebuild and redeploy your frontend (if using a service like Netlify or Vercel)

## Important Notes

- Make sure your Qdrant instance is accessible from the Railway deployment
- The backend API endpoints will be available at your Railway URL:
  - Authentication: `https://your-project-name-production.up.railway.app/auth/`
  - RAG: `https://your-project-name-production.up.railway.app/rag/`
  - Translation: `https://your-project-name-production.up.railway.app/translate/`
  - Personalization: `https://your-project-name-production.up.railway.app/personalize/`

- For the frontend to work properly with the deployed backend, ensure CORS is configured correctly in the backend (which is already done in the main.py file)

## Environment Variables for Railway

When setting up the project on Railway, make sure to add these environment variables:

```
GEMINI_API_KEY=your_actual_gemini_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
JWT_SECRET=your_secure_jwt_secret
ENVIRONMENT=production
```