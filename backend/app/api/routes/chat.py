from fastapi import APIRouter

from app.models.schemas import ChatResponse, ChatRequest

router = APIRouter()
@router.post("/chat" , response_model=ChatResponse , tags=["AI Agent"])
async def chat(request: ChatRequest):
    dummy_reply = "Hello World"

    return ChatResponse(
        reply=dummy_reply,
        source_used=["Mock data"]
    )