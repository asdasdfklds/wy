
from typing import List, Optional

from pydantic import BaseModel,Field

# 工单分析入参
class AnalyzeRequest(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    fault_type: Optional[str] = Field(None)


# 新增知识库入参
class KnowledgeAddRequest(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    category: Optional[str] = Field(None)
    content: str = Field(...)

class SimilarItem(BaseModel):
    id: int
    title: str
    content: str
    score: float

class AnalyzeResponse(BaseModel):
    fault_type: str = Field(...)
    suggestion: str = Field(...)
    similar_tickets: List[SimilarItem] = Field(default_factory=list)
    similar_knowledge: List[SimilarItem] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """
    自然语言对话请求

    教学要点：
    - sessionId 用于关联多轮上下文；前端用 uuid 或时间戳即可
    - 不带任何身份参数：Agent 统一用 .env 里的服务账号身份访问后端
    """
    session_id: str = Field(..., description="会话 ID")
    message: str   = Field(..., description="用户输入")


class ToolCallRecord(BaseModel):
    """一次工具调用的展示记录（前端要据此渲染 loading / 表格 / 确认弹窗）"""
    tool: str = Field(..., description="工具名")
    args: dict = Field(default_factory=dict, description="工具入参")
    result_preview: str = Field("", description="工具结果摘要，最多 200 字")
    needs_confirm: bool = Field(
        False,
        description="是否需要前端弹窗确认（仅 create/update 类写工具会为 true）",
    )
    success: bool = Field(True, description="工具是否执行成功")


class ChatResponse(BaseModel):
    """对话响应"""
    reply: str = Field(..., description="最终给用户看的回复")
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    session_id: str = Field(..., description="回传 sessionId")
    finished: bool = Field(True, description="是否正常结束；False 表示出错降级")


class TicketUpdateRequest(BaseModel):
    item_id: int = Field(...)
    title: str = Field(...)
    fault_type: Optional[str] = Field(None)
    description: str = Field(...)
    resolution:str = Field(...)