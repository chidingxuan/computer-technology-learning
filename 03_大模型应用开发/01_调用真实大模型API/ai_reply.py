"""第03阶段第01课作业：封装一次可测试的大模型文本请求。"""

from typing import Any


def build_response_request(user_text: str, model: str) -> dict[str, str]:
    """校验输入并生成 Responses API 的核心请求参数。"""
    # TODO 1：去除两项输入首尾空白，拒绝空值，并返回 model/input 字典。
    raise NotImplementedError


def extract_output_text(response: Any) -> str:
    """从 SDK 响应对象取得非空的 output_text。"""
    # TODO 2：读取 response.output_text，去除首尾空白；缺失或为空时抛 ValueError。
    raise NotImplementedError


def generate_reply(client: Any, user_text: str, model: str) -> str:
    """调用注入的客户端并返回模型文本；本函数不读取环境变量。"""
    # TODO 3：组合前两个函数，并调用 client.responses.create(**request)。
    raise NotImplementedError
