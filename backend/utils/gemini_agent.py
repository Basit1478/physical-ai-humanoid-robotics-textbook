from typing import Dict, List, Any
import requests
import json
import time
import os

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBGyEFjjE4QJO2rCRvFiDZrnHnvkdhknhY")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

class OpenAI_Agents_Gemini:
    def __init__(self):
        """
        Initialize OpenAI Agents SDK with Gemini API configuration
        """
        self.api_key = GEMINI_API_KEY
        self.base_url = GEMINI_API_BASE
        self.default_model = "gemini-pro"

    def chat_completion(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        """
        Simulate OpenAI chat completion API using Gemini
        """
        if model is None:
            model = self.default_model

        # Convert OpenAI message format to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Add system message as a user message (Gemini doesn't have system role)
                gemini_messages.append({"role": "user", "parts": [{"text": f"System: {msg['content']}"}]})
            else:
                gemini_messages.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

        # Prepare Gemini API request
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"

        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
                "topP": 0.8,
                "topK": 40
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            gemini_response = response.json()

            # Convert Gemini response to OpenAI format
            if "candidates" in gemini_response and len(gemini_response["candidates"]) > 0:
                content = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "id": "chatcmpl-" + gemini_response.get("id", "gemini"),
                    "object": "chat.completion",
                    "created": int(time.time()) if 'time' in globals() else 0,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
            else:
                return {"error": "No candidates in response"}

        except Exception as e:
            return {"error": str(e)}