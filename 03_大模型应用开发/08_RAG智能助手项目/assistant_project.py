"""学生任务：组合既有能力，不重写SDK、检索算法或SQL。完整契约见讲义第4节。"""
from collections.abc import Callable
from project_support import answer_question, run_agent


def run_request(question: str, mode: str, retrieve: Callable, generate: Callable,
                ask: Callable, registry: dict, allowed_names: set,
                max_steps: int = 4) -> dict:
    """仅运行所选路径；返回mode/status/answer/sources/model_calls/tool_calls。"""
    # TODO 1：RAG复用第6课，tool复用第7课；不吞异常，不回传内部messages。
    raise NotImplementedError


def save_exchange(conversation_id: int, question: str, result: dict,
                  save_pair: Callable) -> bool:
    """只有answered/complete且正文非空才提交一对消息；回调自己保证原子事务。"""
    # TODO 2：回调接收(conversation_id, question, answer)，不能拆成两次提交。
    raise NotImplementedError


def evaluate_case(case: dict, result: dict) -> dict:
    """检查冻结的状态/关键文字/来源ID/调用预算；返回case_id/passed/failures。"""
    # TODO 3：输出失败类别的顺序固定为status、answer、sources、budget。
    raise NotImplementedError
