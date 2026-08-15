"""第一课作业测试：不联网、不读取真实密钥、不产生API费用。"""

from types import SimpleNamespace

import pytest

from ai_reply import extract_output_text, normalize_question, read_model_name


@pytest.mark.parametrize(
    ("question", "expected"),
    [("什么是API？", "什么是API？"), ("  解释模型和API的区别  ", "解释模型和API的区别")],
)
def test_normalize_question(question, expected):
    assert normalize_question(question) == expected


@pytest.mark.parametrize("question", ["", "   "])
def test_normalize_question_rejects_empty_text(question):
    with pytest.raises(ValueError, match="问题"):
        normalize_question(question)


def test_normalize_question_rejects_non_string():
    with pytest.raises(TypeError, match="字符串"):
        normalize_question(None)  # type: ignore[arg-type]


def test_read_model_name():
    assert read_model_name({"DEEPSEEK_MODEL": "  demo-model  "}) == "demo-model"


@pytest.mark.parametrize("environ", [{}, {"DEEPSEEK_MODEL": ""}, {"DEEPSEEK_MODEL": "   "}])
def test_read_model_name_rejects_missing_or_empty_value(environ):
    with pytest.raises(ValueError, match="DEEPSEEK_MODEL"):
        read_model_name(environ)


def test_extract_output_text():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="  这是模型回答。  "))]
    )
    assert extract_output_text(response) == "这是模型回答。"


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(),
        SimpleNamespace(choices=[]),
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=""))]),
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=None))]),
    ],
)
def test_extract_output_text_rejects_missing_or_empty_text(response):
    with pytest.raises(ValueError, match="文本"):
        extract_output_text(response)
