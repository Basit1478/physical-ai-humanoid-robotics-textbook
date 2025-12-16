# Quickstart: Docusaurus-Backend Integration

## Overview
Quick setup guide to integrate the RAG backend with Docusaurus frontend and create a complete chatbot experience.

## Prerequisites

### System Requirements
- Node.js 16+ and npm/yarn
- Python 3.9+ with the FastAPI backend running
- Git for version control

### External Services
- FastAPI backend from Spec 3 running and accessible
- RAG agent service from Spec 3 properly configured
- Docusaurus documentation site set up

## Setup Instructions

### 1. Prepare Backend Services
```bash
# Ensure your FastAPI backend from Spec 3 is running
cd backend/rag-agent
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Verify the backend is accessible
curl http://localhost:8000/health
```

### 2. Set Up Docusaurus Environment
```bash
# Navigate to your Docusaurus project
cd your-docusaurus-project

# Install required dependencies
npm install
```

### 3. Install Chatbot Component Dependencies
```bash
# Install React and related dependencies
npm install react react-dom axios
```

## Integrating the Chatbot Component

### 1. Create Chatbot Component Structure
Create the following directory structure in your Docusaurus project:
```
src/
└── components/
    └── Chatbot/
        ├── Chatbot.jsx
        ├── Chatbot.css
        ├── TextSelection.js
        └── api.js
```

### 2. Basic Configuration
Add the backend URL to your Docusaurus configuration in `docusaurus.config.js`:

```javascript
module.exports = {
  // ... other config
  themeConfig: {
    // ... other theme config
    chatbot: {
      backendUrl: 'http://localhost:8000', // Update to your backend URL
      enabled: true,
      position: 'bottom-right', // Options: 'bottom-right', 'sidebar', 'inline'
      enableSelectedText: true
    }
  }
};
```

### 3. Environment Configuration
Create or update your `.env` file with the backend configuration:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=15000
```

## Running the Integrated System

### 1. Start Backend Service
```bash
# Start your FastAPI backend (from Spec 3)
cd backend/rag-agent
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 2. Start Docusaurus Frontend
```bash
# In your Docusaurus project directory
npm start
```

### 3. Configuration Options
The chatbot can be configured through the docusaurus.config.js file:

| Option | Description | Default |
|--------|-------------|---------|
| `backendUrl` | URL of the FastAPI backend | http://localhost:8000 |
| `enabled` | Whether chatbot is enabled | true |
| `position` | Position of chat interface | bottom-right |
| `enableSelectedText` | Enable selected text functionality | true |
| `apiTimeout` | Request timeout in milliseconds | 15000 |

## Using the Integrated Chatbot

### 1. Basic Chat Interaction
1. Navigate to any documentation page
2. Click on the chatbot icon (usually in bottom-right corner)
3. Type your question in the input field
4. Press Enter or click Send to submit

### 2. Selected Text Queries
1. Select text on any documentation page
2. The chatbot will detect the selection
3. Ask a question related to the selected text
4. The selected text will be included as context

### 3. Chat Features
- **Message History**: Previous messages are preserved in the session
- **Loading Indicators**: Shows when waiting for backend response
- **Error Handling**: Displays meaningful error messages
- **Session Management**: Maintains conversation context

## Component Integration

### 1. Adding to Layout
To add the chatbot globally to all pages, modify your layout component:

```jsx
// In your layout component
import Chatbot from '@site/src/components/Chatbot/Chatbot';

function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <Chatbot />
    </>
  );
}
```

### 2. Adding to Specific Pages
To add the chatbot to specific pages only:

```jsx
// In your MDX file
import Chatbot from '@site/src/components/Chatbot/Chatbot';

<Chatbot position="inline" />
```

### 3. API Communication
The chatbot communicates with the backend using the following endpoints:

#### Question Answering
- **Endpoint**: `POST /api/v1/ask`
- **Description**: Sends questions to the RAG agent

**Request Body**:
```json
{
  "query_text": "What is inverse kinematics?",
  "selected_text": "optional selected text",
  "context": "additional context"
}
```

**Response**:
```json
{
  "response_id": "uuid",
  "answer_text": "The agent's response...",
  "source_chunks": ["chunk_id_1", "chunk_id_2"],
  "confidence_score": 0.85,
  "citations": [...]
}
```

#### Health Check
- **Endpoint**: `GET /health`
- **Description**: Checks backend service health

## Verification

### 1. Check Backend Connection
Verify the backend is responding:
```bash
curl http://localhost:8000/health
```

### 2. Test Chat Functionality
1. Open your Docusaurus site in a browser
2. Look for the chatbot icon/interface
3. Try sending a simple message
4. Verify the response appears in the UI

### 3. Test Selected Text Feature
1. Select text on a documentation page
2. Initiate a chat or add to existing chat
3. Verify the selected text is included in the query context
4. Check that the response relates to the selected text

## Troubleshooting

### Common Issues

#### Backend Connection Errors
- **Issue**: Cannot connect to backend API
- **Solution**: Verify backend URL in configuration and ensure backend service is running

#### CORS Errors
- **Issue**: Cross-origin requests blocked
- **Solution**: Configure CORS in FastAPI backend to allow Docusaurus origin

#### Text Selection Not Working
- **Issue**: Selected text not captured
- **Solution**: Check browser compatibility and text selection permissions

#### Component Not Loading
- **Issue**: Chatbot component doesn't appear
- **Solution**: Verify component path and Docusaurus plugin configuration

### Debugging Commands
```bash
# Check backend health
curl http://localhost:8000/health

# Test chat endpoint directly
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query_text": "test query"}'
```

## Next Steps

1. **Customize Appearance**: Adjust styling to match your documentation theme
2. **Configure Options**: Set up different positioning and feature options
3. **Test Across Pages**: Verify functionality on different types of documentation pages
4. **User Testing**: Get feedback from users on the chatbot experience
5. **Performance Optimization**: Monitor and optimize for performance

## Support

For issues with the frontend-backend integration:
- Check that both frontend and backend services are running
- Verify network connectivity between services
- Review browser console for client-side errors
- Check backend logs for server-side errors
- Consult the troubleshooting section