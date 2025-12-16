# Retrieval Validation Service

A Python-based service for validating the semantic search pipeline by querying Qdrant vectors and confirming semantic relevance and metadata accuracy.

## Features

- **Qdrant Integration**: Connects to existing Qdrant collection with the same embeddings as the ingestion service
- **Semantic Relevance Validation**: Validates that retrieved results are semantically relevant to queries
- **Metadata Accuracy Verification**: Confirms that metadata correctly maps to original modules/pages
- **Multiple Query Type Support**: Validates factual, conceptual, procedural, and comparative queries
- **Comprehensive Metrics**: Calculates precision, MRR, and other validation metrics
- **CLI Test Harness**: Interactive and batch testing capabilities
- **Detailed Logging**: Comprehensive logging of validation metrics and failure cases

## Prerequisites

- Python 3.9+
- Access to Cohere API (same model as ingestion service)
- Qdrant Cloud account with existing collection from ingestion service

## Installation

1. Clone the repository
2. Navigate to the retrieval validation service directory:
   ```bash
   cd backend/retrieval-validation
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables (or copy from your ingestion service):

```env
# Qdrant configuration (should match your ingestion service)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=textbook_content

# Cohere API configuration (should match your ingestion service)
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-multilingual-v2.0

# Retrieval settings
TOP_K=5
COSINE_THRESHOLD=0.3
MAX_QUERY_LENGTH=2000

# Validation settings
RELEVANCE_THRESHOLD=0.7
TEST_QUERY_FILE=test_queries.txt

# Logging
LOG_LEVEL=INFO

# Performance settings
RETRIEVAL_TIMEOUT=30
```

## Usage

### CLI Commands

The service provides several CLI commands for testing and validation:

#### 1. Single Query Search
```bash
python -m src.main search -q "What is inverse kinematics?" --top-k 5
```

#### 2. Comprehensive Validation
```bash
python -m src.main validate --queries-file test_queries.txt --output-file validation_report.json
```

#### 3. Query Type Testing
```bash
python -m src.main test-query-types --query-type factual
python -m src.main test-query-types --query-type all  # Test all types
```

#### 4. Collection Information
```bash
python -m src.main collection-info
```

#### 5. Interactive Mode
```bash
python -m src.main interactive
```

### As a Module

```python
from src.validation_service import ValidationService

# Initialize validation service
validation_service = ValidationService()

# Run comprehensive validation
report = validation_service.run_comprehensive_validation([
    "What is inverse kinematics?",
    "Explain robot path planning"
])

# Print validation report
validation_service.log_validation_metrics(report)
```

## Validation Process

The service performs the following validation steps:

1. **Query Embedding**: Embeds user queries using the same Cohere model as the ingestion service
2. **Similarity Search**: Performs cosine distance similarity search in Qdrant
3. **Result Retrieval**: Retrieves top-k chunks with metadata
4. **Relevance Validation**: Validates semantic relevance using multiple metrics
5. **Metadata Accuracy**: Verifies that metadata correctly maps to original content
6. **Metric Calculation**: Calculates precision, MRR, and other validation metrics

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant Cloud URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `QDRANT_COLLECTION_NAME` | Name of Qdrant collection | textbook_content |
| `COHERE_API_KEY` | Cohere API key | Required |
| `COHERE_MODEL` | Cohere model name | embed-multilingual-v2.0 |
| `TOP_K` | Number of results to retrieve | 5 |
| `COSINE_THRESHOLD` | Minimum similarity threshold | 0.3 |
| `RELEVANCE_THRESHOLD` | Threshold for considering result relevant | 0.7 |
| `TEST_QUERY_FILE` | File containing test queries | test_queries.txt |
| `LOG_LEVEL` | Logging level | INFO |

## Output

The validation service provides comprehensive reports including:

- **Relevance Metrics**: Average relevance scores, percentage of relevant results
- **Precision Metrics**: P@1, P@3, P@5 scores
- **Metadata Accuracy**: Percentage of results with valid metadata
- **Performance Metrics**: Average search time per query
- **Failure Analysis**: Details of any retrieval failures

## Metrics Explained

- **Precision@K (P@K)**: Percentage of relevant results in the top K results
- **Mean Reciprocal Rank (MRR)**: Average of the reciprocal ranks of first relevant result
- **Semantic Relevance**: Combined score of embedding similarity and text similarity
- **Metadata Accuracy**: Percentage of results with complete and valid metadata

## Directory Structure

```
backend/retrieval-validation/
├── src/
│   ├── retrieval_service.py    # Main retrieval functionality
│   ├── validation_service.py   # Validation logic
│   ├── cli_harness.py          # CLI interface
│   └── main.py                 # Entry point
├── utils/
│   ├── embedding_utils.py      # Embedding operations
│   └── similarity_utils.py     # Similarity calculations
├── config/
│   └── settings.py             # Configuration management
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── .env.example              # Example environment file
├── test_queries.txt          # Sample test queries
└── validation_report.json    # Sample output (when generated)
```

## Testing

The service includes multiple testing modes:

1. **Single Query Testing**: Test individual queries with detailed results
2. **Batch Validation**: Run comprehensive validation on multiple queries
3. **Query Type Testing**: Test different types of queries (factual, conceptual, etc.)
4. **Interactive Mode**: Test queries in real-time

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify QDRANT_URL and QDRANT_API_KEY are correct
2. **API Errors**: Check COHERE_API_KEY and ensure account has sufficient credits
3. **Collection Not Found**: Ensure QDRANT_COLLECTION_NAME matches your ingestion service
4. **No Results**: Check if the collection has been populated by the ingestion service

### Logging

Enable DEBUG level logging for detailed troubleshooting:
```env
LOG_LEVEL=DEBUG
```

## Performance Considerations

- The service uses the same Cohere model as the ingestion service for consistency
- Retrieval times depend on collection size and Qdrant performance
- Batch validation can take time for large query sets

## Security

- API keys are loaded from environment variables
- No sensitive data is logged
- Follows best practices for API access

## License

[Specify your license here]