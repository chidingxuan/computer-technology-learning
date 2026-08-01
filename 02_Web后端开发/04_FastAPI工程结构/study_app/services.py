"""第04课作业：在这里实现业务逻辑。"""

from .schemas import TaskCreate, TaskResponse


_tasks: list[TaskResponse] = []


def reset_tasks() -> None:
    """清空内存数据；测试会在每个测试前调用它。"""

    _tasks.clear()


def create_task(task: TaskCreate) -> TaskResponse:
    """创建一个学习任务并返回完整任务。"""

    # TODO：按照作业契约生成服务器字段、保存任务并返回结果。
    response_task = TaskResponse(
        id = len(_tasks) + 1,
        title = task.title,
        priority= task.priority,
        completed= False
    )
    _tasks.append(response_task)
    return response_task


def list_tasks() -> list[TaskResponse]:
    """返回当前全部学习任务。"""

    # TODO：返回任务列表；注意不要让调用者直接拿到内部列表本身。
    return _tasks.copy()
