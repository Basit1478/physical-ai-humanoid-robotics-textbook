import { API_BASE_URL } from './config';

// API utility functions
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

// RAG API functions
export const ragApi = {
  // Add a document to the RAG system
  addDocument: async (content: string) => {
    return apiCall('/rag/documents', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  },

  // Query documents from the RAG system
  queryDocuments: async (query: string, topK: number = 5) => {
    return apiCall('/rag/query', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  },

  // Chat with the RAG system
  chat: async (query: string, topK: number = 5) => {
    return apiCall('/rag/chat', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  },
};

// Translation API functions
export const translateApi = {
  // Translate text
  translate: async (text: string, sourceLang: string = 'en', targetLang: string = 'ur') => {
    return apiCall('/translate/translate', {
      method: 'POST',
      body: JSON.stringify({ text, source_lang: sourceLang, target_lang: targetLang }),
    });
  },

  // Translate to Urdu specifically
  translateToUrdu: async (text: string) => {
    return apiCall(`/translate/urdu?text=${encodeURIComponent(text)}`, {
      method: 'POST',
    });
  },
};

// Personalization API functions
export const personalizeApi = {
  // Set user preferences
  setPreferences: async (preferences: any) => {
    return apiCall('/personalize/preferences', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  },

  // Personalize content
  personalizeContent: async (content: string, userId: string) => {
    return apiCall('/personalize/content', {
      method: 'POST',
      body: JSON.stringify({ content, user_id: userId, content_type: 'text' }),
    });
  },

  // Get user profile
  getUserProfile: async (userId: string) => {
    return apiCall(`/personalize/profile/${userId}`, {
      method: 'GET',
    });
  },
};

// Authentication API functions
export const authApi = {
  // Signup
  signup: async (userData: any) => {
    return apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Login
  login: async (loginData: any) => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify(loginData),
    });
  },
};