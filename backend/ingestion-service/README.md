# Docusaurus Content Ingestion Service

A Python-based ingestion service that crawls Docusaurus websites, extracts content, chunks it, generates embeddings using Cohere, and stores vectors in Qdrant.

## Features

- **Async crawling** of Docusaurus websites
- **Content extraction** with HTML cleanup
- **Token-aware chunking** (500-1200 tokens with overlap)
- **Cohere embedding generation**
- **Qdrant vector storage** with idempotent uploads
- **Comprehensive logging and retry mechanisms**

## Prerequisites

- Python 3.9+
- Access to Cohere API
- Qdrant Cloud account

## Installation

1. Clone the repository
2. Navigate to the ingestion service directory:
   ```bash
   cd backend/ingestion-service
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

Create a `.env` file in the root directory with the following variables:

```env
# Docusaurus site to crawl
DOCUSAURUS_BASE_URL=https://your-docusaurus-site.com

# Cohere API configuration
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-multilingual-v2.0

# Qdrant configuration
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=textbook_content

# Crawler settings
CRAWLER_DELAY=1.0
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30

# Chunking settings
CHUNK_SIZE_MIN=500
CHUNK_SIZE_MAX=1200
CHUNK_OVERLAP=100

# Logging
LOG_LEVEL=INFO

# Retry settings
RETRY_ATTEMPTS=3
RETRY_DELAY=1.0
```

## Usage

### Running the Ingestion Pipeline

```bash
cd backend/ingestion-service
python -m src.ingestion_service
```

### Using as a Module

```python
import asyncio
from src.ingestion_service import IngestionService

async def main():
    ingestion_service = IngestionService()
    report = await ingestion_service.run_ingestion_pipeline("https://your-docusaurus-site.com")
    print(report)

asyncio.run(main())
```

## Architecture

```
[Website URLs]
      ↓
  [Crawler] → Crawls and extracts HTML content
      ↓
[Content Extractor] → Cleans HTML, extracts main content
      ↓
 [Chunker] → Splits content into token-aware chunks
      ↓
[Embedder] → Generates Cohere embeddings
      ↓
 [Qdrant] → Stores vectors with metadata
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DOCUSAURUS_BASE_URL` | Base URL of the Docusaurus site to crawl | Required |
| `COHERE_API_KEY` | Cohere API key | Required |
| `QDRANT_URL` | Qdrant Cloud URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `QDRANT_COLLECTION_NAME` | Name of Qdrant collection | textbook_content |
| `CRAWLER_DELAY` | Delay between requests (seconds) | 1.0 |
| `MAX_CONCURRENT_REQUESTS` | Max concurrent HTTP requests | 5 |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | 30 |
| `CHUNK_SIZE_MIN` | Minimum tokens per chunk | 500 |
| `CHUNK_SIZE_MAX` | Maximum tokens per chunk | 1200 |
| `CHUNK_OVERLAP` | Overlap tokens between chunks | 100 |
| `RETRY_ATTEMPTS` | Number of retry attempts | 3 |
| `RETRY_DELAY` | Initial delay between retries | 1.0 |

## Output

The ingestion service provides a comprehensive summary report:

- Number of pages crawled
- Number of content chunks processed
- Number of embeddings generated
- Number of vectors stored
- Duration of the process
- Any errors encountered

## Idempotent Processing

The service implements idempotent processing by:
- Generating content hashes for each chunk
- Checking if vectors with the same content hash already exist
- Only uploading new or changed content
- Preventing duplicate uploads

## Error Handling

- **Network errors**: Automatic retries with exponential backoff
- **Content extraction errors**: Graceful degradation with fallback methods
- **API errors**: Retry mechanisms and error logging
- **Storage errors**: Detailed error reporting

## Logging

The service provides detailed logging at different levels:
- INFO: Major process steps and progress
- WARNING: Non-critical issues
- ERROR: Critical failures

## Directory Structure

```
backend/ingestion-service/
├── src/
│   ├── crawler.py          # Async crawling functionality
│   ├── embedding_service.py # Cohere embedding generation
│   ├── qdrant_service.py   # Qdrant vector storage
│   └── ingestion_service.py # Main orchestrator
├── utils/
│   ├── tokenization.py     # Text chunking and tokenization
│   ├── content_extraction.py # HTML content extraction
│   └── url_utils.py        # URL handling utilities
├── config/
│   └── settings.py         # Configuration management
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .env.example           # Example environment file
```

## Performance Considerations

- The crawler respects `robots.txt` and implements rate limiting
- Concurrent request limits prevent overwhelming the target server
- Batch processing for embeddings and vector storage
- Memory-efficient processing of large documents

## Troubleshooting

### Common Issues

1. **Cohere API errors**: Verify your API key and model name
2. **Qdrant connection errors**: Check your URL and API key
3. **Crawling rate limits**: Adjust `CRAWLER_DELAY` and `MAX_CONCURRENT_REQUESTS`
4. **Memory issues**: Process large sites in smaller batches

### Logging

Enable DEBUG level logging for detailed troubleshooting:
```env
LOG_LEVEL=DEBUG
```

## Security

- API keys are loaded from environment variables
- No sensitive data is logged
- Follows best practices for HTTP requests

## License

[Specify your license here]