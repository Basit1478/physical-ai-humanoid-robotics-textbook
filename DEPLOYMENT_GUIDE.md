# 🚀 Quick Deployment Guide

## Backend → Railway

### Step 1: Prepare Your Backend for Deployment

1. Make sure you have the following files in your `backend` directory:
   - `main.py` - Main FastAPI application
   - `requirements.txt` - Python dependencies
   - `Dockerfile` - Container configuration
   - All your API modules (auth, rag-chatbot, translate-urdu, personalize)

2. Ensure your `.env` file contains the correct production values:
   ```
   GEMINI_API_KEY=your_production_gemini_api_key
   QDRANT_URL=your_production_qdrant_url
   QDRANT_API_KEY=your_production_qdrant_api_key
   JWT_SECRET=your_secure_production_jwt_secret
   ENVIRONMENT=production
   ```

### Step 2: Deploy to Railway

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository that contains the backend
4. Choose the `backend` directory for the deployment
5. Add environment variables in the "Variables" section:
   - `GEMINI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `JWT_SECRET`
   - `ENVIRONMENT` (set to "production")
6. Click "Deploy"

### Step 3: Get Your Backend URL

After successful deployment, you'll receive a URL in the format:
`https://your-project-name-production.up.railway.app`

Keep this URL handy as you'll need it for the frontend configuration.

---

## Frontend Deployment (Netlify/Vercel)

### Step 1: Add Environment Variable in Vercel

Set `NEXT_PUBLIC_API_URL` to your Railway backend URL

### Step 2: Deploy Frontend to Netlify or Vercel

#### Option A: Deploy to Netlify

1. Go to [Netlify](https://netlify.com)
2. Click "New site from Git"
3. Select your repository
4. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
5. Add environment variables if needed
6. Click "Deploy site"

#### Option B: Deploy to Vercel

1. Go to [Vercel](https://vercel.com)
2. Click "New Project" → "Import Git Repository"
3. Select your frontend repository
4. Configure build settings:
   - Framework Preset: Docusaurus
   - Build Command: `npm run build`
   - Output Directory: `build`
5. Click "Deploy"

### Step 3: Connect Frontend to Backend

Once both deployments are complete:
- Your frontend will be available at your Netlify/Vercel URL
- Your backend will be available at your Railway URL
- The frontend will automatically connect to the backend using the configured URL

---

## Testing the Deployment

1. Visit your frontend URL
2. Test all features:
   - Authentication (signup/login)
   - RAG Chatbot
   - Urdu Translation
   - Personalization
3. Check browser console for any API connection errors
4. Verify that all API calls are going to your deployed backend

---

## Troubleshooting

### Common Issues:

1. **CORS errors**: Ensure your backend allows requests from your frontend domain
2. **API key errors**: Double-check that all environment variables are correctly set
3. **Connection timeouts**: Verify that your Qdrant instance is accessible from Railway
4. **Frontend not connecting**: Check that the API_BASE_URL is correctly set in the frontend

### API Endpoints Reference:

After deployment, your backend will have these endpoints available:
- Authentication: `https://your-railway-url/auth/`
- RAG: `https://your-railway-url/rag/`
- Translation: `https://your-railway-url/translate/`
- Personalization: `https://your-railway-url/personalize/`

---

## Security Notes

- Never commit your actual API keys to the repository
- Use environment variables for all sensitive information
- Ensure your JWT secret is strong and unique
- Consider using HTTPS for all connections in production