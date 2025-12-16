import { ChatMessage } from './Chatbot';

export interface ChatRequest {
  query_text: string;
  selected_text?: string | null;
  context?: string;
}

export interface ChatResponse {
  answer: string;
  source_chunks: string[];
  confidence_score: number;
  citations: Array<{
    url: string;
    title: string;
    position: number;
    score: number;
  }>;
  query_time: number;
  selected_text_used?: boolean;
}

export interface ErrorResponse {
  error: string;
}

class ChatbotAPIService {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to localhost
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Set up the request with proper headers for CORS
      const response = await fetch(`${this.baseUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add any required headers for your backend
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async retrieveChunks(query: string, topK?: number): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/retrieve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: query,
          top_k: topK || 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error retrieving chunks:', error);
      throw error;
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);

      return response.ok;
    } catch (error) {
      console.error('Error checking health:', error);
      return false;
    }
  }
}

export default new ChatbotAPIService();