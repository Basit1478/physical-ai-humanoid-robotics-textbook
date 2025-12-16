# Quickstart: RAG Agent using OpenAI Agents SDK with Gemini model

## Overview
Quick setup guide to run the Retrieval-Augmented Generation (RAG) Agent that uses OpenAI Agents SDK with a Gemini model and FastAPI integration.

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip package manager
- Git (for cloning if needed)

### External Services
- Qdrant Cloud account with existing collection from Spec 1
- Google Gemini API key
- Access to the Qdrant collection created in the ingestion pipeline (Spec 1)

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
python -m venv rag-agent-env

# Activate virtual environment
# On Windows:
rag-agent-env\Scripts\activate
# On macOS/Linux:
source rag-agent-env/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install fastapi uvicorn qdrant-client pydantic python-dotenv google-generativeai
```

### 4. Configure Environment Variables
Create a `.env` file in your project root with the following content:

```env
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=textbook_content
AGENT_MODEL=gemini-2.5-flash
RETRIEVAL_TOP_K=5
RETRIEVAL_THRESHOLD=0.7
MAX_TOKENS=2048
TEMPERATURE=0.1
```

## Running the RAG Agent

### 1. Start the FastAPI Server
```bash
# Navigate to the RAG agent directory
cd backend/rag-agent

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configuration Options
The RAG agent can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API key for agent responses | Required |
| `QDRANT_URL` | Qdrant Cloud endpoint | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `QDRANT_COLLECTION` | Name of the Qdrant collection | textbook_content |
| `AGENT_MODEL` | Gemini model name | gemini-2.5-flash |
| `RETRIEVAL_TOP_K` | Number of chunks to retrieve | 5 |
| `RETRIEVAL_THRESHOLD` | Similarity threshold for retrieval | 0.7 |
| `MAX_TOKENS` | Maximum tokens in agent response | 2048 |
| `TEMPERATURE` | Response randomness (0-1) | 0.1 |

### 3. API Endpoints
Once running, the agent provides the following endpoints:

#### Synchronous Question Answering
- **Endpoint**: `POST /api/v1/ask`
- **Description**: Answers questions synchronously using retrieved content

**Request Body**:
```json
{
  "query_text": "What is inverse kinematics?",
  "selected_text": "optional selected text for focused queries",
  "context": "optional additional context"
}
```

**Response**:
```json
{
  "response_id": "uuid",
  "answer_text": "The agent's response based on retrieved content...",
  "source_chunks": ["chunk_id_1", "chunk_id_2"],
  "confidence_score": 0.85,
  "citations": [
    {
      "url": "https://example.com/docs/kinematics",
      "title": "Kinematics Concepts",
      "position": 1
    }
  ]
}
```

#### Streaming Response
- **Endpoint**: `POST /api/v1/ask/stream`
- **Description**: Provides streaming response for better user experience

**Request Body**: Same as synchronous endpoint

**Response**: Server-sent events with response chunks

#### Health Check
- **Endpoint**: `GET /health`
- **Description**: Checks service health and external dependencies

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00Z",
  "dependencies": {
    "gemini": "connected",
    "qdrant": "connected"
  }
}
```

## Using the RAG Agent

### 1. Basic Question Answering
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "Explain robot path planning algorithms"
  }'
```

### 2. Selected Text Query
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are the key points?",
    "selected_text": "Path planning is a fundamental problem in robotics that involves finding a collision-free path from a start to goal configuration."
  }'
```

### 3. Query with Context
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "How does this relate to the previous concept?",
    "context": "We were discussing motion planning techniques"
  }'
```

## Agent Components

### Retrieval Service
- Connects to Qdrant vector database
- Performs semantic search using the same embeddings as Spec 1
- Retrieves top-k most relevant content chunks
- Includes metadata and source information

### Gemini Agent
- Uses OpenAI Agents SDK configured with Gemini model
- Processes retrieved context to generate responses
- Ensures responses are grounded in retrieved content
- Prevents hallucinations through content validation

### RAG Orchestrator
- Coordinates retrieval and generation processes
- Formats context for the agent
- Validates response quality
- Generates citations and metadata

### Content Validator
- Ensures all responses are based on retrieved content
- Detects and prevents hallucinations
- Validates factual accuracy
- Provides confidence scoring

## Verification

### 1. Check Service Health
Verify the service is running correctly:
```bash
curl http://localhost:8000/health
```

### 2. Test Basic Functionality
Test with a simple query:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is the main topic of this textbook?"
  }'
```

### 3. Verify Content Grounding
Check that responses include source citations and are based on retrieved content:
- Look for `source_chunks` in the response
- Verify `citations` reference actual textbook content
- Confirm response is factual and not hallucinated

## Troubleshooting

### Common Issues

#### Gemini API Connection Errors
- **Issue**: Cannot connect to Gemini API
- **Solution**: Verify `GEMINI_API_KEY` in your `.env` file

#### Qdrant Connection Errors
- **Issue**: Cannot connect to Qdrant Cloud
- **Solution**: Verify `QDRANT_URL` and `QDRANT_API_KEY` in your `.env` file

#### No Results Returned
- **Issue**: Queries return no results
- **Solution**: Verify the Qdrant collection has data from Spec 1

#### Content Hallucination
- **Issue**: Agent responds with information not in the textbook
- **Solution**: Adjust retrieval threshold or implement stricter validation

### Debugging Commands
```bash
# Run with verbose logging
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level debug

# Test individual components
python -c "
from src.services.qdrant_service import QdrantService
service = QdrantService()
results = service.search('test query', top_k=3)
print('Retrieved chunks:', len(results))
"
```

## Next Steps

1. **Customize Configuration**: Adjust retrieval parameters and agent settings based on your needs
2. **Test with Domain Queries**: Try queries specific to your textbook content
3. **Monitor Performance**: Track response times and quality metrics
4. **Scale Deployment**: Consider containerization and orchestration for production
5. **Add Monitoring**: Implement logging and monitoring for production use

## Support

For issues with the RAG agent:
- Check the project documentation
- Review the service logs
- Verify Qdrant collection has data from Spec 1
- Consult the troubleshooting section