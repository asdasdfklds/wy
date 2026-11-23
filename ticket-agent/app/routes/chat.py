from app.chat_agent import run_chat
from app.schemas import ChatRequest, ChatResponse, ToolCallRecord
from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest):
    result = run_chat(req.session_id, req.message)
    return ChatResponse(
        reply=result["reply"],
        tool_calls=[ToolCallRecord(**r) for r in result["tool_calls"]],
        session_id=result["session_id"],
        finished=result["finished"],
    )
