"""第04课作业：在这里定义学习任务的 HTTP 路由。"""

from fastapi import APIRouter

from ..schemas import TaskCreate, TaskResponse
from ..services import create_task, list_tasks


# TODO：给这组路由配置作业要求的共同前缀和文档标签。
router = APIRouter(prefix= "/tasks", tags=["tasks"])


# TODO：修改装饰器的路径、成功状态码和响应模型。
@router.post("", status_code=201, response_model= TaskResponse)
def create_task_endpoint(task: TaskCreate) -> TaskResponse:
    """把创建请求交给 services.create_task。"""

    return create_task(task)


# TODO：修改装饰器的路径和响应模型。
@router.get("", status_code = 200,response_model= list[TaskResponse])
def list_tasks_endpoint() -> list[TaskResponse]:
    """把查询请求交给 services.list_tasks。"""

    return list_tasks()
