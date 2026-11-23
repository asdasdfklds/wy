from fastapi import FastAPI

from dotenv import load_dotenv

load_dotenv()  # 先加载 .env，后面各模块初始化时读到的才是真实配置

from app.routes.analyze import router as analyze_router
from app.routes.knowledge import router as knowledge_router
from app.routes.chat import router as chat_router


import uvicorn

app = FastAPI()
app.include_router(analyze_router)
app.include_router(knowledge_router)
app.include_router(chat_router)

@app.get("/")
def health_check():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
