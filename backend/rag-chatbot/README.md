# RAG Agent Service

A FastAPI-based Retrieval-Augmented Generation (RAG) agent service that uses Google's Gemini model for question answering, with retrieval from a Qdrant vector database.

## Features

- **RAG Architecture**: Combines retrieval from Qdrant with generation using Gemini
- **Selected Text Queries**: Supports queries focused on specific selected text
- **FastAPI Endpoints**: `/ask`, `/retrieve`, and `/health` endpoints
- **Grounded Responses**: Enforces answers strictly from retrieved context
- **Structured Logging**: Comprehensive logging of queries, retrieved chunks, and responses
- **Environment Configuration**: Flexible configuration via environment variables

## Prerequisites

- Python 3.9+
- Google Gemini API key
- Qdrant Cloud account with populated collection from ingestion service

## Installation

1. Clone the repository
2. Navigate to the RAG agent service directory:
   ```bash
   cd backend/rag-agent
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
# Gemini configuration (required)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Qdrant configuration (required)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=textbook_content

# Agent configuration
AGENT_SYSTEM_INSTRUCTIONS=You are an AI assistant that answers questions based ONLY on the provided context...

# Retrieval configuration
RETRIEVAL_TOP_K=5
RETRIEVAL_THRESHOLD=0.3

# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Logging configuration
LOG_LEVEL=INFO

# Model parameters
TEMPERATURE=0.1
MAX_TOKENS=2048
```

## Usage

### Running the Service

```bash
cd backend/rag-agent
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using the main entry point:
```bash
python -m src.main
```

### API Endpoints

#### 1. Ask Endpoint (`POST /ask`)

Main endpoint for asking questions and getting AI-generated answers.

**Request Body:**
```json
{
  "query_text": "Your question here",
  "selected_text": "Optional selected text for focused queries",
  "context": "Optional additional context"
}
```

**Response:**
```json
{
  "answer": "The AI-generated answer",
  "source_chunks": ["chunk_id_1", "chunk_id_2"],
  "confidence_score": 0.85,
  "citations": [
    {
      "url": "source_url",
      "title": "source_title",
      "position": 1,
      "score": 0.85
    }
  ],
  "query_time": 1.234,
  "selected_text_used": true
}
```

#### 2. Retrieve Endpoint (`POST /retrieve`)

Endpoint to retrieve relevant chunks without generating an answer.

**Request Body:**
```json
{
  "query_text": "Your search query",
  "top_k": 5
}
```

**Response:**
```json
{
  "retrieved_chunks": [
    {
      "id": "chunk_id",
      "score": 0.85,
      "text": "chunk text content",
      "url": "source_url",
      "title": "source_title",
      "position": 1,
      "token_count": 150,
      "source_metadata": {},
      "payload": {}
    }
  ],
  "count": 5,
  "query_time": 0.567
}
```

#### 3. Health Endpoint (`GET /health`)

Health check endpoint to verify service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-15T10:30:00.123456",
  "service_info": {
    "service": "RAG Agent",
    "model": "gemini-2.5-flash",
    "collection_info": {
      "vector_count": 1000,
      "collection_name": "textbook_content"
    }
  }
}
```

## Architecture

```
[User Query]
      ↓
  [FastAPI] → Handles HTTP requests and responses
      ↓
[RAG Agent] → Orchestrates retrieval and generation
      ↓
  [Qdrant] ←→ Retrieves relevant chunks
      ↓
 [Gemini] ←→ Generates grounded response
      ↓
[Response] → Returns answer with citations
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model name | gemini-2.5-flash |
| `QDRANT_URL` | Qdrant Cloud URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `QDRANT_COLLECTION_NAME` | Name of Qdrant collection | textbook_content |
| `AGENT_SYSTEM_INSTRUCTIONS` | System instructions for the agent | Default instructions |
| `RETRIEVAL_TOP_K` | Number of chunks to retrieve | 5 |
| `RETRIEVAL_THRESHOLD` | Minimum similarity threshold | 0.3 |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `TEMPERATURE` | Gemini temperature parameter | 0.1 |
| `MAX_TOKENS` | Maximum tokens in response | 2048 |

## Selected Text Functionality

The service supports selected text queries where users can select specific text and ask questions about it:

1. User selects text in the frontend
2. Selected text is passed along with the query
3. The service combines the query and selected text for more focused retrieval
4. Answers are generated with context from the selected text area

## Logging

The service uses structured logging with the following log events:

- `query_received`: When a query is received
- `chunks_retrieved`: When chunks are retrieved from Qdrant
- `query_answered`: When a response is generated successfully
- `query_error`: When an error occurs during processing
- `answer_validation`: When answer grounding is validated
- `health_check`: When health check is performed

## Security

- API keys are loaded from environment variables
- No sensitive data is logged
- Input validation on all endpoints
- Rate limiting can be added as needed

## Performance Considerations

- Retrieval time depends on Qdrant collection size and query complexity
- Generation time depends on Gemini API response time
- Consider caching for frequently asked questions

## Testing

To test the service:

1. Start the service: `uvicorn src.main:app --reload`
2. Use the `/docs` endpoint for interactive API documentation
3. Test with sample queries via the API or interactive docs

## Directory Structure

```
backend/rag-agent/
├── src/
│   ├── main.py              # FastAPI application
│   └── rag_agent.py         # Main RAG agent service
├── utils/
│   ├── gemini_client.py     # Gemini API client
│   └── qdrant_retriever.py  # Qdrant retrieval utilities
├── config/
│   └── settings.py          # Configuration management
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .env.example           # Example environment file
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Verify GEMINI_API_KEY and QDRANT_API_KEY are correct
2. **No Results**: Check if Qdrant collection has been populated by ingestion service
3. **Slow Responses**: Monitor API usage and consider rate limits
4. **Grounding Issues**: Verify that system instructions are properly enforced

### Logging

Enable DEBUG level logging for detailed troubleshooting:
```env
LOG_LEVEL=DEBUG
```

## License

[Specify your license here]