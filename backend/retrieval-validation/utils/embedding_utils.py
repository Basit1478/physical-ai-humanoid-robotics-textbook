"""
Embedding utilities for the retrieval validation service
"""
import cohere
import numpy as np
from typing import List, Union
from config.settings import COHERE_API_KEY, COHERE_MODEL, RETRIEVAL_TIMEOUT


class EmbeddingService:
    def __init__(self):
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(COHERE_API_KEY)
        self.model = COHERE_MODEL

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query using Cohere API.
        """
        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"  # Appropriate for search queries
            )
            return response.embeddings[0] if response.embeddings else []
        except Exception as e:
            raise Exception(f"Error embedding query: {str(e)}")

    def embed_queries(self, queries: List[str]) -> List[List[float]]:
        """
        Embed multiple queries using Cohere API.
        """
        if not queries:
            return []

        # Cohere has a limit on the number of texts per request
        batch_size = 96  # Conservative batch size to avoid rate limits
        all_embeddings = []

        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_query"
                )
                embeddings = response.embeddings
                all_embeddings.extend(embeddings)
            except Exception as e:
                raise Exception(f"Error embedding batch {i//batch_size + 1}: {str(e)}")

        return all_embeddings

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        similarity = dot_product / (norm_v1 * norm_v2)
        return float(similarity)

    def get_model_info(self) -> dict:
        """
        Get information about the embedding model being used.
        """
        return {
            'model': self.model,
            'api_provider': 'cohere',
            'input_type': 'search_query'
        }