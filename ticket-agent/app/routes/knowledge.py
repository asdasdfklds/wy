from fastapi import APIRouter

import os
from app.schemas import KnowledgeAddRequest
from app.vector_store import get_milvus_store

router = APIRouter()


@router.post("/knowledge/add")
def add_knowledge(req: KnowledgeAddRequest):
    """
    把 Mysql 新增的运维知识同步到向量数据库
    """
    store = get_milvus_store(os.getenv("MILVUS_KNOWLEDGE"))
    store.insert(req.id, req.title, req.content, req.category)
    return True


@router.delete("/knowledge/{id}")
def delete_knowledge(id: int):
    store = get_milvus_store(os.getenv("MILVUS_KNOWLEDGE"))
    store.delete(id)
    return True

@router.delete("/knowledge/{id}")
def delete_knowledge(id: int):
    store = get_milvus_store(os.getenv("MILVUS_KNOWLEDGE"))
    store.delete(id)
    return True
