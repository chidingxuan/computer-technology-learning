"""第03阶段第01课作业：准备一次模型API调用所需的数据。"""

from collections.abc import Mapping
from typing import Any


def normalize_question(question: str) -> str:
    """返回去除首尾空白后的问题；空问题抛出 ValueError。"""
    # TODO 1：先检查类型，再去除首尾空白，最后拒绝空字符串。
    if not isinstance(question, str):
        raise TypeError("字符串")

    if not question.strip():
        raise ValueError("问题")

    return question.strip()


def read_model_name(environ: Mapping[str, str]) -> str:
    """从环境变量映射读取非空的 DEEPSEEK_MODEL。"""
    # TODO 2：读取 DEEPSEEK_MODEL，去除首尾空白；缺失或为空时抛 ValueError。
    if "DEEPSEEK_MODEL" not in environ:
        raise ValueError("没有DEEPSEEK_MODEL")

    model_name = environ["DEEPSEEK_MODEL"]
    if model_name is None or not model_name.strip():
        raise ValueError("没有DEEPSEEK_MODEL")
    return model_name.strip()

def extract_output_text(response: Any) -> str:
    """读取 Chat Completions 响应中的非空文本。"""
    # TODO 3：读取 response.choices[0].message.content，检查并清理；无文本时抛 ValueError。
    try:
        ans = response.choices[0].message.content
    except:
        raise ValueError("文本")

    if not isinstance(ans,str) or not ans.strip():
        raise ValueError("文本")

    return ans.strip()