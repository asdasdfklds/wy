
from typing import Optional

from pydantic import BaseModel,Field


class AnalyzeRequest(BaseModel):
    ticket: str = Field(...)
    description: str = Field(...)
    fault_type:Optional[str] =Field(None)