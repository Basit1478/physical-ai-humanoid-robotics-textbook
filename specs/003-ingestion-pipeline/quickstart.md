# Quickstart: Ingestion Pipeline for Docusaurus Website

## Overview
Quick setup guide to run the backend ingestion pipeline that crawls the Physical AI & Humanoid Robotics Docusaurus website, extracts book content, generates Cohere embeddings, and stores vectors in Qdrant.

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip package manager
- Git (for cloning if needed)

### External Services
- Cohere API key (for embeddings)
- Qdrant Cloud account and API key
- Access to the target Docusaurus website

## Setup Instructions

### 1. Clone or Create Project Structure
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
python -m venv ingestion-env

# Activate virtual environment
# On Windows:
ingestion-env\Scripts\activate
# On macOS/Linux:
source ingestion-env/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install requests beautifulsoup4 cohere qdrant-client python-dotenv tiktoken trafilatura
```

### 4. Configure Environment Variables
Create a `.env` file in your project root with the following content:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
DOCUSAURUS_BASE_URL=https://your-docusaurus-site.com
CHUNK_SIZE_MIN=500
CHUNK_SIZE_MAX=1200
CHUNK_OVERLAP=100
```

## Running the Ingestion Pipeline

### 1. Basic Execution
```bash
# Navigate to the ingestion pipeline directory
cd backend/ingestion-pipeline

# Run the main ingestion script
python -m src.main
```

### 2. Configuration Options
The pipeline can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DOCUSAURUS_BASE_URL` | Base URL of the Docusaurus website | Required |
| `COHERE_API_KEY` | Cohere API key for embeddings | Required |
| `QDRANT_URL` | Qdrant Cloud endpoint | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `CHUNK_SIZE_MIN` | Minimum tokens per chunk | 500 |
| `CHUNK_SIZE_MAX` | Maximum tokens per chunk | 1200 |
| `CHUNK_OVERLAP` | Overlap tokens between chunks | 100 |
| `RATE_LIMIT_DELAY` | Delay between requests (seconds) | 1 |

### 3. Command Line Options
```bash
# Run with specific options
python -m src.main --base-url "https://example.com" --limit 50

# Run in debug mode with verbose output
python -m src.main --debug

# Process only specific URLs
python -m src.main --urls "https://example.com/page1,https://example.com/page2"
```

## Pipeline Components

### Crawler
- Discovers all pages from the Docusaurus website
- Follows internal links to find book content
- Respects robots.txt and rate limits

### Extractor
- Removes HTML tags and navigation elements
- Extracts clean text content from pages
- Preserves document structure and hierarchy

### Chunker
- Splits content into 500-1200 token chunks
- Maintains semantic boundaries
- Creates overlapping chunks for context preservation

### Embedder
- Generates Cohere embeddings for each chunk
- Handles API rate limiting and retries
- Validates embedding quality

### Storage
- Stores vectors and metadata in Qdrant
- Implements idempotent processing
- Maintains document-to-chunk relationships

## Verification

### 1. Check Processing Logs
Monitor the console output for processing status:
```
[INFO] Starting ingestion pipeline...
[INFO] Crawling: https://example.com/intro
[INFO] Extracted 2450 tokens from intro page
[INFO] Created 3 chunks from intro page
[INFO] Generated embeddings for 3 chunks
[INFO] Stored 3 vectors in Qdrant
```

### 2. Verify Qdrant Collection
Check that vectors were stored correctly:
```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Check collection size
count = client.count(collection_name="textbook_content")
print(f"Stored {count} vectors")
```

### 3. Sample Query Test
Test retrieval functionality:
```python
# Search for similar content
search_results = client.search(
    collection_name="textbook_content",
    query_vector=your_query_embedding,
    limit=5
)
```

## Troubleshooting

### Common Issues

#### API Rate Limits
- **Issue**: Cohere or Qdrant API rate limit exceeded
- **Solution**: Increase `RATE_LIMIT_DELAY` in configuration

#### Content Extraction Problems
- **Issue**: HTML not properly cleaned
- **Solution**: Update CSS selectors in extractor module

#### Memory Issues
- **Issue**: Processing large sites causes memory errors
- **Solution**: Process documents sequentially, not in parallel

#### Network Errors
- **Issue**: Connection timeouts during crawling
- **Solution**: Increase timeout values in crawler configuration

### Debugging Commands
```bash
# Run with maximum verbosity
python -m src.main --debug --verbose

# Test individual components
python -m src.tests.test_crawler
python -m src.tests.test_extractor
```

## Next Steps

1. **Customize Configuration**: Adjust chunk sizes and overlap based on your content
2. **Monitor Performance**: Track processing time and API usage
3. **Validate Quality**: Review extracted content and embeddings
4. **Scale Processing**: Implement parallel processing for larger sites
5. **Set Up Monitoring**: Add alerts for processing failures

## Support

For issues with the ingestion pipeline:
- Check the project documentation
- Review the processing logs
- Verify API keys and service availability
- Consult the troubleshooting section