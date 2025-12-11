---
sidebar_position: 5
title: Integration Guide
---

# Integration Guide

This guide explains how to connect the frontend components to the backend services.

## Overview

The Docusaurus website includes three main interactive components:
1. **Urdu Translation Button** - Translates selected text to Urdu
2. **Personalization Button** - Manages user profiles and preferences
3. **RAG Chatbot** - AI assistant powered by Retrieval Augmented Generation

## Backend Connection

### Environment Setup

To connect these components to your backend services, you'll need to:

1. Update the API endpoints in each component
2. Configure authentication tokens
3. Set up proper error handling

### Urdu Translation Integration

In `src/components/CustomFeatures/UrduButton.tsx`, replace the simulation code with actual API calls:

```typescript
// Replace the simulation with actual API call
const response = await fetch('/api/urdu-button/translate-selected', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({ text: selectedText })
});
```

### Personalization Integration

In `src/components/CustomFeatures/PersonalizationButton.tsx`, connect to the personalization endpoints:

```typescript
// Replace simulation with actual API calls
const response = await fetch('/api/personalization-button/update-profile', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify(profile)
});
```

### RAG Chatbot Integration

In `src/components/CustomFeatures/RagChatbot.tsx`, connect to the chat endpoints:

```typescript
// Replace simulation with actual API calls
const response = await fetch('/api/openai-agents/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: JSON.stringify({
    query: inputValue,
    module_id: currentModuleId,
    chapter_id: currentChapterId
  })
});
```

## Authentication

The components expect a JWT token stored in `localStorage` under the key `token`. Make sure your authentication system follows this pattern.

## Deployment

1. Build the Docusaurus site:
   ```bash
   npm run build
   ```

2. Serve the built files with your backend server
3. Ensure CORS is properly configured for API endpoints

## Troubleshooting

Common issues:
- **CORS errors**: Configure your backend to allow requests from your frontend domain
- **Authentication failures**: Verify token storage and expiration handling
- **API connectivity**: Check network requests in browser developer tools

## Next Steps

1. Implement actual API calls in each component
2. Add proper loading states and error handling
3. Test with your backend services
4. Deploy and monitor usage