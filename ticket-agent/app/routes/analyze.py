from fastapi import APIRouter
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.agent import run_agent

router = APIRouter()


def _to_items(row: list):
    return [
        SimilarItem(
            id=int(r.get("item_id") or 0),
            title=r.get("title") or "",
            content=r.get("content") or "",
            score=float(r.get("score", 0.0)),
        ) for r in (row or [])
    ]


@router.post("/analyze")
def analyze_ticket(req: AnalyzeRequest):
    """
    接收 SpringBoot发来的工单分析请求，运行 Agent 返回结构话的结果
    """
    print("进入")
    result, similar_tickets_row, similar_knowledge_row = run_agent(req.title, req.description, req.fault_type)
    insert_ticket(req.id, req.title, req.description, result.get("fault_type", "unknown"))
    return AnalyzeResponse(
        fault_type=result.get("fault_type", "unknown"),
        suggestion=result.get("suggestion", ""),
        similar_tickets=_to_items(similar_tickets_row),
        similar_knowledge=_to_items(similar_knowledge_row),
    )
