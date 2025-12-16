"""
Retrieval service for validating semantic search pipeline
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import logging
import time
from config.settings import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, TOP_K, COSINE_THRESHOLD
from utils.embedding_utils import EmbeddingService
from utils.similarity_utils import calculate_semantic_relevance, rank_results_by_relevance


class RetrievalService:
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
        self.top_k = TOP_K
        self.embedding_service = EmbeddingService()
        self.logger = logging.getLogger(__name__)

    def validate_collection_exists(self) -> bool:
        """
        Validate that the Qdrant collection exists.
        """
        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            return collection_exists
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {str(e)}")
            return False

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Perform semantic search using the same Cohere model and cosine distance.

        Args:
            query: The search query string
            top_k: Number of results to return (uses default if None)

        Returns:
            List of results with text, metadata, and similarity scores
        """
        if not query.strip():
            return []

        k = top_k or self.top_k

        try:
            # Embed the query using the same Cohere model as the ingestion service
            query_embedding = self.embedding_service.embed_query(query)

            # Perform search in Qdrant using cosine distance
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=k,
                with_payload=True,  # Include metadata
                with_vectors=False,  # Don't include vectors to save bandwidth
                score_threshold=COSINE_THRESHOLD  # Minimum similarity threshold
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

            self.logger.info(f"Search completed: '{query[:50]}...' -> {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            return []

    def search_with_validation(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        Perform search and include validation metrics.

        Args:
            query: The search query string
            top_k: Number of results to return (uses default if None)

        Returns:
            Dictionary containing results and validation metrics
        """
        start_time = time.time()

        # Perform the search
        results = self.search(query, top_k)

        search_time = time.time() - start_time

        # Calculate relevance for each result
        validated_results = []
        for result in results:
            relevance_data = calculate_semantic_relevance(
                query,
                result['text'],
                [],  # We don't have embeddings here, but the function will use text similarity
                result['text']
            )

            validated_result = result.copy()
            validated_result.update(relevance_data)
            validated_results.append(validated_result)

        # Sort by combined relevance score
        ranked_results = rank_results_by_relevance(query, validated_results)

        # Calculate validation metrics
        metrics = {
            'query': query,
            'query_length': len(query),
            'results_count': len(ranked_results),
            'search_time_seconds': round(search_time, 4),
            'average_score': sum(r['score'] for r in ranked_results) / len(ranked_results) if ranked_results else 0,
            'average_relevance': sum(r['combined_relevance'] for r in ranked_results) / len(ranked_results) if ranked_results else 0,
            'top_result_score': ranked_results[0]['score'] if ranked_results else 0,
            'top_result_relevance': ranked_results[0]['combined_relevance'] if ranked_results else 0
        }

        return {
            'query': query,
            'results': ranked_results,
            'metrics': metrics,
            'search_time': search_time
        }

    def batch_search(self, queries: List[str], top_k: Optional[int] = None) -> List[Dict]:
        """
        Perform multiple searches and return validation results.

        Args:
            queries: List of query strings
            top_k: Number of results to return for each query

        Returns:
            List of search results with validation for each query
        """
        all_results = []

        for i, query in enumerate(queries):
            self.logger.info(f"Processing query {i+1}/{len(queries)}: '{query[:30]}...'")
            result = self.search_with_validation(query, top_k)
            all_results.append(result)

        return all_results

    def validate_retrieval_accuracy(self, query_result_pairs: List[Dict]) -> Dict:
        """
        Validate retrieval accuracy by comparing expected vs retrieved results.

        Args:
            query_result_pairs: List of dicts with 'query', 'expected_result_id', and optionally 'expected_text'

        Returns:
            Validation metrics including accuracy scores
        """
        correct_retrievals = 0
        total_queries = len(query_result_pairs)

        detailed_results = []

        for pair in query_result_pairs:
            query = pair['query']
            expected_id = pair.get('expected_result_id')
            expected_text = pair.get('expected_text', '')

            # Search for the query
            search_results = self.search(query, top_k=self.top_k)

            # Check if expected result is in top results
            found_expected = False
            rank_of_expected = -1

            for i, result in enumerate(search_results):
                if expected_id and result['id'] == expected_id:
                    found_expected = True
                    rank_of_expected = i + 1  # 1-indexed
                    break
                elif expected_text and expected_text in result['text']:
                    found_expected = True
                    rank_of_expected = i + 1
                    break

            detailed_result = {
                'query': query,
                'expected_id': expected_id,
                'expected_text_contains': expected_text != '',
                'found_expected': found_expected,
                'rank_of_expected': rank_of_expected,
                'top_result_id': search_results[0]['id'] if search_results else None,
                'top_result_score': search_results[0]['score'] if search_results else 0,
                'total_results': len(search_results)
            }

            detailed_results.append(detailed_result)

            if found_expected:
                correct_retrievals += 1

        accuracy = correct_retrievals / total_queries if total_queries > 0 else 0

        return {
            'accuracy': accuracy,
            'total_queries': total_queries,
            'correct_retrievals': correct_retrievals,
            'detailed_results': detailed_results,
            'metrics': {
                'accuracy_percentage': round(accuracy * 100, 2),
                'queries_with_results': sum(1 for r in detailed_results if r['total_results'] > 0),
                'avg_rank_of_expected': sum(r['rank_of_expected'] for r in detailed_results if r['rank_of_expected'] > 0) /
                                       sum(1 for r in detailed_results if r['rank_of_expected'] > 0) if any(r['rank_of_expected'] > 0 for r in detailed_results) else 0
            }
        }

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        """
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