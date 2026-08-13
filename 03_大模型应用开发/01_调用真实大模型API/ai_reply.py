"""第03阶段第01课作业：准备一次模型API调用所需的数据。"""

from collections.abc import Mapping
from typing import Any


def normalize_question(question: str) -> str:
    """返回去除首尾空白后的问题；空问题抛出 ValueError。"""
    # TODO 1：先检查类型，再去除首尾空白，最后拒绝空字符串。
    raise NotImplementedError


def read_model_name(environ: Mapping[str, str]) -> str:
    """从环境变量映射读取非空的 OPENAI_MODEL。"""
    # TODO 2：读取 OPENAI_MODEL，去除首尾空白；缺失或为空时抛 ValueError。
    raise NotImplementedError


def extract_output_text(response: Any) -> str:
    """读取响应对象的非空 output_text。"""
    # TODO 3：读取 output_text，确认它是字符串并去除首尾空白；无文本时抛 ValueError。
    raise NotImplementedError
