from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Physical AI & Humanoid Robotics Book Platform API",
    description="Backend API for educational book with AI features, user authentication, and content personalization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}

# Include routers
from auth.auth_router import router as auth_router
from rag_chatbot.rag_router import router as rag_router
from translate_urdu.translate_router import router as translate_router
from personalize.personalize_router import router as personalize_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(translate_router, prefix="/translate", tags=["translate"])
app.include_router(personalize_router, prefix="/personalize", tags=["personalize"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))