from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter(prefix="/translate")

# Pydantic models
class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = "en"
    target_language: str = "ur"
    user_id: str

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    translation_id: str

class DocumentTranslationRequest(BaseModel):
    content: str  # Markdown content
    user_id: str

class DocumentTranslationResponse(BaseModel):
    translated_content: str
    translation_id: str

# Initialize the LLM with Gemini
def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

@router.post("/text", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        # Validate target language
        if request.target_language != "ur":
            raise HTTPException(status_code=400, detail="Only Urdu translation is supported")

        # Initialize LLM
        llm = get_gemini_llm()

        # Create a prompt for translation
        prompt = f"""
        Translate the following text to Urdu.
        Preserve the meaning and context accurately.
        Keep technical terms in English where appropriate.
        Text to translate: {request.text}
        """

        # Get translation from LLM
        response = llm.invoke(prompt)
        translated_text = response.content if hasattr(response, 'content') else str(response)

        translation_id = str(uuid.uuid4())

        return TranslationResponse(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            translation_id=translation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")

@router.post("/document", response_model=DocumentTranslationResponse)
async def translate_document(request: DocumentTranslationRequest):
    try:
        # Initialize LLM
        llm = get_gemini_llm()

        # Create a prompt for translating Markdown content
        prompt = f"""
        Translate the following Markdown content to Urdu.
        Preserve all Markdown formatting including headers, lists, code blocks, and links.
        Do not translate code blocks or technical terms that should remain in English.
        Maintain the structure and formatting of the document.

        Content to translate:
        {request.content}
        """

        # Get translation from LLM
        response = llm.invoke(prompt)
        translated_content = response.content if hasattr(response, 'content') else str(response)

        translation_id = str(uuid.uuid4())

        return DocumentTranslationResponse(
            translated_content=translated_content,
            translation_id=translation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating document: {str(e)}")

@router.get("/health")
async def translation_health():
    return {"status": "healthy", "service": "Urdu Translation"}

# Additional endpoint for translation status check
@router.get("/status/{translation_id}")
async def get_translation_status(translation_id: str):
    # In a real implementation, this would check the status of a translation job
    # For this example, we'll just return a placeholder
    return {
        "translation_id": translation_id,
        "status": "completed",
        "progress": 100
    }