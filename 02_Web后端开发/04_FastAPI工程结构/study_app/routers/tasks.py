"""第04课作业：在这里定义学习任务的 HTTP 路由。"""

from fastapi import APIRouter

from ..schemas import TaskCreate, TaskResponse
from ..services import create_task, list_tasks


# TODO：给这组路由配置作业要求的共同前缀和文档标签。
router = APIRouter()


# TODO：修改装饰器的路径、成功状态码和响应模型。
@router.post("/TODO-create")
def create_task_endpoint(task: TaskCreate) -> TaskResponse:
    """把创建请求交给 services.create_task。"""

    return create_task(task)


# TODO：修改装饰器的路径和响应模型。
@router.get("/TODO-list")
def list_tasks_endpoint() -> list[TaskResponse]:
    """把查询请求交给 services.list_tasks。"""

    return list_tasks()
