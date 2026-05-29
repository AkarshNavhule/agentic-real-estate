from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import ask_real_estate_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["AI Agent"])
async def process_chat(request: ChatRequest):
    """
    Accepts a user query, triggers the Semantic Kernel agent,
    and returns the AI-generated response using RAG.
    """
    try:
        # Call the Semantic Kernel Agent
        ai_reply = await ask_real_estate_agent(request.message)

        return ChatResponse(
            reply=ai_reply,
            sources_used=["Azure AI Search - properties-index"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))