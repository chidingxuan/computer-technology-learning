"""第04课作业：学习任务 API 的应用入口。"""

from fastapi import FastAPI

from .routers.tasks import router as tasks_router


# TODO：把应用标题修改为作业规定的文字。
app = FastAPI(title="学习任务 API")

# TODO：把 tasks_router 挂载到主应用；不要在这里重新编写任务路由。
app.include_router(tasks_router)

@app.get("/health")
def health() -> dict[str, str]:
    """健康检查接口已经给出，不需要修改。"""

    return {"status": "ok"}
