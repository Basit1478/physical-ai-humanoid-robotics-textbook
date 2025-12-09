from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

# Import the OpenAI Agents SDK with Gemini from the utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gemini_agent import OpenAI_Agents_Gemini

translate_router = APIRouter()

class TranslateRequest(BaseModel):
    text: str
    source_lang: Optional[str] = "en"
    target_lang: Optional[str] = "ur"

class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

# Initialize the Gemini agent
gemini_agent = OpenAI_Agents_Gemini()

@translate_router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """Translate text from source language to target language using Gemini"""
    try:
        # Create prompt for translation
        prompt = f"""
        Translate the following text from {request.source_lang} to {request.target_lang}:
        
        Text: "{request.text}"
        
        Translation:
        """
        
        # Use Gemini to perform translation
        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate the given text from {request.source_lang} to {request.target_lang}. Return only the translation without any additional explanation."},
            {"role": "user", "content": prompt}
        ]
        
        response_data = gemini_agent.chat_completion(
            messages=messages,
            model="gemini-pro"
        )
        
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response_data['error']}")
        
        translated_text = response_data["choices"][0]["message"]["content"]
        
        return TranslateResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")

@translate_router.post("/urdu", response_model=TranslateResponse)
async def translate_to_urdu(text: str):
    """Specific endpoint to translate English text to Urdu"""
    try:
        # Create prompt for Urdu translation
        prompt = f"Translate the following English text to Urdu: '{text}'"
        
        # Use Gemini to perform translation
        messages = [
            {"role": "system", "content": "You are a professional Urdu translator. Translate the given English text to Urdu. Return only the Urdu translation without any additional explanation."},
            {"role": "user", "content": prompt}
        ]
        
        response_data = gemini_agent.chat_completion(
            messages=messages,
            model="gemini-pro"
        )
        
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response_data['error']}")
        
        translated_text = response_data["choices"][0]["message"]["content"]
        
        return TranslateResponse(
            original_text=text,
            translated_text=translated_text,
            source_lang="en",
            target_lang="ur"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating to Urdu: {str(e)}")