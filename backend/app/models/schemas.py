from typing import Optional, List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):

    reply: str
    session_id: str
    source_used: List[str] = []