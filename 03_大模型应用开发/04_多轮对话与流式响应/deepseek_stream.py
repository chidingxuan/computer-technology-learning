"""教师提供的接线模块：真实DeepSeek流 → 本课事件；导入不会联网。

学生仍在Notebook与conversation_flow.py完成收集、提交逻辑。
这里只支持单个纯文本回答，不支持工具调用、图片或思考内容拼接。
"""
from collections.abc import Iterator
from pathlib import Path
import os

from dotenv import dotenv_values
from httpx import HTTPError
from openai import OpenAI, OpenAIError


def make_deepseek_client(lesson_dir: Path | None = None) -> tuple[OpenAI, str]:
    """读取密钥，创建客户端；此时不发送请求，不打印配置内容。"""
    folder = Path(lesson_dir) if lesson_dir is not None else Path(__file__).resolve().parent
    local = dotenv_values(folder / ".env")
    shared = dotenv_values(folder.parent / "01_调用真实大模型API" / ".env")
    key = os.getenv("DEEPSEEK_API_KEY") or local.get("DEEPSEEK_API_KEY") or shared.get("DEEPSEEK_API_KEY")
    if not key or key == "replace_with_your_key":
        raise ValueError("未配置密钥：使用第一课.env，或按本课.env.example创建本课.env；不要把密钥贴进Notebook。")
    # 仅共享第一课密钥，不继承旧模型名，也不修改第一课.env或全局环境。
    model = local.get("DEEPSEEK_MODEL") or "deepseek-flash"
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=30.0, max_retries=0)
    return client, model


def request_text_stream(client: OpenAI, model: str, messages: list[dict[str, str]], *, max_tokens: int = 180):
    """真正发出一次付费请求：禁用思考，限制输出，不自动重试。"""
    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        max_tokens=max_tokens,
        extra_body={"thinking": {"type": "disabled"}},
    )


def deepseek_events(stream, diagnostics: dict | None = None) -> Iterator[dict[str, str | None]]:
    """逐项转换SDK对象，正常stop才产生done；退出时关闭上游流。

    diagnostics只存结束原因和异常类型，不存密钥、异常原文或请求正文。
    消费者提前退出时须调用生成器.close()，使finally及时执行。
    """
    info = diagnostics if diagnostics is not None else {}
    info.update(finish_reason=None, error_type=None)
    try:
        try:
            for chunk in stream:
                if not chunk.choices:
                    continue  # 防御兼容接口的非正文事件，不代表完成
                choice = chunk.choices[0]
                content = choice.delta.content
                reason = choice.finish_reason
                if content is not None:
                    yield {"kind": "delta", "text": content}
                elif reason is None:
                    yield {"kind": "delta", "text": None}
                if reason is not None:
                    info["finish_reason"] = reason
                    if reason == "stop":
                        yield {"kind": "done"}
                    elif reason != "length":
                        # 过滤、资源中断、aborted或本课不支持的tool_calls等。
                        yield {"kind": "error"}
                    # length保留正文，但不发done/error，让收集器返回incomplete。
                    return
        except (OpenAIError, HTTPError) as error:
            info["error_type"] = type(error).__name__
            yield {"kind": "error"}
    finally:
        stream.close()
