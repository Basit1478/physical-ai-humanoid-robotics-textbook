from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.qdrant_setup import QdrantSetup
from auth import auth_router
from backend.rag_chatbot import rag_router  # Using underscore version
from backend.translate_urdu import translation_router  # Using underscore version
from backend.personalize import personalize_router

# Create FastAPI app
app = FastAPI(
    title="Textbook Backend API",
    description="Backend API for the textbook project with RAG, translation, and personalization features",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(rag_router, tags=["RAG Chatbot"])
app.include_router(translation_router, tags=["Translation"])
app.include_router(personalize_router, tags=["Personalization"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Textbook Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify all services are running"""
    try:
        # Test Qdrant connection
        qdrant = QdrantSetup()
        # This will raise an exception if Qdrant is not accessible
        qdrant.client.get_collections()

        return {
            "status": "healthy",
            "services": {
                "api": "running",
                "qdrant": "connected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": f"Qdrant connection failed: {str(e)}"
        }

@app.on_event('startup')
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize Qdrant connection
        qdrant = QdrantSetup()
        print("Qdrant connection established successfully")
    except Exception as e:
        print(f"Error initializing Qdrant: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )