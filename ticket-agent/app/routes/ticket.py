import os

from fastapi import APIRouter

from app.schemas import TicketUpdateRequest
from app.vector_store import get_milvus_store

router = APIRouter()


@router.post("/ticket")
def update_ticket(req: TicketUpdateRequest):
    store = get_milvus_store(os.getenv("MILVUS_TICKET"))
    store.update(req.item_id, req.title, req.description, req.fault_type, req.resolution)
    return True
