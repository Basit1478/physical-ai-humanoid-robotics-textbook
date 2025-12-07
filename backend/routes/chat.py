from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import ChatRequest, ChatResponse, ChatSession
from services.chat_service import rag_service
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Chat endpoint that uses RAG to answer questions about the textbook"""
    try:
        response = rag_service.chat(db, current_user.id, chat_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.post("/chat/start-session", response_model=ChatSession)
def start_chat_session(
    title: str = "New Chat Session",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Start a new chat session"""
    try:
        session = rag_service.create_chat_session(db, current_user.id, title)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chat session: {str(e)}"
        )

@router.get("/chat/sessions/{session_id}/history")
def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get chat history for a specific session"""
    try:
        # Verify user owns this session
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or you don't have access to it"
            )

        history = rag_service.get_session_history(db, session_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.get("/chat/sessions")
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get all chat sessions for the current user"""
    try:
        sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )