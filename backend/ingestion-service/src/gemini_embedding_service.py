"""
Embedding service using Google's Gemini API for text embeddings
"""
import google.generativeai as genai
import logging
from typing import List
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, RETRY_ATTEMPTS, RETRY_DELAY


class GeminiEmbeddingService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)

        # Use the Google embedding model
        self.model_name = "models/embedding-001"
        self.logger = logging.getLogger(__name__)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Google's embedding API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        all_embeddings = []

        # Process texts in smaller batches to avoid rate limits
        batch_size = 10  # Google's embedding API typically has smaller batch limits

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            for attempt in range(RETRY_ATTEMPTS):
                try:
                    # Use Google's dedicated embedding API
                    result = genai.embed_content(
                        model=self.model_name,
                        content=batch,
                        task_type="retrieval_document"
                    )

                    embeddings = result['embedding']
                    all_embeddings.extend(embeddings)
                    self.logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                    break  # Success, break retry loop

                except Exception as e:
                    self.logger.error(f"Error generating embeddings for batch {i//batch_size + 1} (attempt {attempt + 1}): {str(e)}")

                    if attempt == RETRY_ATTEMPTS - 1:
                        # Final attempt failed, raise the error
                        raise e
                    else:
                        # Wait before retrying
                        import time
                        time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff

        return all_embeddings

    def generate_embedding_for_single_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Single text string to embed

        Returns:
            Embedding vector (list of floats)
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def get_model_info(self) -> dict:
        """
        Get information about the embedding model being used.
        """
        return {
            'model': self.model_name,
            'api_provider': 'google',
            'dimensions': self._get_embedding_dimensions()
        }

    def _get_embedding_dimensions(self) -> int:
        """
        Get the dimensions of the embedding model by testing with a sample text.
        """
        try:
            sample_embedding = self.generate_embedding_for_single_text("sample text")
            return len(sample_embedding) if sample_embedding else 0
        except Exception as e:
            self.logger.error(f"Error getting embedding dimensions: {str(e)}")
            # Google's embedding-001 typically returns 768 dimensions
            return 768