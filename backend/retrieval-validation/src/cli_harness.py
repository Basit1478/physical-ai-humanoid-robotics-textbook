"""
CLI harness for testing the retrieval validation system
"""
import click
import json
import sys
from typing import List
from datetime import datetime

from .validation_service import ValidationService
from .retrieval_service import RetrievalService
from config.settings import TOP_K, RELEVANCE_THRESHOLD


@click.group()
def cli():
    """CLI harness for retrieval validation testing."""
    pass


@cli.command()
@click.option('--query', '-q', required=True, help='Query to test')
@click.option('--top-k', default=TOP_K, help='Number of results to retrieve (default: 5)')
@click.option('--threshold', default=RELEVANCE_THRESHOLD, help='Relevance threshold (default: 0.7)')
def search(query: str, top_k: int, threshold: float):
    """Perform a single search and validate results."""
    click.echo(f"Searching for: '{query}'")
    click.echo(f"Top-K: {top_k}, Relevance Threshold: {threshold}")
    click.echo("-" * 60)

    try:
        retrieval_service = RetrievalService()
        result = retrieval_service.search_with_validation(query, top_k=top_k)

        if not result['results']:
            click.echo("No results found.")
            return

        click.echo(f"Found {len(result['results'])} results:")
        click.echo(f"Search time: {result['search_time']:.4f} seconds")
        click.echo()

        for i, res in enumerate(result['results'], 1):
            relevance_status = "✓ RELEVANT" if res['is_relevant'] else "✗ NOT RELEVANT"
            click.echo(f"{i}. {relevance_status}")
            click.echo(f"   Score: {res['score']:.4f}, Relevance: {res['combined_relevance']:.4f}")
            click.echo(f"   Title: {res['title']}")
            click.echo(f"   URL: {res['url']}")
            click.echo(f"   Preview: {res['text'][:200]}...")
            click.echo()

    except Exception as e:
        click.echo(f"Error during search: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--queries-file', '-f', default='test_queries.txt', help='File with test queries (one per line)')
@click.option('--top-k', default=TOP_K, help='Number of results to retrieve (default: 5)')
@click.option('--output-file', '-o', help='Output file for validation report')
def validate(queries_file: str, top_k: int, output_file: str):
    """Run comprehensive validation on a set of test queries."""
    click.echo(f"Running validation on queries from: {queries_file}")
    click.echo(f"Top-K: {top_k}")
    click.echo("-" * 60)

    try:
        validation_service = ValidationService()

        # Load queries from file
        try:
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            click.echo(f"Loaded {len(queries)} queries from {queries_file}")
        except FileNotFoundError:
            click.echo(f"Queries file {queries_file} not found.")
            click.echo("Creating a sample queries file...")
            queries = [
                "What is inverse kinematics?",
                "Explain robot path planning",
                "How does PID controller work?",
                "What are the types of robot actuators?",
                "Describe forward kinematics"
            ]
            with open(queries_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(queries))
            click.echo(f"Created sample file with {len(queries)} queries")
            click.echo("You can edit this file and run validation again.")

        if not queries:
            click.echo("No queries to validate.")
            return

        # Run comprehensive validation
        report = validation_service.run_comprehensive_validation(queries)

        # Display summary
        summary = report['summary']
        click.echo(f"Validation completed!")
        click.echo(f"Status: {summary['status']}")
        click.echo(f"Queries processed: {summary['queries_processed']}")
        click.echo(f"Relevance score: {summary['relevance_score']:.4f}")
        click.echo(f"Metadata accuracy: {summary['metadata_accuracy']:.2f}%")

        # Display precision metrics
        precision = report['relevance_validation']['precision_metrics']
        click.echo("\nPrecision Metrics:")
        for k, score in precision.items():
            click.echo(f"  {k.upper()}: {score}%")

        # Display performance metrics
        perf = report['performance_metrics']
        click.echo(f"\nAvg search time: {perf['avg_search_time_per_query']:.4f}s/query")

        # Save report if output file specified
        if output_file:
            validation_service.save_validation_report(report, output_file)
            click.echo(f"\nFull report saved to: {output_file}")

        # Log detailed report
        validation_service.log_validation_metrics(report)

    except Exception as e:
        click.echo(f"Error during validation: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--query-type', '-t', type=click.Choice(['factual', 'conceptual', 'procedural', 'comparative', 'all']),
              default='all', help='Type of queries to test')
@click.option('--top-k', default=TOP_K, help='Number of results to retrieve (default: 5)')
def test_query_types(query_type: str, top_k: int):
    """Test different types of queries."""
    click.echo(f"Testing {query_type} queries")
    click.echo(f"Top-K: {top_k}")
    click.echo("-" * 60)

    # Define sample queries by type
    query_types = {
        'factual': [
            "What is the definition of inverse kinematics?",
            "What is the formula for PID controller?",
            "List the types of robot sensors"
        ],
        'conceptual': [
            "Explain the concept of robot kinematics",
            "What is the difference between forward and inverse kinematics?",
            "Describe how path planning works in robotics"
        ],
        'procedural': [
            "How to implement a PID controller?",
            "Steps for robot calibration",
            "How to perform inverse kinematics calculation"
        ],
        'comparative': [
            "Compare forward and inverse kinematics",
            "What are the differences between various path planning algorithms?",
            "Compare different types of robot actuators"
        ]
    }

    if query_type == 'all':
        test_queries = []
        for qtype, queries in query_types.items():
            test_queries.extend(queries)
    else:
        test_queries = query_types.get(query_type, [])

    if not test_queries:
        click.echo(f"No test queries available for type: {query_type}")
        return

    try:
        retrieval_service = RetrievalService()
        validation_service = ValidationService()

        click.echo(f"Testing {len(test_queries)} {query_type} queries...")
        click.echo()

        total_relevance = 0
        total_results = 0
        successful_queries = 0

        for i, query in enumerate(test_queries, 1):
            click.echo(f"{i}. Query: {query}")
            result = retrieval_service.search_with_validation(query, top_k=top_k)

            if result['results']:
                avg_relevance = sum(r['combined_relevance'] for r in result['results']) / len(result['results'])
                total_relevance += avg_relevance
                total_results += len(result['results'])
                successful_queries += 1

                click.echo(f"   Results: {len(result['results'])}, Avg Relevance: {avg_relevance:.4f}")
                click.echo(f"   Search Time: {result['search_time']:.4f}s")
            else:
                click.echo("   No results found")

            click.echo()

        if successful_queries > 0:
            overall_avg_relevance = total_relevance / successful_queries
            click.echo(f"Overall Results:")
            click.echo(f"  Successful queries: {successful_queries}/{len(test_queries)}")
            click.echo(f"  Overall avg relevance: {overall_avg_relevance:.4f}")
            click.echo(f"  Total results: {total_results}")

    except Exception as e:
        click.echo(f"Error during query type testing: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def collection_info():
    """Get information about the Qdrant collection."""
    click.echo("Fetching collection information...")
    click.echo("-" * 60)

    try:
        retrieval_service = RetrievalService()
        stats = retrieval_service.get_collection_stats()

        if not stats:
            click.echo("Could not retrieve collection information.")
            return

        click.echo(f"Collection: {stats['collection_name']}")
        click.echo(f"Vector Count: {stats['vector_count']}")
        click.echo(f"Vector Size: {stats['config']['vector_size']}")
        click.echo(f"Distance: {stats['config']['distance']}")

    except Exception as e:
        click.echo(f"Error fetching collection info: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def interactive():
    """Interactive mode for testing queries."""
    click.echo("Interactive Query Testing Mode")
    click.echo("Enter queries (type 'quit' or 'exit' to quit)")
    click.echo("-" * 60)

    retrieval_service = RetrievalService()

    while True:
        try:
            query = click.prompt('\nQuery', type=str)
            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query.strip():
                continue

            result = retrieval_service.search_with_validation(query)

            if not result['results']:
                click.echo("No results found.")
                continue

            click.echo(f"\nFound {len(result['results'])} results:")
            for i, res in enumerate(result['results'][:3], 1):  # Show top 3
                relevance_status = "✓" if res['is_relevant'] else "✗"
                click.echo(f"{i}. {relevance_status} Score: {res['score']:.4f}")
                click.echo(f"   Title: {res['title']}")
                click.echo(f"   Preview: {res['text'][:100]}...")
                click.echo()

        except KeyboardInterrupt:
            click.echo("\nExiting interactive mode...")
            break
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)

    click.echo("Goodbye!")


if __name__ == '__main__':
    cli()