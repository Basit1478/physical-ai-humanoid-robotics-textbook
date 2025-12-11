import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import httpx
import json

load_dotenv()

class GeminiService:
    """
    Gemini service using OpenAI-compatible API format
    This uses the Gemini API through OpenAI SDK compatibility layer
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = "gemini-pro"

        if not self.api_key or self.api_key.startswith("YOUR_"):
            logging.warning("GEMINI_API_KEY not properly set, Gemini client disabled")
            self.api_key = None

    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini via REST API"""
        if not self.api_key:
            logging.warning("Gemini model not initialized, returning mock response")
            return "Gemini API not available. This is a mock response for testing."

        try:
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            headers = {
                "Content-Type": "application/json",
            }
            params = {
                "key": self.api_key
            }
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                }
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, params=params, json=payload)
                response.raise_for_status()
                result = response.json()

                if "candidates" in result and len(result["candidates"]) > 0:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logging.error(f"Unexpected Gemini response format: {result}")
                    return "Sorry, I'm having trouble generating a response right now."

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error calling Gemini API: {e.response.status_code} - {e.response.text}")
            return "Sorry, I'm having trouble generating a response right now."
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            return "Sorry, I'm having trouble generating a response right now."

    def embed_content(self, text: str) -> List[float]:
        """Generate embeddings for text using Gemini Embedding API"""
        if not self.api_key:
            logging.warning("Gemini embedding model not initialized, returning mock embedding")
            import random
            return [random.random() for _ in range(768)]

        try:
            url = f"{self.base_url}/models/text-embedding-004:embedContent"
            headers = {
                "Content-Type": "application/json",
            }
            params = {
                "key": self.api_key
            }
            payload = {
                "model": "models/text-embedding-004",
                "content": {
                    "parts": [{"text": text}]
                }
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, params=params, json=payload)
                response.raise_for_status()
                result = response.json()

                if "embedding" in result and "values" in result["embedding"]:
                    return result["embedding"]["values"]
                else:
                    logging.error(f"Unexpected embedding response format: {result}")
                    import random
                    return [random.random() for _ in range(768)]

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error generating embeddings: {e.response.status_code} - {e.response.text}")
            import random
            return [random.random() for _ in range(768)]
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            import random
            return [random.random() for _ in range(768)]

# Global instance
gemini_service = GeminiService()