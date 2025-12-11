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
  // Query documents from the RAG system
  queryDocuments: async (query: string) => {
    return apiCall('/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        question: query,
        user_id: 'anonymous' // In a real app, this would be the actual user ID
      }),
    });
  },

  // Chat with the RAG system
  chat: async (query: string) => {
    return apiCall('/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        question: query,
        user_id: 'anonymous' // In a real app, this would be the actual user ID
      }),
    });
  },
};

// Translation API functions
export const translateApi = {
  // Translate chapter content
  translateChapter: async (content: string, chapterId: string) => {
    return apiCall('/translate/chapter', {
      method: 'POST',
      body: JSON.stringify({
        content: content,
        chapter_id: chapterId,
        user_id: 'anonymous', // In a real app, this would be the actual user ID
        target_language: 'ur'
      }),
    });
  },
};

// Personalization API functions
export const personalizeApi = {
  // Personalize chapter content
  personalizeChapter: async (content: string, chapterId: string, userBackground: any) => {
    return apiCall('/personalize/chapter', {
      method: 'POST',
      body: JSON.stringify({
        original_content: content,
        chapter_id: chapterId,
        user_id: 'anonymous', // In a real app, this would be the actual user ID
        user_background: userBackground || {}
      }),
    });
  },
};

// Authentication API functions
export const authApi = {
  // Signup
  signup: async (email: string, password: string, fullName: string, softwareBackground: string, hardwareBackground: string) => {
    return apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
        software_background: softwareBackground,
        hardware_background: hardwareBackground
      }),
    });
  },

  // Login
  login: async (email: string, password: string) => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
};