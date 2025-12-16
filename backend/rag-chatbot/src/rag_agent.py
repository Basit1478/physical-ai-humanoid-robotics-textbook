"""
RAG Agent service that orchestrates retrieval and generation
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import sys

# Try to import structlog for structured logging, but make it optional
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None

from config.settings import settings
from utils.gemini_client import GeminiClient
from utils.qdrant_retriever import QdrantRetriever


class RAGAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.qdrant_retriever = QdrantRetriever()

        # Initialize logger - use structlog if available, otherwise standard logging
        if STRUCTLOG_AVAILABLE:
            self.logger = structlog.get_logger(__name__)
            # Initialize structured logger
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        else:
            self.logger = logging.getLogger(__name__)

    def _log_info(self, event: str, **kwargs):
        """Log info message with structlog if available, otherwise use standard logging."""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(event, **kwargs)
        else:
            self.logger.info(f"{event}: {kwargs}")

    def _log_error(self, event: str, **kwargs):
        """Log error message with structlog if available, otherwise use standard logging."""
        if STRUCTLOG_AVAILABLE:
            self.logger.error(event, **kwargs)
        else:
            self.logger.error(f"{event}: {kwargs}")

    def ask(self, query: str, selected_text: Optional[str] = None) -> Dict:
        """
        Main method to answer questions using RAG approach.

        Args:
            query: The question to answer
            selected_text: Optional selected text to focus the answer

        Returns:
            Dictionary containing the answer and metadata
        """
        start_time = datetime.now()

        try:
            # Log the incoming query
            self._log_info("query_received", query=query, selected_text=selected_text)

            # Retrieve relevant chunks from Qdrant
            if selected_text:
                retrieved_chunks = self.qdrant_retriever.retrieve_chunks_with_selected_text(
                    query, selected_text
                )
            else:
                retrieved_chunks = self.qdrant_retriever.retrieve_chunks(query)

            # Log retrieved chunks
            self._log_info(
                "chunks_retrieved",
                count=len(retrieved_chunks),
                query=query,
                chunk_ids=[chunk['id'] for chunk in retrieved_chunks]
            )

            if not retrieved_chunks:
                response = {
                    'answer': "I couldn't find any relevant information in the knowledge base to answer your question.",
                    'source_chunks': [],
                    'confidence_score': 0.0,
                    'citations': [],
                    'query_time': (datetime.now() - start_time).total_seconds()
                }
                self._log_info("no_chunks_found", query=query)
                return response

            # Generate answer using Gemini with retrieved context
            answer = self.gemini_client.generate_content_with_retrieved_context(
                query, retrieved_chunks
            )

            # Extract source information for citations
            citations = []
            for chunk in retrieved_chunks:
                citation = {
                    'url': chunk.get('url', ''),
                    'title': chunk.get('title', ''),
                    'position': chunk.get('position', 0),
                    'score': chunk.get('score', 0.0)
                }
                citations.append(citation)

            # Calculate confidence based on top chunk score
            confidence_score = max(chunk.get('score', 0.0) for chunk in retrieved_chunks) if retrieved_chunks else 0.0

            # Prepare response
            response = {
                'answer': answer,
                'source_chunks': [chunk['id'] for chunk in retrieved_chunks],
                'confidence_score': confidence_score,
                'citations': citations,
                'query_time': (datetime.now() - start_time).total_seconds()
            }

            # Log successful response
            self._log_info(
                "query_answered",
                query=query,
                answer_length=len(answer),
                confidence_score=confidence_score,
                query_time=response['query_time']
            )

            return response

        except Exception as e:
            self._log_error("query_error", query=query, error=str(e))
            return {
                'answer': f"An error occurred while processing your query: {str(e)}",
                'source_chunks': [],
                'confidence_score': 0.0,
                'citations': [],
                'query_time': (datetime.now() - start_time).total_seconds()
            }

    def retrieve_only(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        Method to only retrieve relevant chunks without generating an answer.

        Args:
            query: The query to search for
            top_k: Number of chunks to retrieve

        Returns:
            Dictionary containing the retrieved chunks
        """
        start_time = datetime.now()

        try:
            # Log the retrieval request
            self._log_info("retrieval_request", query=query, top_k=top_k)

            # Retrieve chunks
            retrieved_chunks = self.qdrant_retriever.retrieve_chunks(query, top_k)

            # Log retrieved chunks
            self._log_info(
                "retrieval_completed",
                count=len(retrieved_chunks),
                query=query,
                query_time=(datetime.now() - start_time).total_seconds()
            )

            return {
                'retrieved_chunks': retrieved_chunks,
                'count': len(retrieved_chunks),
                'query_time': (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            self._log_error("retrieval_error", query=query, error=str(e))
            return {
                'retrieved_chunks': [],
                'count': 0,
                'query_time': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }

    def validate_answer_grounding(self, answer: str, context: str) -> bool:
        """
        Validate that the answer is grounded in the provided context.
        """
        try:
            is_valid = self.gemini_client.validate_response_against_context(answer, context)
            self._log_info("answer_validation", is_valid=is_valid)
            return is_valid
        except Exception as e:
            self._log_error("validation_error", error=str(e))
            return False

    def get_service_info(self) -> Dict:
        """
        Get information about the service and its components.
        """
        try:
            collection_stats = self.qdrant_retriever.get_collection_stats()
            return {
                'service': 'RAG Agent',
                'model': settings.GEMINI_MODEL,
                'collection_info': collection_stats,
                'retrieval_top_k': settings.RETRIEVAL_TOP_K,
                'retrieval_threshold': settings.RETRIEVAL_THRESHOLD,
                'system_instructions': settings.AGENT_SYSTEM_INSTRUCTIONS
            }
        except Exception as e:
            self._log_error("service_info_error", error=str(e))
            return {
                'service': 'RAG Agent',
                'error': str(e)
            }

    def process_selected_text_query(self, query: str, selected_text: str) -> Dict:
        """
        Process a query that focuses on selected text.

        Args:
            query: The question about the selected text
            selected_text: The text that was selected

        Returns:
            Dictionary containing the focused answer
        """
        start_time = datetime.now()

        try:
            # Log the selected text query
            self._log_info(
                "selected_text_query",
                query=query,
                selected_text_preview=selected_text[:100] + "..." if len(selected_text) > 100 else selected_text
            )

            # Retrieve chunks relevant to both query and selected text
            retrieved_chunks = self.qdrant_retriever.retrieve_chunks_with_selected_text(
                query, selected_text
            )

            if not retrieved_chunks:
                response = {
                    'answer': "I couldn't find specific information related to the selected text to answer your question.",
                    'source_chunks': [],
                    'confidence_score': 0.0,
                    'citations': [],
                    'query_time': (datetime.now() - start_time).total_seconds(),
                    'selected_text_used': True
                }
                self._log_info("no_selected_text_chunks", query=query)
                return response

            # Generate answer using Gemini with retrieved context
            answer = self.gemini_client.generate_content_with_retrieved_context(
                query, retrieved_chunks
            )

            # Extract source information for citations
            citations = []
            for chunk in retrieved_chunks:
                citation = {
                    'url': chunk.get('url', ''),
                    'title': chunk.get('title', ''),
                    'position': chunk.get('position', 0),
                    'score': chunk.get('score', 0.0)
                }
                citations.append(citation)

            # Calculate confidence based on top chunk score
            confidence_score = max(chunk.get('score', 0.0) for chunk in retrieved_chunks) if retrieved_chunks else 0.0

            response = {
                'answer': answer,
                'source_chunks': [chunk['id'] for chunk in retrieved_chunks],
                'confidence_score': confidence_score,
                'citations': citations,
                'query_time': (datetime.now() - start_time).total_seconds(),
                'selected_text_used': True
            }

            # Log successful response
            self._log_info(
                "selected_text_answered",
                query=query,
                answer_length=len(answer),
                confidence_score=confidence_score,
                query_time=response['query_time']
            )

            return response

        except Exception as e:
            self._log_error("selected_text_error", query=query, error=str(e))
            return {
                'answer': f"An error occurred while processing your selected text query: {str(e)}",
                'source_chunks': [],
                'confidence_score': 0.0,
                'citations': [],
                'query_time': (datetime.now() - start_time).total_seconds(),
                'selected_text_used': True
            }