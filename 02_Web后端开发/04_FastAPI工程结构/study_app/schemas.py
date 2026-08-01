"""第04课作业：在这里定义请求和响应数据模型。"""

from pydantic import BaseModel
from pydantic import Field

class TaskCreate(BaseModel):
    """客户端创建学习任务时提交的数据。"""

    # TODO：按照 Notebook 中的“作业数据契约”定义字段和约束。
    title: str = Field(..., min_length=1, max_length=80)
    priority: int = Field(1, le = 5, ge = 1)


class TaskResponse(BaseModel):
    """服务器返回给客户端的完整学习任务数据。"""

    # TODO：按照 Notebook 中的“作业数据契约”定义字段。
    id: int
    title: str
    priority: int
    completed: bool
