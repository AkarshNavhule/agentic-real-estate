import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import ask_real_estate_agent, ask_real_estate_agent_stream

router = APIRouter()



@router.post("/chat", response_model=ChatResponse, tags=["AI Agent"])
async def process_chat(request: ChatRequest):
    try:
        current_session = request.session_id if request.session_id else str(uuid.uuid4())

        ai_reply = await ask_real_estate_agent(request.message, current_session)

        return ChatResponse(
            reply=ai_reply,
            session_id=current_session,
            sources_used=["Azure AI Search", "SQLite CRM"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/chat/stream", tags=["AI Agent"])
async def process_chat_stream(request: ChatRequest):
    try:
        current_session = request.session_id if request.session_id else str(uuid.uuid4())

        return StreamingResponse(
            ask_real_estate_agent_stream(request.message, current_session),
            media_type="text/event-stream",
            headers={"X-Session-ID": current_session}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))