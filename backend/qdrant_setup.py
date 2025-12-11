from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
import uuid
from pydantic import BaseModel

class QdrantSetup:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collections = {
            "users": "user_backgrounds",
            "documents": "textbook_documents",
            "embeddings": "text_embeddings"
        }
        self._initialize_collections()

    def _initialize_collections(self):
        # Create collections if they don't exist
        existing_collections = [col.name for col in self.client.get_collections().collections]

        # User backgrounds collection
        if self.collections["users"] not in existing_collections:
            self.client.create_collection(
                collection_name=self.collections["users"],
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

        # Documents collection
        if self.collections["documents"] not in existing_collections:
            self.client.create_collection(
                collection_name=self.collections["documents"],
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

        # Embeddings collection
        if self.collections["embeddings"] not in existing_collections:
            self.client.create_collection(
                collection_name=self.collections["embeddings"],
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    def store_user_background(self, user_id: str, software_background: str, hardware_background: str):
        """Store user background information in Qdrant"""
        self.client.upsert(
            collection_name=self.collections["users"],
            points=[
                models.PointStruct(
                    id=uuid.uuid4().int,
                    vector=[0.0] * 384,  # Placeholder vector
                    payload={
                        "user_id": user_id,
                        "software_background": software_background,
                        "hardware_background": hardware_background,
                        "created_at": str(__import__('datetime').datetime.now())
                    }
                )
            ]
        )

    def get_user_background(self, user_id: str):
        """Retrieve user background information from Qdrant"""
        results = self.client.scroll(
            collection_name=self.collections["users"],
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=1
        )

        if results[0]:
            return results[0][0].payload
        return None

    def store_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Store document in Qdrant"""
        self.client.upsert(
            collection_name=self.collections["documents"],
            points=[
                models.PointStruct(
                    id=uuid.uuid4().int,
                    vector=[0.0] * 384,  # Placeholder vector
                    payload={
                        "doc_id": doc_id,
                        "content": content,
                        "metadata": metadata
                    }
                )
            ]
        )

    def search_documents(self, query_vector: List[float], top_k: int = 5):
        """Search documents in Qdrant"""
        results = self.client.search(
            collection_name=self.collections["documents"],
            query_vector=query_vector,
            limit=top_k
        )
        return [hit.payload for hit in results]