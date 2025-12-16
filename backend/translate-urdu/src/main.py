from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os

app = FastAPI(title="Urdu Translation Service", version="1.0.0")

class TranslateRequest(BaseModel):
    text: str
    source_lang: Optional[str] = "en"
    target_lang: Optional[str] = "ur"

class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    # In a real implementation, you would use a translation model
    # For now, we'll simulate the translation using Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Return a mock translation for demonstration
        return TranslateResponse(
            original_text=request.text,
            translated_text=f"[Mock Urdu translation of: {request.text}]",
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"Translate the following text from {request.source_lang} to {request.target_lang}: {request.text}"
        response = model.generate_content(prompt)

        return TranslateResponse(
            original_text=request.text,
            translated_text=response.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        # Return mock translation in case of error
        return TranslateResponse(
            original_text=request.text,
            translated_text=f"[Mock Urdu translation of: {request.text}]",
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )

@app.get("/")
async def root():
    return {"message": "Urdu Translation Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)