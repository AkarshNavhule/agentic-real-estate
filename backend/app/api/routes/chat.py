from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import ask_real_estate_agent
from fastapi.responses import StreamingResponse
import uuid
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["AI Agent"])
async def process_chat(request: ChatRequest):
    """
    Accepts a user query, triggers the Semantic Kernel agent,
    and returns the AI-generated response using RAG.
    """
    try:

        current_session = request.session_id if request.session_id else str(uuid.uuid4())
        # Call the Semantic Kernel Agent
        ai_reply = await ask_real_estate_agent(request.message, current_session)

        return ChatResponse(
            reply=ai_reply,
            session_id=current_session,
            sources_used=["Azure AI Search - properties-index"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream", tags=["AI Agent"])
async def process_chat_stream(request: ChatRequest):
    try:
        current_session = request.session_id if request.session_id else str(uuid.uuid4())

        # We pass the async generator directly into the StreamingResponse
        return StreamingResponse(
            ask_real_estate_agent(request.message, current_session),
            media_type="text/event-stream",
            headers={"X-Session-ID": current_session}  # Send session ID via headers since we can't send JSON!
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))