from fastapi import APIRouter, HTTPException, Depends
from .models import ChatQueryRequest, ChatQueryResponse, EmbedContentRequest, EmbedContentResponse
from .qdrant_client import qdrant_service
from .gemini_client import gemini_service
from typing import List
import uuid

router = APIRouter()

@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """Handle chat queries with RAG"""
    try:
        # Generate embedding for the query
        query_vector = gemini_service.embed_content(request.question)

        # Search for relevant content in Qdrant
        search_results = qdrant_service.search_content(query_vector, limit=5)

        # Build context from search results
        context_parts = []
        sources = []
        for result in search_results:
            context_parts.append(result["content"])
            sources.append(result["metadata"].get("section_title", "Unknown"))

        # Combine retrieved context with user-provided context
        full_context = "\n\n".join(context_parts)
        if request.context:
            full_context = f"User provided context: {request.context}\n\nRetrieved context: {full_context}"

        # Build the prompt for Gemini
        prompt = f"""
        You are an AI assistant for a Physical AI & Humanoid Robotics textbook.
        Use the following context to answer the user's question.
        If the context doesn't contain enough information, say so.

        Context: {full_context}

        Question: {request.question}

        Answer:
        """

        # Generate response using Gemini
        answer = gemini_service.generate_response(prompt)

        # Generate or use conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        return ChatQueryResponse(
            answer=answer,
            sources=sources,
            confidence=0.8,  # Placeholder confidence score
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/embed-content", response_model=EmbedContentResponse)
async def embed_content(request: EmbedContentRequest):
    """Embed and store content in Qdrant"""
    try:
        # Generate embedding for the content
        vector = gemini_service.embed_content(request.content)

        # Prepare metadata
        metadata = {
            "chapter_id": request.chapter_id,
            "chapter_title": request.chapter_title,
            "section_title": request.section_title,
            "page_url": request.page_url
        }

        # Generate content ID
        content_id = str(uuid.uuid4())

        # Store in Qdrant
        qdrant_service.add_point(
            content_id=content_id,
            vector=vector,
            text=request.content,
            metadata=metadata
        )

        return EmbedContentResponse(
            success=True,
            content_id=content_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error embedding content: {str(e)}")

@router.get("/health")
async def rag_health():
    """Health check for RAG service"""
    return {"status": "healthy", "service": "rag-chatbot"}