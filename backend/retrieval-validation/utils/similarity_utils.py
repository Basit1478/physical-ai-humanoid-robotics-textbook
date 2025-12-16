"""
Similarity utilities for the retrieval validation service
"""
import numpy as np
from typing import List, Tuple
import re


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings using multiple methods.
    Uses TF-IDF with sklearn if available, otherwise falls back to simple overlap.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    # If texts are identical, return 1.0
    if text1.strip() == text2.strip():
        return 1.0

    # Try using sklearn for more sophisticated similarity if available
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Simple preprocessing
        def preprocess(text):
            # Remove extra whitespace and convert to lowercase
            text = re.sub(r'\s+', ' ', text.lower().strip())
            return text

        processed_text1 = preprocess(text1)
        processed_text2 = preprocess(text2)

        # Use TF-IDF vectorization for similarity calculation
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity_matrix[0][0])
    except ImportError:
        # Fallback to simple overlap similarity if sklearn is not available
        return calculate_simple_overlap_similarity(text1, text2)


def calculate_simple_overlap_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity based on word overlap as a fallback method.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    # Preprocess texts: convert to lowercase, remove extra whitespace, split into words
    def preprocess(text):
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split into words and remove empty strings
        words = [word for word in text.split() if word.strip()]
        return set(words)  # Use set to get unique words

    words1 = preprocess(text1)
    words2 = preprocess(text2)

    if not words1 and not words2:
        return 1.0  # Both texts are empty
    if not words1 or not words2:
        return 0.0  # One is empty, the other is not

    # Calculate Jaccard similarity (intersection over union)
    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    jaccard_similarity = len(intersection) / len(union)
    return jaccard_similarity


def calculate_bm25_similarity(text1: str, text2: str, k1: float = 1.5, b: float = 0.75) -> float:
    """
    Calculate similarity using a simplified BM25 approach.
    This is a simplified version for demonstration purposes.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    # Preprocess texts
    def preprocess(text):
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return set(text.split())  # Use set to get unique words

    words1 = preprocess(text1)
    words2 = preprocess(text2)

    if not words1 or not words2:
        return 0.0

    # Calculate overlap
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    if union == 0:
        return 0.0

    # Simplified BM25-like calculation
    overlap_ratio = intersection / union
    length_penalty = min(len(words1), len(words2)) / max(len(words1), len(words2))

    return overlap_ratio * length_penalty


def calculate_semantic_relevance(query: str, result_text: str, query_embedding: List[float] = None,
                                result_embedding: List[float] = None) -> dict:
    """
    Calculate various measures of semantic relevance between query and result.
    """
    # Calculate embedding-based similarity if embeddings are provided
    embedding_similarity = 0.0
    if query_embedding and result_embedding and len(query_embedding) == len(result_embedding):
        from utils.embedding_utils import EmbeddingService
        service = EmbeddingService()
        embedding_similarity = service.cosine_similarity(query_embedding, result_embedding)

    # Calculate text-based similarity
    text_similarity = calculate_text_similarity(query, result_text)

    # Combined relevance score (average of both measures)
    combined_relevance = (embedding_similarity + text_similarity) / 2.0

    return {
        'embedding_similarity': embedding_similarity,
        'text_similarity': text_similarity,
        'combined_relevance': combined_relevance,
        'is_relevant': combined_relevance >= 0.5  # Default threshold
    }


def rank_results_by_relevance(query: str, results: List[dict]) -> List[dict]:
    """
    Rank a list of results by their relevance to the query.
    Each result should have 'text', 'embedding', and 'score' keys.
    """
    ranked_results = []
    for result in results:
        relevance_data = calculate_semantic_relevance(
            query,
            result.get('text', ''),
            result.get('embedding', []),
            result.get('text', '')
        )

        # Combine Qdrant score with our relevance calculation
        qdrant_score = result.get('score', 0.0)
        combined_score = (qdrant_score + relevance_data['combined_relevance']) / 2.0

        ranked_result = result.copy()
        ranked_result.update(relevance_data)
        ranked_result['combined_score'] = combined_score

        ranked_results.append(ranked_result)

    # Sort by combined score in descending order
    ranked_results.sort(key=lambda x: x['combined_score'], reverse=True)
    return ranked_results


def calculate_precision_at_k(relevant_results: List[bool], k: int) -> float:
    """
    Calculate precision at k (P@k) for validation.
    relevant_results: List of booleans indicating if each result is relevant
    """
    if not relevant_results or k <= 0:
        return 0.0

    # Take only the first k results
    top_k_results = relevant_results[:k] if len(relevant_results) >= k else relevant_results

    # Calculate precision
    relevant_count = sum(1 for is_relevant in top_k_results if is_relevant)
    return relevant_count / len(top_k_results) if top_k_results else 0.0


def calculate_mean_reciprocal_rank(relevant_results_list: List[List[bool]]) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR) for validation.
    relevant_results_list: List of lists, each containing booleans for a query's results
    """
    if not relevant_results_list:
        return 0.0

    reciprocal_ranks = []
    for relevant_results in relevant_results_list:
        # Find the rank of the first relevant result (1-indexed)
        for rank, is_relevant in enumerate(relevant_results, 1):
            if is_relevant:
                reciprocal_ranks.append(1.0 / rank)
                break
        else:
            # No relevant results found
            reciprocal_ranks.append(0.0)

    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0