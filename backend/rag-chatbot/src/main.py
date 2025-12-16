"""
FastAPI application for the RAG Agent service
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
import asyncio
from config.settings import settings
from .rag_agent import RAGAgent


# Request/Response models
class AskRequest(BaseModel):
    query_text: str
    selected_text: Optional[str] = None
    context: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    source_chunks: List[str]
    confidence_score: float
    citations: List[Dict]
    query_time: float
    selected_text_used: Optional[bool] = None


class RetrieveRequest(BaseModel):
    query_text: str
    top_k: Optional[int] = settings.RETRIEVAL_TOP_K


class RetrieveResponse(BaseModel):
    retrieved_chunks: List[Dict]
    count: int
    query_time: float
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service_info: Dict


class IngestDocumentRequest(BaseModel):
    text: str
    title: str
    url: str
    metadata: Optional[Dict] = {}


class IngestDocumentResponse(BaseModel):
    status: str
    document_id: str
    message: str


class IngestUrlRequest(BaseModel):
    url: str
    recursive: bool = False
    max_pages: int = 10


class IngestUrlResponse(BaseModel):
    status: str
    documents_processed: int
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent API",
    description="Retrieval-Augmented Generation Agent using Gemini model",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Agent
rag_agent = RAGAgent()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))

# Try to set up structlog for structured logging, but make it optional
try:
    import structlog
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

    def get_logger():
        return structlog.get_logger()
except ImportError:
    # If structlog is not available, use standard logging
    def get_logger():
        return logging.getLogger(__name__)


@app.get("/")
async def root():
    """Root endpoint for basic service information."""
    return {
        "message": "RAG Agent API",
        "version": "1.0.0",
        "endpoints": ["/ask", "/retrieve", "/health"]
    }


@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    Endpoint to ask questions and get answers from the RAG agent.

    - **query_text**: The question to answer
    - **selected_text**: Optional selected text to focus the answer
    - **context**: Additional context (optional)
    """
    try:
        # Log the incoming request
        logger = get_logger()
        logger.info(
            "ask_endpoint_called",
            query_text=request.query_text,
            has_selected_text=bool(request.selected_text)
        )

        # Process the request based on whether selected text is provided
        if request.selected_text:
            response = rag_agent.process_selected_text_query(
                request.query_text,
                request.selected_text
            )
        else:
            response = rag_agent.ask(
                request.query_text,
                request.selected_text
            )

        return AskResponse(**response)

    except Exception as e:
        logger = get_logger()
        logger.error("ask_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_endpoint(request: RetrieveRequest):
    """
    Endpoint to retrieve relevant chunks from the knowledge base.

    - **query_text**: The query to search for
    - **top_k**: Number of chunks to retrieve (default from config)
    """
    try:
        # Log the incoming request
        logger = get_logger()
        logger.info(
            "retrieve_endpoint_called",
            query_text=request.query_text,
            top_k=request.top_k
        )

        response = rag_agent.retrieve_only(
            request.query_text,
            request.top_k
        )

        return RetrieveResponse(**response)

    except Exception as e:
        logger = get_logger()
        logger.error("retrieve_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """
    Health check endpoint to verify service status.
    """
    try:
        # Check if required services are available
        service_info = rag_agent.get_service_info()

        # Verify Qdrant connection by checking collection
        collection_exists = True  # This would be checked in a real implementation

        health_status = "healthy" if collection_exists else "degraded"

        response = HealthResponse(
            status=health_status,
            timestamp=str(__import__('datetime').datetime.now().isoformat()),
            service_info=service_info
        )

        logger = get_logger()
        logger.info("health_check", status=health_status)
        return response

    except Exception as e:
        logger = get_logger()
        logger.error("health_check_error", error=str(e))
        return HealthResponse(
            status="unhealthy",
            timestamp=str(__import__('datetime').datetime.now().isoformat()),
            service_info={"error": str(e)}
        )


@app.get("/info")
async def info_endpoint():
    """
    Get detailed information about the service configuration.
    """
    try:
        service_info = rag_agent.get_service_info()
        return {
            "service": "RAG Agent",
            "config": {
                "gemini_model": settings.GEMINI_MODEL,
                "retrieval_top_k": settings.RETRIEVAL_TOP_K,
                "retrieval_threshold": settings.RETRIEVAL_THRESHOLD,
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_TOKENS
            },
            "service_info": service_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting service info: {str(e)}")


# Additional utility endpoints
@app.get("/stats")
async def stats_endpoint():
    """
    Get statistics about the service.
    """
    try:
        service_info = rag_agent.get_service_info()
        return {
            "collection_stats": service_info.get('collection_info', {}),
            "model": service_info.get('model', 'unknown'),
            "uptime": "tracking would be implemented in production"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# Add ingestion endpoints
@app.post("/ingest/document", response_model=IngestDocumentResponse)
async def ingest_document_endpoint(request: IngestDocumentRequest):
    """
    Endpoint to ingest a single document into the knowledge base.

    - **text**: The content of the document
    - **title**: Title of the document
    - **url**: URL or identifier for the document
    - **metadata**: Additional metadata for the document
    """
    try:
        logger = get_logger()
        logger.info(
            "ingest_document_endpoint_called",
            title=request.title,
            url=request.url
        )

        # Use the RAG agent to handle document ingestion
        result = await rag_agent.ingest_single_document(
            text=request.text,
            title=request.title,
            url=request.url,
            metadata=request.metadata
        )

        return IngestDocumentResponse(**result)

    except Exception as e:
        logger = get_logger()
        logger.error("ingest_document_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")


@app.post("/ingest/url", response_model=IngestUrlResponse)
async def ingest_url_endpoint(request: IngestUrlRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to ingest content from a URL into the knowledge base.

    - **url**: The URL to crawl and ingest
    - **recursive**: Whether to crawl recursively (default: false)
    - **max_pages**: Maximum number of pages to crawl (default: 10)
    """
    try:
        logger = get_logger()
        logger.info(
            "ingest_url_endpoint_called",
            url=request.url,
            recursive=request.recursive,
            max_pages=request.max_pages
        )

        # Use the RAG agent to handle URL ingestion
        result = await rag_agent.ingest_from_url(
            url=request.url,
            recursive=request.recursive,
            max_pages=request.max_pages
        )

        return IngestUrlResponse(**result)

    except Exception as e:
        logger = get_logger()
        logger.error("ingest_url_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error ingesting from URL: {str(e)}")


@app.get("/ingestion/status")
async def ingestion_status_endpoint():
    """
    Get the current status of the ingestion system.
    """
    try:
        service_info = rag_agent.get_service_info()
        return {
            "status": "ready",
            "ingestion_info": service_info.get('ingestion_info', {}),
            "collection_stats": service_info.get('collection_info', {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ingestion status: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )