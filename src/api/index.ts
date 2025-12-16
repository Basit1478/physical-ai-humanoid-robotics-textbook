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
  // Query documents from the RAG system (new format)
  queryDocuments: async (query: string) => {
    const response = await apiCall('/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        question: query,
        context: null
      }),
    });

    // If response follows new format (success/data/message), return the data part
    if (response.success !== undefined && response.data) {
      return response.data;
    }
    // Otherwise return the raw response for legacy compatibility
    return response;
  },

  // Chat with the RAG system (uses legacy format for frontend compatibility)
  chat: async (query: string) => {
    // Use the legacy endpoint that matches the frontend format
    return apiCall('/rag/chat', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        top_k: 5,
        user_id: 'anonymous'
      }),
    });
  },
};

// Translation API functions
export const translateApi = {
  // Translate chapter content
  translateChapter: async (content: string, chapterId: string) => {
    const response = await apiCall('/translate/chapter', {
      method: 'POST',
      body: JSON.stringify({
        content: content,
        chapter_id: chapterId,
        user_id: 'anonymous', // In a real app, this would be the actual user ID
        target_language: 'ur'
      }),
    });

    // If response follows new format (success/data/message), return the data part
    if (response.success !== undefined && response.data) {
      return response.data;
    }
    // Otherwise return the raw response for legacy compatibility
    return response;
  },
};

// Personalization API functions
export const personalizeApi = {
  // Personalize chapter content
  personalizeChapter: async (content: string, chapterId: string, userBackground: any) => {
    const response = await apiCall('/personalize/chapter', {
      method: 'POST',
      body: JSON.stringify({
        original_content: content,
        chapter_id: chapterId,
        user_id: 'anonymous', // In a real app, this would be the actual user ID
        user_background: userBackground || {}
      }),
    });

    // If response follows new format (success/data/message), return the data part
    if (response.success !== undefined && response.data) {
      return response.data;
    }
    // Otherwise return the raw response for legacy compatibility
    return response;
  },
};

// Authentication API functions
export const authApi = {
  // Signup
  signup: async (email: string, password: string, fullName: string, softwareBackground: string, hardwareBackground: string) => {
    const response = await apiCall('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
        software_background: softwareBackground,
        hardware_background: hardwareBackground
      }),
    });

    // If response follows new format (success/data/message), return the data part
    if (response.success !== undefined && response.data) {
      return response.data;
    }
    // Otherwise return the raw response for legacy compatibility
    return response;
  },

  // Login
  login: async (email: string, password: string) => {
    const response = await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // If response follows new format (success/data/message), return the data part
    if (response.success !== undefined && response.data) {
      return response.data;
    }
    // Otherwise return the raw response for legacy compatibility
    return response;
  },
};