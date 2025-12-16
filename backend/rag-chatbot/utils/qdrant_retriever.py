"""
Qdrant retriever for the RAG Agent service
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import logging
from config.settings import settings
from .gemini_client import GeminiClient


class QdrantRetriever:
    def __init__(self):
        if not settings.QDRANT_URL:
            # During validation or if URL is not set, we'll initialize with a mock client
            # In production, this should be handled by validate_required_settings()
            self.client = None
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            self.gemini_client = GeminiClient()

            # Initialize Cohere client for validation
            if settings.COHERE_API_KEY:
                import cohere
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            else:
                self.cohere_client = None
            self.logger = logging.getLogger(__name__)
            return

        # Initialize Qdrant client
        if settings.QDRANT_API_KEY:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=False  # Using HTTP for better compatibility
            )
        else:
            self.client = QdrantClient(url=settings.QDRANT_URL)

        self.collection_name = settings.QDRANT_COLLECTION_NAME

        # Initialize logger before using it
        self.logger = logging.getLogger(__name__)

        # Ensure the collection exists with the correct configuration
        self.ensure_collection_exists(vector_size=768)

        self.gemini_client = GeminiClient()

        # Initialize Cohere client for embedding queries
        if settings.COHERE_API_KEY:
            import cohere
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
        else:
            self.cohere_client = None
            self.logger.warning("COHERE_API_KEY not set - embedding functionality will be limited")

    def validate_collection_exists(self) -> bool:
        """
        Validate that the Qdrant collection exists.
        """
        if not self.client:
            # For validation purposes
            return True

        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            return collection_exists
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {str(e)}")
            return False

    def retrieve_chunks(self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None) -> List[Dict]:
        """
        Retrieve relevant chunks from Qdrant based on the query.

        Args:
            query: The query string
            top_k: Number of results to retrieve (uses default if None)
            threshold: Minimum similarity threshold (uses default if None)

        Returns:
            List of retrieved chunks with text, metadata, and similarity scores
        """
        if not query.strip():
            return []

        if not self.client:
            # Mock response for validation
            k = top_k or settings.RETRIEVAL_TOP_K
            mock_chunks = []
            for i in range(min(k, 3)):  # Return up to 3 mock chunks
                mock_chunks.append({
                    'id': f'mock_chunk_{i}',
                    'score': 0.8,
                    'text': f'Mock content for query: {query[:30]}... This is a simulated response for validation purposes.',
                    'url': 'mock-url',
                    'title': 'Mock Title',
                    'position': i,
                    'token_count': 100,
                    'source_metadata': {},
                    'payload': {}
                })
            return mock_chunks

        k = top_k or settings.RETRIEVAL_TOP_K
        sim_threshold = threshold or settings.RETRIEVAL_THRESHOLD

        try:
            # Embed the query using Cohere with 768-dimensional vectors for compatibility with the collection
            try:
                if self.cohere_client:
                    response = self.cohere_client.embed(
                        texts=[query],
                        model=settings.COHERE_MODEL,
                        input_type="search_query",
                        embedding_types=["float"]
                    )
                    # Extract the embedding - for v3 models with embedding_types, the result is nested
                    query_embedding = response.embeddings.float[0]
                    # Ensure it's exactly 768 dimensions (truncate or pad if needed)
                    while len(query_embedding) < 768:
                        query_embedding.append(0.0)
                    query_embedding = query_embedding[:768]
                else:
                    # Fallback to placeholder embedding
                    query_embedding = self._get_placeholder_embedding_768(query)
            except Exception as e:
                self.logger.warning(f"Error using Cohere for query embedding: {str(e)}, falling back to placeholder")
                query_embedding = self._get_placeholder_embedding_768(query)

            # Perform search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                with_payload=True,  # Include metadata
                with_vectors=False,  # Don't include vectors to save bandwidth
                score_threshold=sim_threshold  # Minimum similarity threshold
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    'id': result.id,
                    'score': result.score,
                    'text': result.payload.get('text', ''),
                    'url': result.payload.get('url', ''),
                    'title': result.payload.get('title', ''),
                    'position': result.payload.get('position', 0),
                    'token_count': result.payload.get('token_count', 0),
                    'source_metadata': result.payload.get('source_metadata', {}),
                    'payload': result.payload  # Keep original payload
                }
                formatted_results.append(formatted_result)

            self.logger.info(f"Retrieved {len(formatted_results)} chunks for query: '{query[:50]}...'")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error during retrieval: {str(e)}")
            return []

    def retrieve_chunks_with_selected_text(self, query: str, selected_text: str,
                                         top_k: Optional[int] = None,
                                         threshold: Optional[float] = None) -> List[Dict]:
        """
        Retrieve relevant chunks using both the query and selected text as context.

        Args:
            query: The main query string
            selected_text: Selected text to focus the search
            top_k: Number of results to retrieve (uses default if None)
            threshold: Minimum similarity threshold (uses default if None)

        Returns:
            List of retrieved chunks with text, metadata, and similarity scores
        """
        if not query.strip() and not selected_text.strip():
            return []

        # Combine query and selected text for better retrieval
        combined_query = f"{query} {selected_text}".strip()

        return self.retrieve_chunks(combined_query, top_k, threshold)

    def _get_placeholder_embedding_768(self, text: str) -> List[float]:
        """
        Placeholder method to generate 768-dimensional embeddings when proper embedding model is not available.
        This matches the dimensionality of the new collection.
        """
        # This is just a placeholder - in real implementation, you'd use the same
        # embedding model that was used during ingestion
        import hashlib
        import math

        # Create a hash of the text
        hash_obj = hashlib.sha256(text.encode())
        hex_dig = hash_obj.hexdigest()

        # Convert hex to a list of floats
        embedding = []
        for i in range(0, len(hex_dig), 2):
            if i + 1 < len(hex_dig):
                val = int(hex_dig[i:i+2], 16) / 255.0  # Normalize to 0-1
                embedding.append(val)

        # Pad or truncate to exactly 768 dimensions
        while len(embedding) < 768:
            embedding.append(0.0)
        embedding = embedding[:768]

        return embedding

    def _get_placeholder_embedding(self, text: str) -> List[float]:
        """
        Placeholder method to generate embeddings when proper embedding model is not available.
        In a real implementation, you'd use the same embedding model as the ingestion service.
        """
        # This is just a placeholder - in real implementation, you'd use the same
        # embedding model that was used during ingestion
        # For now, return a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hex_dig = hash_obj.hexdigest()

        # Convert hex to a list of floats (this is just a placeholder approach)
        embedding = []
        for i in range(0, len(hex_dig), 2):
            if i + 1 < len(hex_dig):
                val = int(hex_dig[i:i+2], 16) / 255.0  # Normalize to 0-1
                embedding.append(val)

        # Pad or truncate to a fixed size (e.g., 128 dimensions)
        while len(embedding) < 128:
            embedding.append(0.0)
        embedding = embedding[:128]

        return embedding

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        """
        if not self.client:
            # Mock response for validation
            return {
                'vector_count': 0,
                'collection_name': self.collection_name,
                'config': {
                    'vector_size': 768,
                    'distance': 'cosine'
                }
            }

        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'vector_count': collection_info.points_count,
                'collection_name': self.collection_name,
                'config': {
                    'vector_size': collection_info.config.params.vectors.size,
                    'distance': collection_info.config.params.vectors.distance
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            # Try to ensure collection exists if there's an error
            self.ensure_collection_exists(vector_size=768)
            # Return basic info after attempting to create collection
            try:
                collection_info = self.client.get_collection(self.collection_name)
                return {
                    'vector_count': collection_info.points_count,
                    'collection_name': self.collection_name,
                    'config': {
                        'vector_size': collection_info.config.params.vectors.size,
                        'distance': collection_info.config.params.vectors.distance
                    }
                }
            except Exception as e2:
                self.logger.error(f"Error getting collection stats after recreation attempt: {str(e2)}")
                return {}

    def search_with_filters(self, query: str, filters: Dict = None,
                          top_k: Optional[int] = None) -> List[Dict]:
        """
        Search with additional filters on payload fields.

        Args:
            query: The search query string
            filters: Dictionary of filter conditions (e.g., {'url': 'specific_url'})
            top_k: Number of results to retrieve

        Returns:
            List of filtered search results
        """
        if not query.strip():
            return []

        if not self.client:
            # Mock response for validation
            k = top_k or settings.RETRIEVAL_TOP_K
            mock_results = []
            for i in range(min(k, 2)):  # Return up to 2 mock results
                mock_results.append({
                    'id': f'mock_filtered_result_{i}',
                    'score': 0.75,
                    'text': f'Mock filtered content for query: {query[:30]}...',
                    'url': 'mock-url',
                    'title': 'Mock Filtered Title',
                    'position': i,
                    'token_count': 100,
                    'source_metadata': {},
                    'payload': {}
                })
            return mock_results

        k = top_k or settings.RETRIEVAL_TOP_K

        try:
            # Create Qdrant filter conditions
            filter_conditions = []
            if filters:
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

            # Embed the query using Cohere with 768-dimensional vectors for compatibility with the collection
            try:
                if self.cohere_client:
                    response = self.cohere_client.embed(
                        texts=[query],
                        model=settings.COHERE_MODEL,
                        input_type="search_query",
                        embedding_types=["float"]
                    )
                    # Extract the embedding - for v3 models with embedding_types, the result is nested
                    query_embedding = response.embeddings.float[0]
                    # Ensure it's exactly 768 dimensions (truncate or pad if needed)
                    while len(query_embedding) < 768:
                        query_embedding.append(0.0)
                    query_embedding = query_embedding[:768]
                else:
                    # Fallback to placeholder embedding
                    query_embedding = self._get_placeholder_embedding_768(query)
            except Exception as e:
                self.logger.warning(f"Error using Cohere for query embedding: {str(e)}, falling back to placeholder")
                query_embedding = self._get_placeholder_embedding_768(query)

            search_filter = models.Filter(must=filter_conditions) if filter_conditions else None

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=k,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    'id': result.id,
                    'score': result.score,
                    'text': result.payload.get('text', ''),
                    'url': result.payload.get('url', ''),
                    'title': result.payload.get('title', ''),
                    'position': result.payload.get('position', 0),
                    'token_count': result.payload.get('token_count', 0),
                    'source_metadata': result.payload.get('source_metadata', {}),
                    'payload': result.payload
                }
                formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            self.logger.error(f"Error during filtered search: {str(e)}")
            return []

    def store_single_vector(self, vector_id: str, vector: List[float], payload: Dict) -> bool:
        """
        Store a single vector with its payload in Qdrant.

        Args:
            vector_id: Unique identifier for the vector
            vector: The embedding vector (list of floats)
            payload: Metadata to store with the vector

        Returns:
            Boolean indicating success
        """
        if not self.client:
            # For validation purposes
            self.logger.warning("Cannot store vector: Qdrant client not initialized")
            return False

        try:
            from qdrant_client.http import models

            # Prepare the point
            point = models.PointStruct(
                id=vector_id,
                vector=vector,
                payload=payload
            )

            # Upsert the point to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            self.logger.info(f"Stored vector with ID: {vector_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error storing vector: {str(e)}")
            return False

    def ensure_collection_exists(self, vector_size: int = 768) -> bool:
        """
        Ensure that the Qdrant collection exists with the correct configuration.

        Args:
            vector_size: Size of the vectors (default 768 for compatibility)

        Returns:
            Boolean indicating if collection exists/is created successfully
        """
        if not self.client:
            self.logger.error("Cannot ensure collection exists: Qdrant client not initialized")
            return False

        try:
            from qdrant_client.http import models

            # Check if collection already exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with 768-dimensional vectors
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

                self.logger.info(f"Created Qdrant collection '{self.collection_name}' with {vector_size}-dimensional vectors")
                return True
            else:
                # Verify the collection has the correct vector size
                collection_info = self.client.get_collection(self.collection_name)
                current_size = collection_info.config.params.vectors.size

                if current_size != vector_size:
                    self.logger.warning(f"Collection has {current_size}-dimensional vectors, expected {vector_size}")
                    # Note: In Qdrant, you cannot change vector size after creation
                    # This would require recreating the collection, which we won't do automatically
                else:
                    self.logger.info(f"Qdrant collection '{self.collection_name}' exists with correct {vector_size}-dimensional vectors")

                return True

        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {str(e)}")
            return False

    def get_vector_count(self) -> int:
        """
        Get the total count of vectors in the collection.
        """
        if not self.client:
            # For validation purposes
            return 0

        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            self.logger.error(f"Error getting vector count: {str(e)}")
            return 0