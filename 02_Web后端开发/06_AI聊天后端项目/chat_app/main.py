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

    # TODO 1：
    # 1. 计算本课目录下 chat.sqlite3 的路径；
    # 2. 配置 repository；
    # 3. 初始化数据库；
    # 4. 最后执行 yield，让应用开始处理请求。
    yield


# TODO 2：把标题改成作业规定的标题，并传入 lifespan。
app = FastAPI(title="待完成的聊天应用")

# TODO 3：把 chat_router 挂载到 app。


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查接口已经完成，不需要修改。"""

    return {"status": "ok"}
