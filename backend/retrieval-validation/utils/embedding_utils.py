"""
Embedding utilities for the retrieval validation service
"""
import cohere
import numpy as np
from typing import List, Union
from config.settings import COHERE_API_KEY, COHERE_MODEL


class EmbeddingService:
    def __init__(self):
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(COHERE_API_KEY)
        self.model = COHERE_MODEL

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query using Cohere API with 768 dimensions.
        """
        if not query:
            return []

        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query",  # Appropriate for search queries
                embedding_types=["float"],  # Request specific embedding type for v3 models
                dimensions=768  # Specify 768 dimensions for compatibility
            )
            # Extract the embedding - for v3 models with embedding_types, the result is nested
            return response.embeddings.float[0] if response.embeddings.float else []
        except Exception as e:
            raise Exception(f"Error embedding query: {str(e)}")

    def embed_queries(self, queries: List[str]) -> List[List[float]]:
        """
        Embed multiple queries using Cohere API with 768 dimensions.
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
                    input_type="search_query",
                    embedding_types=["float"],  # Request specific embedding type for v3 models
                    dimensions=768  # Specify 768 dimensions for compatibility
                )
                # Extract embeddings for v3 models
                embeddings = response.embeddings.float
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
            'dimensions': 768
        }