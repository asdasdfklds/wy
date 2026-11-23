
from typing import List, Optional

from pydantic import BaseModel,Field

# 工单分析入参
class AnalyzeRequest(BaseModel):
    ticket: str = Field(...)
    description: str = Field(...)
    fault_type:Optional[str] =Field(None)

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


