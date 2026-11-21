from fastapi import APIRouter
from app.schemas import AnalyzeRequest
from app.agent import run_agent

router = APIRouter()

@router.post("/analyze")
def analyze_ticket(req: AnalyzeRequest):

    #调用ai agent分析
    result = run_agent(req.ticket, req.description, req.fault_type)
