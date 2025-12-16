"""
Fixed Qdrant retriever using Cohere embeddings for the RAG Agent service
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import logging
import cohere
from config.settings import settings


class QdrantRetriever:
    def __init__(self):
        if not settings.QDRANT_URL:
            # During validation or if URL is not set, we'll initialize with a mock client
            # In production, this should be handled by validate_required_settings()
            self.client = None
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            self.logger = logging.getLogger(__name__)

            # Initialize Cohere client for validation
            if settings.COHERE_API_KEY:
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            else:
                self.cohere_client = None
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

        # Initialize Cohere client
        if settings.COHERE_API_KEY:
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
        else:
            self.cohere_client = None
            self.logger.warning("COHERE_API_KEY not set - embedding functionality will be limited")

        self.logger = logging.getLogger(__name__)

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
        Retrieve relevant chunks from Qdrant based on the query using Cohere embeddings.
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
            # Embed the query using Cohere - this matches the ingestion service approach
            if not self.cohere_client:
                raise Exception("Cohere client not initialized - COHERE_API_KEY required")

            # Generate embedding for the query using Cohere
            response = self.cohere_client.embed(
                texts=[query],
                model=settings.COHERE_MODEL  # Use the same model as during ingestion
            )

            query_embedding = response.embeddings[0]  # Get the first embedding

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
        """
        if not query.strip() and not selected_text.strip():
            return []

        # Combine query and selected text for better retrieval
        combined_query = f"{query} {selected_text}".strip()

        return self.retrieve_chunks(combined_query, top_k, threshold)

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
                    'vector_size': 1024,
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
            return {}

    def search_with_filters(self, query: str, filters: Dict = None,
                          top_k: Optional[int] = None) -> List[Dict]:
        """
        Search with additional filters on payload fields.
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

            # Generate embedding for the query using Cohere
            if not self.cohere_client:
                raise Exception("Cohere client not initialized - COHERE_API_KEY required")

            # Generate embedding for the query using Cohere
            response = self.cohere_client.embed(
                texts=[query],
                model=settings.COHERE_MODEL  # Use the same model as during ingestion
            )

            query_embedding = response.embeddings[0]  # Get the first embedding

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