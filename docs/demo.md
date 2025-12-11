# 🚀 Interactive Features Demo

This page demonstrates all the AI-powered interactive features of the Physical AI & Humanoid Robotics textbook platform.

## 📋 Available Features

Our platform includes three main AI-powered features to enhance your learning experience:

1. **AI Assistant (RAG Chatbot)** - Ask questions about textbook content
2. **Urdu Translation** - Translate any text to Urdu language
3. **Personalization** - Customize content based on your background

---

## 🤖 AI Assistant (RAG Chatbot)

The AI Assistant uses **RAG (Retrieval Augmented Generation)** technology to answer your questions about the textbook content. It combines:
- **Qdrant Vector Database** for semantic search
- **Gemini AI** for intelligent responses
- **Context-aware** answers based on textbook content

### Try It Out:
- Type questions like:
  - "What is a humanoid robot?"
  - "Explain physical AI concepts"
  - "How do robot sensors work?"

---

## 🌐 Urdu Translation

Translate any text on the page to Urdu with AI-powered accuracy.

### How to Use:
1. Select any text on this page
2. Click the "Translate to Urdu" button
3. View the translation in Urdu script

### Sample Text to Translate:
> **Humanoid robots** are autonomous robots that resemble the human body in shape. They are designed to replicate human movements and interactions, making them ideal for applications in healthcare, education, and service industries.

> **Physical AI** refers to artificial intelligence systems that interact with the physical world through sensors and actuators. These systems combine perception, reasoning, and action to operate in real-world environments.

---

## 🎯 Personalization

Customize your learning experience based on your:
- Education level (Beginner/Intermediate/Advanced)
- Field of study (Robotics, CS, EE, ME, etc.)
- Background and experience

### Benefits:
- **Beginner**: More detailed explanations and step-by-step guides
- **Intermediate**: Balanced content with practical examples
- **Advanced**: Technical details and cutting-edge research references

---

## 🔗 Backend API Connection

All features are powered by our FastAPI backend deployed on Render:
- **Backend URL**: https://textbook-backend-api.onrender.com
- **API Documentation**: https://textbook-backend-api.onrender.com/docs

### API Endpoints:
- `/auth/signup` - User registration
- `/auth/login` - User authentication
- `/rag/query` - RAG chatbot queries
- `/translate/chapter` - Urdu translation
- `/personalize/chapter` - Content personalization

---

## 📊 Technology Stack

### Frontend
- **Docusaurus** - Documentation framework
- **React** - UI components
- **TypeScript** - Type-safe code

### Backend
- **FastAPI** - Python web framework
- **Gemini AI** - Google's AI model
- **Qdrant** - Vector database for RAG
- **Better-Auth** - Authentication system

### Deployment
- **Frontend**: Render Static Site
- **Backend**: Render Web Service (Python)
- **Vector DB**: Qdrant Cloud

---

## ⚠️ Important Notes

### First-Time Usage
If you're using the features for the first time:
1. The backend may take **30-60 seconds** to wake up (Render free tier)
2. Look for the **backend status indicator** in the AI Assistant
3. ✅ **Connected** = Ready to use
4. ⚠️ **Disconnected** = Wait a moment and try again

### API Key Requirements
Some features require valid API keys:
- ✅ **Authentication** - Working without API keys
- ⚠️ **RAG Chatbot** - Requires Gemini API key
- ⚠️ **Translation** - Requires Gemini API key
- ⚠️ **Personalization** - Requires Gemini API key

If you see "trouble generating a response", the API keys may need to be updated in the backend.

---

## 🧪 Testing Instructions

### Test the RAG Chatbot
1. Scroll down to the "Interactive Learning Features" section
2. Find the "AI Assistant (RAG Chatbot)" panel
3. Wait for the backend status to show "✅ Connected"
4. Type a question and click "Send"
5. Observe the AI response

### Test Urdu Translation
1. Find the "Urdu Translation" panel
2. Select some text from the "Sample Text" section above
3. Click "Translate to Urdu"
4. View the translated text in Urdu script (right-to-left)

### Test Personalization
1. Find the "Personalization" panel
2. Click "Create Profile" or "Update Profile"
3. Select your education level and field of study
4. Save your profile
5. Your preferences are stored and used for content customization

---

## 🔄 Live Updates

This page demonstrates real-time integration with the deployed backend. All features are live and functional!

**Backend Status**: Check the AI Assistant panel for current connection status.

---

## 📝 Feedback

Having issues or suggestions?
- Check the [Integration Guide](/docs/integration-guide) for setup details
- Review the [Deployment Status](https://github.com/Basit1478/physical-ai-humanoid-robotics-textbook/blob/main/DEPLOYMENT_STATUS.md)
- Report issues on [GitHub](https://github.com/Basit1478/physical-ai-humanoid-robotics-textbook/issues)

---

**Ready to try? Scroll down to see the Interactive Learning Features section!**
