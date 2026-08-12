"""调用真实大模型API课程作业测试；全程使用假客户端，不访问网络。"""

from types import SimpleNamespace

import pytest

from ai_reply import build_response_request, extract_output_text, generate_reply


@pytest.mark.parametrize(
    ("text", "model", "expected"),
    [
        ("你好", "gpt-test", {"model": "gpt-test", "input": "你好"}),
        ("  解释RAG  ", "  demo-model ", {"model": "demo-model", "input": "解释RAG"}),
    ],
)
def test_build_response_request(text, model, expected):
    assert build_response_request(text, model) == expected


@pytest.mark.parametrize("text", ["", "   "])
def test_rejects_empty_user_text(text):
    with pytest.raises(ValueError, match="用户输入"):
        build_response_request(text, "gpt-test")


@pytest.mark.parametrize("model", ["", "   "])
def test_rejects_empty_model(model):
    with pytest.raises(ValueError, match="模型"):
        build_response_request("你好", model)


def test_extracts_and_strips_output_text():
    response = SimpleNamespace(output_text="  模型回答  ")
    assert extract_output_text(response) == "模型回答"


@pytest.mark.parametrize("response", [SimpleNamespace(), SimpleNamespace(output_text="  ")])
def test_rejects_missing_or_empty_output(response):
    with pytest.raises(ValueError, match="文本"):
        extract_output_text(response)


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="模拟回答")


def test_generate_reply_calls_responses_api_once():
    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)

    result = generate_reply(client, "  什么是向量？ ", " demo-model ")

    assert result == "模拟回答"
    assert responses.calls == [{"model": "demo-model", "input": "什么是向量？"}]
