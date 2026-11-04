"""学生作业：只补3个TODO；输入输出以Notebook第4节为准。

call是协议字典，arguments是JSON字符串；ask/registry中的值是函数，不是SDK对象。
参数校验和操作签名由教师函数提供，不在本课重复实现通用类型判断。
"""
from collections.abc import Callable
from copy import deepcopy
import json
from tool_support import AGENT_RULE, validate_arguments, operation_key


def execute_call(call: dict, registry: dict[str, Callable], allowed_names: set[str]) -> dict:
    """白名单执行一次工具；返回ok/data或ok/error，不让模型名直接变为Python执行权限。"""
    # TODO
    name = call["function"]['name']
    if name not in registry:
        return {"ok": False, "error": "unknown_tool"}

    if name not in allowed_names:
        return {"ok": False, "error": "not_allowed"}

    try:
        arg = validate_arguments(name, call['function']['arguments'])
    except ValueError:
        return {"ok": False, "error": "bad_arguments"}

    try:
        data = registry[name](**arg)
    except TimeoutError:
        return {"ok": False, "error": "tool_timeout"}
    except Exception:
        return {"ok": False, "error": "tool_failed"}

    return {"ok": True, "data": data}



def append_tool_turn(messages: list[dict], assistant_message: dict, outcomes: dict[str, dict]) -> list[dict]:
    """返回嵌套副本：原消息＋assistant调用请求＋每个ID对应的tool消息。"""
    # TODO
    new_message = deepcopy(messages)
    new_message.append(deepcopy(assistant_message))

    for call in assistant_message['tool_calls']:
        id = call['id']
        new_message.append({
            'role': 'tool',
            'tool_call_id': id,
            'content': json.dumps(outcomes[id],ensure_ascii=False)
        })

    return new_message



def run_agent(question: str, ask: Callable, registry: dict[str, Callable],
              allowed_names: set[str], max_steps: int = 4) -> dict:
    """有限循环；max_steps是模型调用上限，全部停止/计数/消息契约见第4.3节。"""
    # TODO
    message = [
        {'role': 'system', 'content': AGENT_RULE},
        {'role': 'user', 'content': question}
    ]

    model_call = 0
    tool_call = 0
    seen_operations = set()

    for _ in range(max_steps):
        reply = ask(deepcopy(message))
        model_call += 1
        calls = reply["tool_calls"]

        if not calls:
            message.append(deepcopy(reply))

            return {
                'status': 'complete',
                'answer': reply['content'],
                'messages': message,
                'model_calls': model_call,
                'tool_calls':tool_call
            }

        if model_call >= max_steps:
            return{
                'status': 'step_limit',
                'answer': "",
                "messages": message,
                'model_calls': model_call,
                'tool_calls': tool_call
            }
        batch_operations = set()

        for call in calls:
            key = operation_key(call)

            if key in seen_operations or key in batch_operations:
                return {
                    "status": "repeated_call",
                    "answer": "",
                    "messages": message,
                    "model_calls": model_call,
                    "tool_calls": tool_call,
                }

            batch_operations.add(key)
        outcomes = {}

        for call in calls:
            result = execute_call(call, registry, allowed_names)
            outcomes[call["id"]] = result
            tool_call += 1

        message = append_tool_turn(message, reply, outcomes)
        seen_operations.update(batch_operations)

    return {
        "status": "step_limit",
        "answer": "",
        "messages": message,
        "model_calls": model_call,
        "tool_calls": tool_call,
    }
