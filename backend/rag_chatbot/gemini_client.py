import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging

load_dotenv()

class GeminiService:
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and not api_key.startswith("YOUR_"):
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.embedding_model = "models/embedding-001"
            except Exception as e:
                logging.warning(f"Could not initialize Gemini client: {e}")
                self.model = None
        else:
            logging.warning("GEMINI_API_KEY not properly set, Gemini client disabled")
            self.model = None

    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        if not self.model:
            logging.warning("Gemini model not initialized, returning mock response")
            return "Gemini API not available. This is a mock response for testing."

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return "Sorry, I'm having trouble generating a response right now."

    def embed_content(self, text: str) -> List[float]:
        """Generate embeddings for text using Gemini"""
        if not hasattr(self, 'embedding_model') or not os.getenv("GEMINI_API_KEY"):
            logging.warning("Gemini embedding model not initialized, returning mock embedding")
            # Return a mock embedding in case of error
            import numpy as np
            return [float(x) for x in np.random.random(768)]

        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            # Return a mock embedding in case of error
            import numpy as np
            return [float(x) for x in np.random.random(768)]

# Global instance
gemini_service = GeminiService()