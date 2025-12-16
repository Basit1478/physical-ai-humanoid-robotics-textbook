"""
Embedding service using Cohere API
"""
import cohere
import asyncio
import logging
from typing import List, Dict, Optional
from config.settings import COHERE_API_KEY, COHERE_MODEL, RETRY_ATTEMPTS, RETRY_DELAY


class EmbeddingService:
    def __init__(self):
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(COHERE_API_KEY)
        self.model = COHERE_MODEL
        self.logger = logging.getLogger(__name__)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        # Cohere has a limit on the number of texts per request
        # According to Cohere docs, batch size should be reasonable
        batch_size = 96  # Conservative batch size to avoid rate limits

        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            for attempt in range(RETRY_ATTEMPTS):
                try:
                    response = self.client.embed(
                        texts=batch,
                        model=self.model,
                        input_type="search_document"  # Appropriate for document search
                    )

                    embeddings = response.embeddings
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

    def get_model_info(self) -> Dict:
        """
        Get information about the embedding model being used.
        """
        return {
            'model': self.model,
            'api_provider': 'cohere',
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
            # Default to common Cohere embedding size
            return 1024  # Cohere's multilingual model typically returns 1024 dimensions