"""第04课作业：在这里定义请求和响应数据模型。"""

from pydantic import BaseModel


class TaskCreate(BaseModel):
    """客户端创建学习任务时提交的数据。"""

    # TODO：按照 Notebook 中的“作业数据契约”定义字段和约束。
    pass


class TaskResponse(BaseModel):
    """服务器返回给客户端的完整学习任务数据。"""

    # TODO：按照 Notebook 中的“作业数据契约”定义字段。
    pass
