"""第06课作业：FastAPI 应用入口。"""

from contextlib import asynccontextmanager
from pathlib import Path
from collections.abc import AsyncIterator

from fastapi import FastAPI

from . import repository
from .routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用启动时准备默认数据库。"""

    # 在应用开始接收请求前配置并初始化默认数据库。
    db_path = Path(__file__).resolve().parent.parent / "chat.sqlite3"
    repository.configure_database(str(db_path))
    repository.initialize_database()
    yield


app = FastAPI(title="AI聊天后端", lifespan=lifespan)

app.include_router(chat_router)

@app.get("/health")
def health() -> dict[str, str]:
    """健康检查接口已经完成，不需要修改。"""

    return {"status": "ok"}
