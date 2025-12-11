from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from ..qdrant_setup import QdrantSetup
from qdrant_client.http import models
import uuid

router = APIRouter(prefix="/rag")

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    query_id: str

class DocumentUploadRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]
    user_id: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str

# Initialize the LLM with Gemini
def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        # Initialize Qdrant
        qdrant = QdrantSetup()

        # In a real implementation, you would generate embeddings for the query
        # and search in the Qdrant collection for relevant documents
        # For this example, we'll use a simple approach

        # Search for relevant documents in Qdrant
        # This is a simplified approach - in practice you'd use vector similarity search
        results = qdrant.client.scroll(
            collection_name=qdrant.collections["documents"],
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=request.user_id)
                    )
                ]
            ) if request.user_id else None,
            limit=5
        )

        # Extract content from results
        context_docs = []
        if results[0]:
            for point in results[0]:
                context_docs.append({
                    "content": point.payload.get("content", ""),
                    "metadata": point.payload.get("metadata", {}),
                    "doc_id": point.payload.get("doc_id", "")
                })

        # Initialize LLM
        llm = get_gemini_llm()

        # Prepare context for the LLM
        context_str = "\n".join([doc["content"] for doc in context_docs[:3]])  # Use top 3 docs

        # Create a prompt for the LLM
        prompt = f"Context: {context_str}\n\nQuestion: {request.query}\n\nPlease provide a helpful answer based on the context provided."

        # Get response from LLM
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        query_id = str(uuid.uuid4())

        return QueryResponse(
            answer=answer,
            sources=context_docs,
            query_id=query_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/upload_document", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest):
    try:
        # Initialize Qdrant
        qdrant = QdrantSetup()

        # Generate a document ID
        doc_id = str(uuid.uuid4())

        # Add user ID to metadata
        metadata = request.metadata.copy()
        metadata["user_id"] = request.user_id

        # Store document in Qdrant
        qdrant.store_document(
            doc_id=doc_id,
            content=request.content,
            metadata=metadata
        )

        return DocumentUploadResponse(
            document_id=doc_id,
            status="uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/health")
async def rag_health():
    return {"status": "healthy", "service": "RAG Chatbot"}