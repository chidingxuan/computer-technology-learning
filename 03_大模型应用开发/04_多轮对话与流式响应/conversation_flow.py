"""第04课作业：三个TODO只操作本地数据，不调用API。"""
from collections.abc import Iterable


def build_request_messages(
    rule: str, history: list[dict[str, str]], question: str, max_turns: int
) -> list[dict[str, str]]:
    """TODO 1：创建包含最近完整轮次的请求快照，具体契约见讲义。"""
    n = min(2*max_turns,len(history))
    ans = []
    ans.append({"role":"system", "content": rule})
    for i in range(len(history)-n, len(history)):
        ans.append(history[i].copy())
    ans.append({"role":"user", "content": question})
    return ans


def collect_stream(events: Iterable[dict[str, str | None]]) -> dict[str, str]:
    """TODO 2：单次消费规范化事件，返回status和text。"""
    terminal = None
    ans = []
    for event in events:
        if event["kind"] == 'delta':
            if event["text"] is not None:
                ans.append(event["text"])
        else:
            terminal = event["kind"]
            break

    if terminal is None:
        return {"status": "incomplete", "text": "".join(ans)}
    elif terminal == "done":
        return {"status": "complete", "text": "".join(ans)}
    else:
        return {"status": "failed", "text": "".join(ans)}


def commit_turn(
    history: list[dict[str, str]], question: str, result: dict[str, str]
) -> list[dict[str, str]]:
    """TODO 3：只将complete且非空的回答保存为完整一轮。"""
    new_history = [message.copy() for message in history]
    if result["status"] == "complete" and result["text"].strip():
        new_history.append({"role": "user", "content": question})
        new_history.append({"role": "assistant", "content": result["text"]})
    return new_history