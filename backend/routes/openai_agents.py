from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import time

from models.database import SessionLocal
from openai_agents.manager import agent_manager
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/openai-agents/create-assistant")
def create_textbook_assistant(
    current_user: User = Depends(get_current_user)
):
    """Create the textbook assistant using OpenAI Agents SDK"""
    try:
        assistant = agent_manager.create_textbook_assistant()
        return {
            "assistant_id": assistant.id,
            "name": assistant.name,
            "model": assistant.model,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assistant: {str(e)}"
        )

@router.post("/openai-agents/chat")
def chat_with_assistant(
    query: str,
    thread_id: str = None,
    module_id: int = None,
    chapter_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Chat with the textbook assistant using OpenAI Agents SDK"""
    try:
        # Create or use existing assistant
        if "textbook_assistant" not in agent_manager.assistants:
            assistant = agent_manager.create_textbook_assistant()
        else:
            assistant = agent_manager.assistants["textbook_assistant"]

        # Create or use existing thread
        if not thread_id:
            thread = agent_manager.create_thread()
            thread_id = thread.id
        else:
            # Verify thread exists
            try:
                agent_manager.client.beta.threads.retrieve(thread_id)
            except Exception:
                thread = agent_manager.create_thread()
                thread_id = thread.id

        # Add user message to thread
        message = agent_manager.add_message_to_thread(thread_id, query)

        # Run the assistant
        run = agent_manager.run_assistant(thread_id, assistant.id)

        # Wait for completion (with timeout)
        max_wait_time = 30  # seconds
        start_time = time.time()

        while run.status not in ["completed", "failed", "cancelled"]:
            if time.time() - start_time > max_wait_time:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Assistant response timed out"
                )

            time.sleep(1)
            run = agent_manager.get_run_status(thread_id, run.id)

        if run.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Assistant run failed: {run.last_error}"
            )

        # Get messages
        messages = agent_manager.get_messages(thread_id)

        # Find the latest assistant message
        assistant_message = None
        for msg in reversed(messages):
            if msg.role == "assistant":
                assistant_message = msg
                break

        if assistant_message:
            # Extract content from the message
            content = ""
            for content_item in assistant_message.content:
                if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                    content += content_item.text.value

            return {
                "response": content,
                "thread_id": thread_id,
                "assistant_id": assistant.id,
                "message_id": assistant_message.id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No response from assistant"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error chatting with assistant: {str(e)}"
        )

@router.get("/openai-agents/thread/{thread_id}/messages")
def get_thread_messages(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all messages from a conversation thread"""
    try:
        # Verify thread exists
        agent_manager.client.beta.threads.retrieve(thread_id)

        # Get messages
        messages = agent_manager.get_messages(thread_id)

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            content = ""
            for content_item in msg.content:
                if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                    content += content_item.text.value

            formatted_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": content,
                "created_at": msg.created_at
            })

        return {
            "thread_id": thread_id,
            "messages": formatted_messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving thread messages: {str(e)}"
        )