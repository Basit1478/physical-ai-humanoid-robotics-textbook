# Frontend Setup Instructions

## API Integration

The Docusaurus frontend is already configured to connect to the backend API. The connection is handled through:

- `src/api/config.ts` - Contains the base URL configuration that dynamically detects the environment
- `src/api/index.ts` - Contains all API utility functions for the four backend services:
  - `ragApi` - RAG system (chat, query, documents)
  - `translateApi` - Translation services (English to Urdu)
  - `personalizeApi` - Content personalization
  - `authApi` - Authentication (signup, login)

## Configuration

The API configuration automatically detects the environment:

```typescript
// API Configuration
const API_BASE_URL = typeof window !== 'undefined'
  ? window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'  // For local development
    : 'https://your-deployed-backend-url.com'  // For production
  : 'http://localhost:8001';  // For server-side rendering
```

## Components Using Backend APIs

The following components in `src/components/CustomFeatures/` have been updated to use the backend APIs:

1. **RagChatbot.tsx** - Connects to `/rag/chat` endpoint for AI-powered textbook assistance
2. **UrduButton.tsx** - Connects to `/translate/translate` endpoint for Urdu translation
3. **PersonalizationButton.tsx** - Connects to `/personalize/preferences` and `/personalize/profile` endpoints for user profile management

## Running the Application

1. Ensure the backend server is running on port 8001
2. In the `my-website` directory, run:
```bash
npm install
npm run start
```
3. The frontend will start on `http://localhost:3000` and automatically connect to the backend at `http://localhost:8001`

## Testing the Connection

You can verify that the frontend is properly connected to the backend by:

1. Opening the developer tools in your browser (F12)
2. Navigating to the Network tab
3. Using any of the custom features (chatbot, translation, personalization)
4. Confirming that API requests are being made to `http://localhost:8001`