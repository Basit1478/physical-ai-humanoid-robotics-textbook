import qdrant_client
from qdrant_client.http import models
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class QdrantService:
    def __init__(self):
        # Initialize Qdrant client
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = "book_content"

        # Only initialize client if credentials are available
        if self.url and self.api_key and not self.url.startswith("YOUR_") and not self.api_key.startswith("YOUR_"):
            try:
                self.client = qdrant_client.QdrantClient(
                    url=self.url,
                    api_key=self.api_key
                )
                # Initialize the collection if it doesn't exist
                self._init_collection()
            except Exception as e:
                logging.warning(f"Could not initialize Qdrant client: {e}")
                self.client = None
        else:
            logging.warning("QDRANT_URL or QDRANT_API_KEY not properly set, Qdrant client disabled")
            self.client = None

    def _init_collection(self):
        """Initialize the Qdrant collection with proper configuration"""
        if not self.client:
            return

        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=768,  # Size of Gemini embeddings
                    distance=models.Distance.COSINE
                )
            )

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using a placeholder - in real implementation, use Gemini"""
        # In a real implementation, we would call the Gemini API to generate embeddings
        # For now, we'll return a mock embedding (in practice, use google-generativeai)
        # This is just a placeholder for the actual implementation
        import numpy as np
        # Mock embedding - in real implementation, use Gemini API
        return [float(x) for x in np.random.random(768)]

    def store_content(self, content_id: str, text: str, metadata: Dict[str, Any]):
        """Store content in Qdrant with embeddings"""
        if not self.client:
            logging.warning("Qdrant client not initialized, skipping content storage")
            return

        vector = self.embed_text(text)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=content_id,
                    vector=vector,
                    payload={
                        "content": text,
                        "metadata": metadata
                    }
                )
            ]
        )

    def search_content(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in Qdrant using the provided query vector"""
        if not self.client:
            logging.warning("Qdrant client not initialized, returning empty results")
            return []

        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "content": result.payload["content"],
                "metadata": result.payload["metadata"],
                "score": result.score
            })

        return results

    def add_point(self, content_id: str, vector: List[float], text: str, metadata: Dict[str, Any]):
        """Add a single point to the collection"""
        if not self.client:
            logging.warning("Qdrant client not initialized, skipping point addition")
            return

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=content_id,
                    vector=vector,
                    payload={
                        "content": text,
                        "metadata": metadata
                    }
                )
            ]
        )

# Global instance
qdrant_service = QdrantService()