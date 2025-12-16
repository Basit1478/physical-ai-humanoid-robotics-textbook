"""
Validation service for validating retrieval quality and accuracy
"""
import logging
import time
from typing import List, Dict, Tuple
from datetime import datetime
import json
from config.settings import RELEVANCE_THRESHOLD, TEST_QUERY_FILE
from .retrieval_service import RetrievalService
from utils.similarity_utils import (
    calculate_precision_at_k, calculate_mean_reciprocal_rank,
    calculate_semantic_relevance
)


class ValidationService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.logger = logging.getLogger(__name__)
        self.validation_results = []

    def validate_semantic_relevance(self, query: str, results: List[Dict]) -> Dict:
        """
        Validate semantic relevance of retrieved results.

        Args:
            query: The original query
            results: List of retrieved results

        Returns:
            Validation metrics for semantic relevance
        """
        if not results:
            return {
                'query': query,
                'relevant_count': 0,
                'total_results': 0,
                'relevance_percentage': 0.0,
                'avg_relevance_score': 0.0
            }

        relevant_count = 0
        total_relevance_score = 0.0
        relevance_details = []

        for result in results:
            # Calculate semantic relevance
            relevance_data = calculate_semantic_relevance(
                query,
                result['text'],
                [],  # Using text similarity fallback
                result['text']
            )

            is_relevant = relevance_data['combined_relevance'] >= RELEVANCE_THRESHOLD
            if is_relevant:
                relevant_count += 1

            total_relevance_score += relevance_data['combined_relevance']

            relevance_detail = {
                'result_id': result['id'],
                'text_preview': result['text'][:200],
                'embedding_similarity': relevance_data['embedding_similarity'],
                'text_similarity': relevance_data['text_similarity'],
                'combined_relevance': relevance_data['combined_relevance'],
                'is_relevant': is_relevant
            }
            relevance_details.append(relevance_detail)

        avg_relevance_score = total_relevance_score / len(results) if results else 0.0
        relevance_percentage = (relevant_count / len(results)) * 100 if results else 0.0

        return {
            'query': query,
            'relevant_count': relevant_count,
            'total_results': len(results),
            'relevance_percentage': round(relevance_percentage, 2),
            'avg_relevance_score': round(avg_relevance_score, 4),
            'relevance_details': relevance_details
        }

    def validate_metadata_accuracy(self, results: List[Dict]) -> Dict:
        """
        Validate that metadata correctly maps to modules/pages.

        Args:
            results: List of retrieved results

        Returns:
            Validation metrics for metadata accuracy
        """
        if not results:
            return {
                'total_results': 0,
                'valid_metadata_count': 0,
                'metadata_accuracy_percentage': 0.0,
                'issues': []
            }

        valid_metadata_count = 0
        issues = []

        for result in results:
            result_issues = []
            is_valid = True

            # Check if required metadata fields exist
            if not result.get('url'):
                result_issues.append('Missing URL')
                is_valid = False

            if not result.get('title'):
                result_issues.append('Missing title')
                is_valid = False

            if 'position' not in result:
                result_issues.append('Missing position')
                is_valid = False

            if is_valid:
                valid_metadata_count += 1

            if result_issues:
                issues.append({
                    'result_id': result['id'],
                    'issues': result_issues
                })

        accuracy_percentage = (valid_metadata_count / len(results)) * 100 if results else 0.0

        return {
            'total_results': len(results),
            'valid_metadata_count': valid_metadata_count,
            'metadata_accuracy_percentage': round(accuracy_percentage, 2),
            'issues': issues
        }

    def validate_multiple_query_types(self, queries_by_type: Dict[str, List[str]]) -> Dict:
        """
        Validate retrieval across multiple query types.

        Args:
            queries_by_type: Dictionary mapping query types to lists of queries

        Returns:
            Validation results grouped by query type
        """
        type_results = {}

        for query_type, queries in queries_by_type.items():
            self.logger.info(f"Validating {query_type} queries ({len(queries)} total)")

            type_start_time = time.time()
            query_results = []

            for query in queries:
                search_result = self.retrieval_service.search_with_validation(query)
                relevance_validation = self.validate_semantic_relevance(query, search_result['results'])

                query_results.append({
                    'query': query,
                    'search_result': search_result,
                    'relevance_validation': relevance_validation
                })

            type_end_time = time.time()

            # Calculate aggregate metrics for this query type
            total_relevance_score = sum(qr['relevance_validation']['avg_relevance_score'] for qr in query_results)
            avg_relevance_score = total_relevance_score / len(query_results) if query_results else 0.0

            relevant_results_count = sum(qr['relevance_validation']['relevant_count'] for qr in query_results)
            total_results_count = sum(qr['relevance_validation']['total_results'] for qr in query_results)
            relevance_percentage = (relevant_results_count / total_results_count * 100) if total_results_count > 0 else 0.0

            type_results[query_type] = {
                'query_count': len(queries),
                'avg_search_time': (type_end_time - type_start_time) / len(queries) if queries else 0,
                'avg_relevance_score': round(avg_relevance_score, 4),
                'relevance_percentage': round(relevance_percentage, 2),
                'detailed_results': query_results
            }

        return {
            'query_types_validated': list(type_results.keys()),
            'results_by_type': type_results,
            'summary': {
                'total_query_types': len(type_results),
                'total_queries': sum(len(queries_by_type[qtype]) for qtype in type_results.keys())
            }
        }

    def run_comprehensive_validation(self, test_queries: List[str] = None) -> Dict:
        """
        Run comprehensive validation of the retrieval system.

        Args:
            test_queries: Optional list of test queries (if None, will try to load from file)

        Returns:
            Comprehensive validation report
        """
        start_time = time.time()

        # Load test queries if not provided
        if test_queries is None:
            test_queries = self._load_test_queries()

        if not test_queries:
            self.logger.warning("No test queries provided or found")
            return self._empty_validation_report()

        self.logger.info(f"Starting comprehensive validation with {len(test_queries)} queries")

        # Perform retrieval for all test queries
        all_search_results = self.retrieval_service.batch_search(test_queries)

        # Validate semantic relevance
        relevance_results = []
        total_relevance_score = 0.0
        total_relevant_results = 0
        total_results = 0

        for search_result in all_search_results:
            query = search_result['query']
            results = search_result['results']

            relevance_validation = self.validate_semantic_relevance(query, results)
            relevance_results.append(relevance_validation)

            total_relevance_score += relevance_validation['avg_relevance_score']
            total_relevant_results += relevance_validation['relevant_count']
            total_results += relevance_validation['total_results']

        # Validate metadata accuracy
        all_results = [result for search_result in all_search_results for result in search_result['results']]
        metadata_validation = self.validate_metadata_accuracy(all_results)

        # Calculate aggregate metrics
        avg_relevance_score = total_relevance_score / len(relevance_results) if relevance_results else 0.0
        overall_relevance_percentage = (total_relevant_results / total_results * 100) if total_results > 0 else 0.0

        # Calculate precision at different k values
        precision_metrics = {}
        for k in [1, 3, 5]:
            # For simplicity, using a basic precision calculation across all queries
            relevant_at_k = 0
            total_at_k = 0

            for search_result in all_search_results:
                results = search_result['results'][:k]
                relevant_count = sum(1 for r in results if r.get('is_relevant', r.get('combined_relevance', 0) >= RELEVANCE_THRESHOLD))
                relevant_at_k += relevant_count
                total_at_k += len(results)

            precision_at_k = (relevant_at_k / total_at_k * 100) if total_at_k > 0 else 0.0
            precision_metrics[f'precision_at_{k}'] = round(precision_at_k, 2)

        end_time = time.time()

        # Compile comprehensive report
        report = {
            'validation_run': {
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'end_time': datetime.fromtimestamp(end_time).isoformat(),
                'duration_seconds': round(end_time - start_time, 2),
                'total_queries': len(test_queries)
            },
            'relevance_validation': {
                'avg_relevance_score': round(avg_relevance_score, 4),
                'overall_relevance_percentage': round(overall_relevance_percentage, 2),
                'total_relevant_results': total_relevant_results,
                'total_results': total_results,
                'precision_metrics': precision_metrics,
                'detailed_results': relevance_results
            },
            'metadata_validation': metadata_validation,
            'performance_metrics': {
                'avg_search_time_per_query': round(
                    sum(sr['search_time'] for sr in all_search_results) / len(all_search_results) if all_search_results else 0,
                    4
                )
            },
            'summary': {
                'status': 'completed',
                'queries_processed': len(test_queries),
                'results_retrieved': total_results,
                'relevance_score': round(avg_relevance_score, 4),
                'metadata_accuracy': metadata_validation['metadata_accuracy_percentage']
            }
        }

        self.validation_results.append(report)
        return report

    def log_validation_metrics(self, report: Dict):
        """
        Log validation metrics for monitoring and debugging.
        """
        self.logger.info("=" * 60)
        self.logger.info("RETRIEVAL VALIDATION REPORT")
        self.logger.info("=" * 60)

        summary = report['summary']
        self.logger.info(f"Status: {summary['status']}")
        self.logger.info(f"Queries Processed: {summary['queries_processed']}")
        self.logger.info(f"Results Retrieved: {summary['results_retrieved']}")
        self.logger.info(f"Relevance Score: {summary['relevance_score']}")
        self.logger.info(f"Metadata Accuracy: {summary['metadata_accuracy']}%")

        # Performance metrics
        perf = report['performance_metrics']
        self.logger.info(f"Avg Search Time: {perf['avg_search_time_per_query']}s/query")

        # Precision metrics
        precision = report['relevance_validation']['precision_metrics']
        for k, score in precision.items():
            self.logger.info(f"{k.upper()}: {score}%")

        # Relevance metrics
        rel = report['relevance_validation']
        self.logger.info(f"Overall Relevance: {rel['overall_relevance_percentage']}%")

        # Metadata metrics
        meta = report['metadata_validation']
        self.logger.info(f"Metadata Valid: {meta['valid_metadata_count']}/{meta['total_results']}")

        self.logger.info("=" * 60)

    def _load_test_queries(self) -> List[str]:
        """
        Load test queries from file or return default queries.
        """
        try:
            with open(TEST_QUERY_FILE, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Loaded {len(queries)} test queries from {TEST_QUERY_FILE}")
            return queries
        except FileNotFoundError:
            self.logger.info(f"Test query file {TEST_QUERY_FILE} not found, using default queries")
            # Return some default test queries
            return [
                "What is inverse kinematics?",
                "Explain robot path planning",
                "How does PID controller work?",
                "What are the types of robot actuators?",
                "Describe forward kinematics"
            ]
        except Exception as e:
            self.logger.error(f"Error loading test queries: {str(e)}")
            return []

    def _empty_validation_report(self) -> Dict:
        """
        Return an empty validation report when no queries are available.
        """
        current_time = time.time()
        return {
            'validation_run': {
                'start_time': datetime.fromtimestamp(current_time).isoformat(),
                'end_time': datetime.fromtimestamp(current_time).isoformat(),
                'duration_seconds': 0,
                'total_queries': 0
            },
            'relevance_validation': {
                'avg_relevance_score': 0.0,
                'overall_relevance_percentage': 0.0,
                'total_relevant_results': 0,
                'total_results': 0,
                'precision_metrics': {'precision_at_1': 0.0, 'precision_at_3': 0.0, 'precision_at_5': 0.0},
                'detailed_results': []
            },
            'metadata_validation': {
                'total_results': 0,
                'valid_metadata_count': 0,
                'metadata_accuracy_percentage': 0.0,
                'issues': []
            },
            'performance_metrics': {
                'avg_search_time_per_query': 0.0
            },
            'summary': {
                'status': 'no_queries',
                'queries_processed': 0,
                'results_retrieved': 0,
                'relevance_score': 0.0,
                'metadata_accuracy': 0.0
            }
        }

    def save_validation_report(self, report: Dict, filename: str = None):
        """
        Save validation report to a file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Validation report saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving validation report: {str(e)}")