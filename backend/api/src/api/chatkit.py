"""
Chat API endpoint.

Provides a single POST endpoint for chat interface.
Handles SSE (Server-Sent Events) streaming responses.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict
import json

from ..chatkit import chat_service
from ..api.deps import get_current_user


router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_id: Optional[int] = None
    language: Optional[str] = "en"  # Language preference: 'en', 'ur', etc.


@router.post("/chatkit")
async def chat_endpoint(
    request: ChatRequest,
    current_user: Dict[str, any] = Depends(get_current_user)
):
    """
    Chat endpoint with streaming support.

    Handles conversational task management through AI assistant.
    Streams responses using Server-Sent Events (SSE).

    Authentication:
        Requires valid JWT token in Authorization header

    Request Body:
        {
            "message": "Add a task to buy groceries",
            "conversation_id": 123  // Optional
        }

    Response:
        Server-Sent Events stream with format:
        data: {"content": "chunk", "done": false}
        data: {"content": "", "done": true, "conversation_id": 123}

    Example:
        POST /api/chatkit
        Headers:
            Authorization: Bearer <jwt_token>
        Body:
            {
                "message": "Show me all my tasks"
            }

    Returns:
        StreamingResponse with text/event-stream
    """
    try:
        async def event_generator():
            """Generate SSE events from chat service."""
            async for chunk in chat_service.process_message(
                user_id=current_user["user_id"],
                message=request.message,
                conversation_id=request.conversation_id,
                language=request.language
            ):
                # Format as SSE
                yield f"data: {json.dumps(chunk)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
