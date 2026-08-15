"""第03阶段第02课作业：设计提示词、消息和受控参数实验。"""

from typing import Any


PROMPT_VERSION = "support-v1"


def build_support_messages(
    product: str,
    known_information: str,
    question: str,
) -> list[dict[str, str]]:
    """根据产品、已知资料和用户问题构造system、user消息。"""
    # TODO 1：把任务、上下文、约束和输出要求组织进system消息，
    # 再把清理后的用户问题放入user消息。
    raise NotImplementedError


def build_temperature_experiment(
    model: str,
    messages: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """构造只改变temperature的稳定组和多样组请求。"""
    # TODO 2：返回两个请求；除temperature分别为0.2和1.0外，
    # model、messages和max_tokens=300必须保持相同。
    raise NotImplementedError


def build_prompt_test_cases() -> list[dict[str, str]]:
    """返回正常、未知信息、规则冲突三类固定测试样例。"""
    # TODO 3：为normal、unknown、conflict三类情况分别设计
    # question和expected_behavior。
    raise NotImplementedError
