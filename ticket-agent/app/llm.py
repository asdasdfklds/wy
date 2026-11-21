from functools import lru_cache

from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
import os


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("LLM_MODEL"),
        temperature=os.getenv("LLM_TEMPERATURE")
    )