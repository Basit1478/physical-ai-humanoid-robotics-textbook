"""
Gemini client for the RAG Agent service
"""
import google.generativeai as genai
from typing import List, Dict, Optional
import logging
from config.settings import settings


class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            # During validation or if API key is not set, we'll initialize with a mock client
            # In production, this should be handled by validate_required_settings()
            self.model = None
            self.model_name = settings.GEMINI_MODEL
            self.logger = logging.getLogger(__name__)
            return

        # Configure the Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Initialize the model
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

        self.logger = logging.getLogger(__name__)

    def generate_content(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate content using Gemini model with optional context.
        """
        if not self.model:
            # Mock response for validation
            return f"Mock response for: {prompt[:50]}... [API key not configured]"

        try:
            # Combine context with prompt if provided
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\n\nInstructions: Answer based ONLY on the provided context. Do not use any external knowledge."
            else:
                full_prompt = prompt

            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": settings.TEMPERATURE,
                    "max_output_tokens": settings.MAX_TOKENS,
                }
            )

            if response.text:
                return response.text
            else:
                self.logger.warning("Gemini returned empty response")
                return "I couldn't generate a response for your query."

        except Exception as e:
            self.logger.error(f"Error generating content with Gemini: {str(e)}")
            raise e

    def generate_content_with_retrieved_context(self, query: str, retrieved_chunks: List[Dict]) -> str:
        """
        Generate content using Gemini model with retrieved context from Qdrant.
        """
        if not self.model:
            # Mock response for validation
            return f"Mock response for query: {query[:50]}... with {len(retrieved_chunks)} chunks [API key not configured]"

        try:
            # Format the retrieved context
            context = self._format_retrieved_context(retrieved_chunks)

            # Generate response using the context
            response = self.generate_content(query, context)

            return response

        except Exception as e:
            self.logger.error(f"Error generating content with retrieved context: {str(e)}")
            raise e

    def _format_retrieved_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into a context string for the model.
        """
        if not retrieved_chunks:
            return "No relevant context found in the knowledge base."

        formatted_chunks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get('text', '')[:500]  # Limit text length for context
            source = chunk.get('url', 'Unknown source')
            formatted_chunks.append(f"Source {i} ({source}):\n{text}\n")

        return "\n".join(formatted_chunks)

    def validate_response_against_context(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context.
        This is a basic implementation - in production, you'd want more sophisticated validation.
        """
        if not self.model:
            # For validation purposes, return True
            return True

        # Simple validation: check if response contains information from context
        # In a real implementation, you'd use more advanced techniques
        response_lower = response.lower()
        context_lower = context.lower()

        # Check if response contains key phrases from context
        context_sentences = context_lower.split('.')
        response_sentences = response_lower.split('.')

        # Count overlapping sentences (very basic validation)
        overlap_count = 0
        for resp_sent in response_sentences:
            for ctx_sent in context_sentences:
                if len(resp_sent.strip()) > 10 and resp_sent.strip() in ctx_sent:
                    overlap_count += 1

        # If at least some sentences overlap, consider it validated
        return overlap_count > 0