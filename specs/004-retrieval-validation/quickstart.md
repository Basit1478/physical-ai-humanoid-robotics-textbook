# Quickstart: Retrieval Validation Module

## Overview
Quick setup guide to run the retrieval validation module that queries Qdrant vectors and validates semantic search pipeline effectiveness.

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip package manager
- Git (for cloning if needed)

### External Services
- Qdrant Cloud account with existing collection from Spec 1
- Cohere API key (same as used in Spec 1)
- Access to the Qdrant collection created in the ingestion pipeline

## Setup Instructions

### 1. Clone or Access Project Structure
```bash
# If using the full project:
git clone <repository-url>
cd <project-root>

# Navigate to backend directory
cd backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv retrieval-validation-env

# Activate virtual environment
# On Windows:
retrieval-validation-env\Scripts\activate
# On macOS/Linux:
source retrieval-validation-env/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install qdrant-client cohere python-dotenv scikit-learn nltk ranx
```

### 4. Configure Environment Variables
Create a `.env` file in your project root with the following content:

```env
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
VALIDATION_RESULT_PATH=./validation_results
RELEVANCE_THRESHOLD=0.7
MAX_RESULTS_PER_QUERY=10
```

## Running the Validation Module

### 1. Basic Validation Run
```bash
# Navigate to the retrieval validation directory
cd backend/retrieval-validation

# Run the validation with default test queries
python -m src.main
```

### 2. Configuration Options
The validation module can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant Cloud endpoint | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `COHERE_API_KEY` | Cohere API key for query embeddings | Required |
| `VALIDATION_RESULT_PATH` | Path to store validation results | ./validation_results |
| `RELEVANCE_THRESHOLD` | Threshold for relevance scoring | 0.7 |
| `MAX_RESULTS_PER_QUERY` | Maximum results to retrieve per query | 10 |
| `COLLECTION_NAME` | Qdrant collection name | textbook_content |

### 3. Command Line Options
```bash
# Run with specific options
python -m src.main --queries-file "path/to/queries.json" --limit 20

# Run specific query types only
python -m src.main --query-types "factual,conceptual"

# Run with custom result count
python -m src.main --top-k 5

# Run in verbose mode with detailed output
python -m src.main --verbose
```

## Validation Components

### Query Generator
- Loads test queries from various sources
- Generates different query types (factual, conceptual, procedural, comparative)
- Manages test datasets with known answer sets

### Qdrant Connector
- Connects to existing Qdrant collection
- Executes vector similarity searches
- Retrieves results with metadata
- Handles connection errors and retries

### Relevance Evaluator
- Compares query text with retrieved content
- Calculates semantic similarity scores
- Determines relevance based on thresholds
- Provides relevance feedback

### Metadata Validator
- Verifies URL mapping accuracy
- Checks document title consistency
- Validates position and section information
- Identifies metadata discrepancies

### Metrics Calculator
- Calculates precision at K (P@1, P@3, P@5)
- Computes Mean Reciprocal Rank (MRR)
- Calculates Normalized Discounted Cumulative Gain (NDCG)
- Generates aggregate statistics

## Sample Validation Run

### 1. Execute Validation
```bash
python -m src.main --queries-file ./sample-queries.json --output-format json
```

### 2. Expected Output
The validation will produce output similar to:
```
[INFO] Starting validation run...
[INFO] Loaded 25 test queries
[INFO] Executing query 1/25: "What is inverse kinematics?"
[INFO] Retrieved 10 results, relevance: 0.85, metadata accuracy: 0.95
[INFO] Executing query 2/25: "Explain robot path planning"
[INFO] Retrieved 10 results, relevance: 0.78, metadata accuracy: 0.92
...
[SUMMARY] Validation completed
  Total queries: 25
  Average relevance: 0.82
  Average metadata accuracy: 0.94
  Precision@1: 0.76
  Precision@3: 0.81
  MRR: 0.79
  Results saved to: ./validation_results/validation-run-20251215.json
```

### 3. Validation Report
The validation results will be saved in the specified output directory with detailed metrics:
- Overall validation summary
- Individual query results
- Relevance scores for each result
- Metadata accuracy verification
- Performance metrics

## Verification

### 1. Check Validation Results
Verify the validation completed successfully by checking the output:
```
Validation Results Summary:
- Total Queries: 25
- Successful Executions: 25
- Failed Executions: 0
- Average Response Time: 1.2s
- Overall Relevance Score: 0.82
- Metadata Accuracy: 94%
```

### 2. Validate Qdrant Connection
Ensure the module can connect to your Qdrant instance:
```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Check if collection exists and has vectors
collection_info = client.get_collection(collection_name="textbook_content")
print(f"Points in collection: {collection_info.points_count}")
```

### 3. Sample Query Test
Test a single query to verify functionality:
```bash
python -c "
from src.qdrant_connector import QdrantConnector
connector = QdrantConnector()
results = connector.search('What is inverse kinematics?', top_k=3)
print('Sample results:', results[:3])
"
```

## Troubleshooting

### Common Issues

#### Qdrant Connection Errors
- **Issue**: Cannot connect to Qdrant Cloud
- **Solution**: Verify `QDRANT_URL` and `QDRANT_API_KEY` in your `.env` file

#### API Rate Limits
- **Issue**: Cohere API rate limit exceeded
- **Solution**: Add delays between queries or upgrade API plan

#### Empty Results
- **Issue**: Queries return no results
- **Solution**: Verify the Qdrant collection has data from Spec 1

#### Embedding Mismatch
- **Issue**: Query embeddings don't match stored document embeddings
- **Solution**: Ensure same Cohere model is used as in Spec 1

### Debugging Commands
```bash
# Run with maximum verbosity
python -m src.main --verbose --debug

# Test Qdrant connection only
python -m src.tests.test_connection

# Validate specific query
python -m src.main --single-query "test query here"
```

## Next Steps

1. **Customize Test Queries**: Add your own test queries to validate specific content areas
2. **Adjust Thresholds**: Modify relevance thresholds based on your requirements
3. **Analyze Results**: Review validation reports to identify areas for improvement
4. **Schedule Runs**: Set up periodic validation runs to monitor retrieval quality
5. **Expand Test Sets**: Create comprehensive test datasets covering all content areas

## Support

For issues with the retrieval validation module:
- Check the project documentation
- Review the validation logs
- Verify Qdrant collection has data from Spec 1
- Consult the troubleshooting section