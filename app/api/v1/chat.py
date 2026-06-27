from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.rag.rag_engine import chat

router = APIRouter(prefix="/chat", tags=["chat"])


class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[Message] = []


class ChatResponse(BaseModel):
    answer: str


@router.post("/", response_model=ChatResponse)
def ask(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    answer = chat(request.question, history, db)
    return ChatResponse(answer=answer)