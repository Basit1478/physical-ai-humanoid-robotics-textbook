from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
import uuid

# Import the OpenAI Agents SDK with Gemini from the utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gemini_agent import OpenAI_Agents_Gemini

rag_router = APIRouter()

# Initialize Qdrant client
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.1Vld8KV9xc7_MQzD_1EnbekB1G8t7sjaj3NNV9pXPNg")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBGyEFjjE4QJO2rCRvFiDZrnHnvkdhknhY")

# Initialize Qdrant client
if QDRANT_API_KEY:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    qdrant_client = QdrantClient(url=QDRANT_URL)

# Initialize the Gemini agent
gemini_agent = OpenAI_Agents_Gemini()

# Check if collection exists, create it if it doesn't
def ensure_collection_exists():
    try:
        qdrant_client.get_collection("documents")
    except:
        try:
            qdrant_client.create_collection(
                collection_name="documents",
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
        except Exception as e:
            print(f"Warning: Could not create Qdrant collection: {e}")
            print("Make sure Qdrant is running at the specified URL")

def create_embedding(text: str) -> List[float]:
    """
    Create a simple embedding using a hash-based approach.
    In production, replace this with proper embedding model like SentenceTransformer.
    """
    # Create a simple embedding by hashing the text and converting to vector
    hash_object = hashlib.md5(text.encode())
    hex_dig = hash_object.hexdigest()

    # Convert hex to float vector (simplified approach)
    embedding = []
    for i in range(0, len(hex_dig), 2):
        if i + 1 < len(hex_dig):
            byte_val = int(hex_dig[i:i+2], 16)
            normalized_val = (byte_val / 255.0) * 2 - 1  # Normalize to [-1, 1]
            embedding.append(normalized_val)

    # Pad or truncate to desired size (384)
    while len(embedding) < 384:
        embedding.append(0.0)
    embedding = embedding[:384]

    return embedding

class Document(BaseModel):
    id: Optional[str] = None
    content: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    results: List[Dict]
    answer: str

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict]

@rag_router.post("/documents")
async def add_document(document: Document):
    """Add a document to the Qdrant vector database"""
    try:
        # Ensure collection exists
        ensure_collection_exists()

        # Generate embedding for the document content
        embedding = create_embedding(document.content)

        # Create document ID if not provided
        doc_id = document.id or str(uuid.uuid4())

        # Prepare metadata
        metadata = {"content": document.content}  # Store content in metadata

        # Upsert document to Qdrant
        qdrant_client.upsert(
            collection_name="documents",
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "content": document.content,
                        "metadata": metadata
                    }
                )
            ]
        )

        return {
            "id": doc_id,
            "status": "document added",
            "message": "Document successfully added to vector database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@rag_router.post("/query")
async def query_documents(request: QueryRequest):
    """Query documents from the vector database"""
    try:
        # Ensure collection exists
        ensure_collection_exists()

        # Generate embedding for the query
        query_embedding = create_embedding(request.query)

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=request.top_k
        )

        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "content": result.payload.get("content", ""),
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            })

        return {
            "query": request.query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

@rag_router.post("/chat")
async def chat_with_rag(request: ChatRequest):
    """Chat with RAG - query documents and generate response using Gemini"""
    try:
        # Ensure collection exists
        ensure_collection_exists()

        # First, query relevant documents
        query_embedding = create_embedding(request.query)

        search_results = qdrant_client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=request.top_k
        )

        # Format retrieved documents as context
        context_texts = []
        sources = []
        for result in search_results:
            content = result.payload.get("content", "")
            context_texts.append(content)
            sources.append({
                "id": result.id,
                "content": content,
                "metadata": result.payload.get("metadata", {}),
                "score": result.score
            })

        # Create context string
        context_str = "\n\n".join(context_texts)

        # Prepare the prompt for Gemini
        if context_str:
            prompt = f"""
            Use the following context to answer the question:

            Context: {context_str}

            Question: {request.query}

            Answer:
            """
        else:
            # If no context found, answer based on general knowledge
            prompt = f"""
            Answer the following question:

            Question: {request.query}

            Answer:
            """

        # Prepare messages for Gemini
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides accurate and concise answers based on the provided context. If the context doesn't contain the information needed to answer the question, say so."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Get response from Gemini
        response_data = gemini_agent.chat_completion(
            messages=messages,
            model="gemini-pro"
        )

        if "error" in response_data:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response_data['error']}")

        answer = response_data["choices"][0]["message"]["content"]

        return ChatResponse(
            query=request.query,
            answer=answer,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")

@rag_router.get("/collections")
async def get_collections():
    """Get list of collections in Qdrant"""
    try:
        collections = qdrant_client.get_collections()
        return {"collections": [collection.name for collection in collections.collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting collections: {str(e)}")

@rag_router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the Qdrant vector database"""
    try:
        qdrant_client.delete(
            collection_name="documents",
            points_selector=models.PointIdsList(
                points=[doc_id]
            )
        )
        return {
            "id": doc_id,
            "status": "document deleted",
            "message": "Document successfully deleted from vector database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@rag_router.get("/health")
async def health_check():
    """Health check for the RAG service"""
    try:
        # Test Qdrant connection
        collections = qdrant_client.get_collections()
        qdrant_status = "healthy"
    except Exception:
        qdrant_status = "unhealthy"

    return {
        "status": "healthy",
        "qdrant": qdrant_status,
        "gemini_api_key_set": bool(GEMINI_API_KEY)
    }