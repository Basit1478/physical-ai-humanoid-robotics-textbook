"""
Qdrant storage service for vector storage
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import logging
import hashlib
from config.settings import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME


class QdrantStorage:
    def __init__(self):
        if not QDRANT_URL:
            raise ValueError("QDRANT_URL environment variable is required")

        # Initialize Qdrant client
        if QDRANT_API_KEY:
            self.client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
                prefer_grpc=False  # Using HTTP for better compatibility
            )
        else:
            self.client = QdrantClient(url=QDRANT_URL)

        self.collection_name = QDRANT_COLLECTION_NAME
        self.logger = logging.getLogger(__name__)

    def initialize_collection(self, vector_size: int = 1024):
        """
        Initialize the Qdrant collection if it doesn't exist.
        Creates a collection with the appropriate vector size and payload schema.
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create a new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )

                # Create payload index for efficient filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="url",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )

                self.logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                self.logger.info(f"Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            self.logger.error(f"Error initializing Qdrant collection: {str(e)}")
            raise e

    def upsert_vectors(self, vectors_data: List[Dict], batch_size: int = 64):
        """
        Upsert vectors with metadata to Qdrant collection.

        Args:
            vectors_data: List of dictionaries containing 'vector', 'payload', and 'id'
            batch_size: Number of vectors to upload in each batch
        """
        if not vectors_data:
            self.logger.info("No vectors to upload")
            return

        total_vectors = len(vectors_data)
        self.logger.info(f"Uploading {total_vectors} vectors to Qdrant in batches of {batch_size}")

        successful_uploads = 0
        failed_uploads = 0

        for i in range(0, total_vectors, batch_size):
            batch = vectors_data[i:i + batch_size]
            batch_points = []

            for item in batch:
                try:
                    point = models.PointStruct(
                        id=item['id'],
                        vector=item['vector'],
                        payload=item['payload']
                    )
                    batch_points.append(point)
                except Exception as e:
                    self.logger.error(f"Error creating PointStruct for ID {item.get('id', 'unknown')}: {str(e)}")
                    failed_uploads += 1

            if batch_points:
                try:
                    # Upsert the batch of points
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=batch_points
                    )
                    successful_uploads += len(batch_points)
                    self.logger.info(f"Uploaded batch {i//batch_size + 1}/{(total_vectors-1)//batch_size + 1}: {len(batch_points)} vectors")

                except Exception as e:
                    self.logger.error(f"Error uploading batch {i//batch_size + 1}: {str(e)}")
                    failed_uploads += len(batch_points)

        self.logger.info(f"Upload completed: {successful_uploads} successful, {failed_uploads} failed")

    def idempotent_upsert(self, vectors_data: List[Dict], batch_size: int = 64):
        """
        Perform idempotent upsert by checking if vectors with the same content hash already exist.

        Args:
            vectors_data: List of dictionaries containing 'vector', 'payload', and 'id'
            batch_size: Number of vectors to process in each batch
        """
        if not vectors_data:
            self.logger.info("No vectors to upload")
            return

        total_vectors = len(vectors_data)
        self.logger.info(f"Performing idempotent upload of {total_vectors} vectors")

        # Filter out vectors that already exist based on content hash
        filtered_vectors_data = []
        for item in vectors_data:
            content_hash = item['payload'].get('content_hash', '')
            if not self._vector_exists(content_hash):
                filtered_vectors_data.append(item)
            else:
                self.logger.info(f"Vector with content_hash {content_hash} already exists, skipping")

        if filtered_vectors_data:
            self.upsert_vectors(filtered_vectors_data, batch_size)
        else:
            self.logger.info("All vectors already exist, no new vectors to upload")

    def _vector_exists(self, content_hash: str) -> bool:
        """
        Check if a vector with the given content hash already exists in the collection.
        """
        try:
            # Search for points with the specific content_hash
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content_hash",
                            match=models.MatchValue(value=content_hash)
                        )
                    ]
                ),
                limit=1
            )

            return len(search_result[0]) > 0 if search_result else False

        except Exception as e:
            self.logger.error(f"Error checking if vector exists with hash {content_hash}: {str(e)}")
            # If there's an error checking, assume it doesn't exist to be safe
            return False

    def search_vectors(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: The query vector to search for
            top_k: Number of results to return

        Returns:
            List of search results with payload and similarity scores
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )

            search_results = []
            for result in results:
                search_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload,
                    'vector': result.vector
                })

            return search_results

        except Exception as e:
            self.logger.error(f"Error searching vectors: {str(e)}")
            return []

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection.
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': collection_info.config.params.vectors_count,
                'vector_count': collection_info.points_count,
                'config': {
                    'vector_size': collection_info.config.params.vectors.size,
                    'distance': collection_info.config.params.vectors.distance
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return {}

    def delete_collection(self):
        """
        Delete the entire collection (use with caution!).
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
            raise e

    def count_vectors(self) -> int:
        """
        Count the number of vectors in the collection.
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            self.logger.error(f"Error counting vectors: {str(e)}")
            return 0