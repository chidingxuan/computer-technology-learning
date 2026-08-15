"""第03阶段第02课作业：构造可复用、可测试的提示词请求。"""

from typing import Any


PROMPT_VERSION = "support-v1"


def build_support_messages(product: str, question: str) -> list[dict[str, str]]:
    """为客服问答构造system和user两条消息。"""
    # TODO 1：检查并清理product和question，然后构造两条消息。
    raise NotImplementedError


def build_generation_options(temperature: int | float, max_tokens: int) -> dict[str, Any]:
    """检查模型参数并返回可传给SDK的关键字参数字典。"""
    # TODO 2：temperature必须在0到2之间，max_tokens必须是正整数。
    raise NotImplementedError


def build_request(
    model: str,
    messages: list[dict[str, str]],
    options: dict[str, Any],
) -> dict[str, Any]:
    """组合模型名称、消息和生成参数，不发送网络请求。"""
    # TODO 3：检查model、messages和options，再返回一个新的请求字典。
    raise NotImplementedError
