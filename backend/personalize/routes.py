from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from ..qdrant_setup import QdrantSetup

router = APIRouter(prefix="/personalize")

# Pydantic models
class PersonalizationRequest(BaseModel):
    content: str
    user_id: str
    user_background: Dict[str, Any]  # Contains software_background, hardware_background, etc.
    content_type: Optional[str] = "text"  # "text", "markdown", "chapter"

class PersonalizationResponse(BaseModel):
    personalized_content: str
    adjustments_made: list
    personalization_id: str

class ContentPersonalizationRequest(BaseModel):
    original_content: str
    user_background: Dict[str, Any]
    chapter_id: Optional[str] = None
    user_id: str

class ContentPersonalizationResponse(BaseModel):
    personalized_content: str
    adjustments_made: list
    personalization_id: str

# Initialize the LLM with Gemini
def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

@router.post("/content", response_model=PersonalizationResponse)
async def personalize_content(request: PersonalizationRequest):
    try:
        # Initialize LLM
        llm = get_gemini_llm()

        # Extract user background information
        software_background = request.user_background.get("software_background", "beginner")
        hardware_background = request.user_background.get("hardware_background", "beginner")

        # Create a prompt for personalization based on user background
        prompt = f"""
        Personalize the following content based on the user's background:
        - Software Background: {software_background}
        - Hardware Background: {hardware_background}

        Adjust the content to be appropriate for their experience level:
        - For beginners: Add more explanations, examples, and step-by-step guidance
        - For intermediate: Provide balanced explanations with some advanced concepts
        - For advanced: Include more complex examples and assume deeper understanding

        Original content: {request.content}

        Return the personalized content that matches their background level.
        """

        # Get personalized content from LLM
        response = llm.invoke(prompt)
        personalized_content = response.content if hasattr(response, 'content') else str(response)

        # Determine adjustments made based on background
        adjustments = []
        if "beginner" in software_background.lower() or "beginner" in hardware_background.lower():
            adjustments = ["Added more explanations", "Simplified complex concepts", "Added step-by-step guidance"]
        elif "advanced" in software_background.lower() or "advanced" in hardware_background.lower():
            adjustments = ["Added advanced examples", "Assumed deeper understanding", "Included complex concepts"]
        else:
            adjustments = ["Balanced explanations", "Moderate complexity examples"]

        personalization_id = str(uuid.uuid4())

        return PersonalizationResponse(
            personalized_content=personalized_content,
            adjustments_made=adjustments,
            personalization_id=personalization_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error personalizing content: {str(e)}")

@router.post("/chapter", response_model=ContentPersonalizationResponse)
async def personalize_chapter(request: ContentPersonalizationRequest):
    try:
        # Initialize LLM
        llm = get_gemini_llm()

        # Extract user background information
        software_background = request.user_background.get("software_background", "beginner")
        hardware_background = request.user_background.get("hardware_background", "beginner")

        # Create a prompt for personalizing chapter content
        prompt = f"""
        Personalize the following book chapter content based on the user's background:
        - Software Background: {software_background}
        - Hardware Background: {hardware_background}

        Adjust the chapter to be appropriate for their experience level:
        - For beginners: Add more explanations, practical examples, and foundational concepts
        - For intermediate: Provide balanced explanations with some advanced concepts and applications
        - For advanced: Include more complex examples, assume deeper understanding, add advanced applications

        Consider their background when choosing relevant examples:
        - If they have software background, include more software-related examples
        - If they have hardware background, include more hardware-related examples
        - If they have both, balance the examples appropriately

        Original chapter content: {request.original_content}

        Return the personalized chapter content that matches their background level while preserving the structure and key information.
        """

        # Get personalized content from LLM
        response = llm.invoke(prompt)
        personalized_content = response.content if hasattr(response, 'content') else str(response)

        # Determine adjustments made based on background
        adjustments = []
        if "beginner" in software_background.lower() or "beginner" in hardware_background.lower():
            adjustments = [
                "Added foundational explanations",
                "Simplified complex concepts",
                "Added step-by-step examples",
                "Included more context for beginners"
            ]
        elif "advanced" in software_background.lower() or "advanced" in hardware_background.lower():
            adjustments = [
                "Added advanced examples",
                "Assumed deeper understanding",
                "Included complex applications",
                "Added expert-level insights"
            ]
        else:
            adjustments = [
                "Balanced explanations for intermediate level",
                "Moderate complexity examples",
                "Appropriate context for mixed experience levels"
            ]

        personalization_id = str(uuid.uuid4())

        return ContentPersonalizationResponse(
            personalized_content=personalized_content,
            adjustments_made=adjustments,
            personalization_id=personalization_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error personalizing chapter: {str(e)}")

@router.get("/health")
async def personalization_health():
    return {"status": "healthy", "service": "Personalization Service"}

# Get user background for personalization
@router.get("/user-background/{user_id}")
async def get_user_background(user_id: str):
    try:
        # Get user background from Qdrant
        qdrant = QdrantSetup()
        user_data = qdrant.get_user_background(user_id)

        if not user_data:
            raise HTTPException(status_code=404, detail="User background not found")

        return {
            "user_id": user_data.get("user_id"),
            "software_background": user_data.get("software_background"),
            "hardware_background": user_data.get("hardware_background")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user background: {str(e)}")