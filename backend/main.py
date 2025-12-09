from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import Dict, List, Optional

app = FastAPI(title="Textbook Project Backend", version="1.0.0")

# Add CORS middleware to allow communication with Docusaurus frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-applications - import them directly at the module level
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth.auth_api import auth_router
from rag_chatbot.rag_api import rag_router
from translate_urdu.translate_api import translate_router
from personalize.personalize_api import personalize_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(translate_router, prefix="/translate", tags=["translate"])
app.include_router(personalize_router, prefix="/personalize", tags=["personalize"])

@app.get("/")
async def root():
    return {"message": "Textbook Project Backend API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)