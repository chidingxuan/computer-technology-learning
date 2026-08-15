"""第二课作业测试：只检查本地数据，不联网、不读取真实密钥。"""

import pytest

from prompt_design import (
    PROMPT_VERSION,
    build_generation_options,
    build_request,
    build_support_messages,
)


def test_prompt_version_is_fixed():
    assert PROMPT_VERSION == "support-v1"


def test_build_support_messages():
    messages = build_support_messages("云笔记", "  怎样导出文件？  ")

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1] == {"role": "user", "content": "怎样导出文件？"}
    system_content = messages[0]["content"]
    assert "云笔记" in system_content
    assert "已知" in system_content
    assert "不知道" in system_content
    assert "三句话" in system_content


@pytest.mark.parametrize("product", ["", "   "])
def test_build_support_messages_rejects_empty_product(product):
    with pytest.raises(ValueError, match="产品"):
        build_support_messages(product, "怎样导出文件？")


def test_build_support_messages_rejects_non_string_product():
    with pytest.raises(TypeError, match="产品"):
        build_support_messages(None, "怎样导出文件？")  # type: ignore[arg-type]


@pytest.mark.parametrize("question", ["", "   "])
def test_build_support_messages_rejects_empty_question(question):
    with pytest.raises(ValueError, match="问题"):
        build_support_messages("云笔记", question)


def test_build_support_messages_rejects_non_string_question():
    with pytest.raises(TypeError, match="问题"):
        build_support_messages("云笔记", None)  # type: ignore[arg-type]


@pytest.mark.parametrize("temperature", [0, 0.7, 2])
def test_build_generation_options_accepts_temperature_boundary(temperature):
    assert build_generation_options(temperature, 300) == {
        "temperature": temperature,
        "max_tokens": 300,
    }


@pytest.mark.parametrize("temperature", [-0.1, 2.1])
def test_build_generation_options_rejects_out_of_range_temperature(temperature):
    with pytest.raises(ValueError, match="temperature"):
        build_generation_options(temperature, 300)


@pytest.mark.parametrize("temperature", ["0.7", None])
def test_build_generation_options_rejects_non_numeric_temperature(temperature):
    with pytest.raises(TypeError, match="temperature"):
        build_generation_options(temperature, 300)  # type: ignore[arg-type]


@pytest.mark.parametrize("max_tokens", [0, -1])
def test_build_generation_options_rejects_non_positive_max_tokens(max_tokens):
    with pytest.raises(ValueError, match="max_tokens"):
        build_generation_options(0.2, max_tokens)


@pytest.mark.parametrize("max_tokens", [1.5, True, "300", None])
def test_build_generation_options_rejects_non_integer_max_tokens(max_tokens):
    with pytest.raises(TypeError, match="max_tokens"):
        build_generation_options(0.2, max_tokens)  # type: ignore[arg-type]


def test_build_request_returns_independent_request_data():
    messages = [{"role": "user", "content": "你好"}]
    options = {"temperature": 0.2, "max_tokens": 100}

    request = build_request("demo-model", messages, options)

    assert request == {
        "model": "demo-model",
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": 0.2,
        "max_tokens": 100,
    }
    assert request["messages"] is not messages
    assert request is not options


@pytest.mark.parametrize("model", ["", "   "])
def test_build_request_rejects_empty_model(model):
    with pytest.raises(ValueError, match="模型"):
        build_request(model, [{"role": "user", "content": "你好"}], {})


def test_build_request_rejects_non_string_model():
    with pytest.raises(TypeError, match="模型"):
        build_request(None, [{"role": "user", "content": "你好"}], {})  # type: ignore[arg-type]


def test_build_request_rejects_empty_messages():
    with pytest.raises(ValueError, match="消息"):
        build_request("demo-model", [], {})


@pytest.mark.parametrize("messages", [None, {}, "不是列表"])
def test_build_request_rejects_non_list_messages(messages):
    with pytest.raises(TypeError, match="消息"):
        build_request("demo-model", messages, {})  # type: ignore[arg-type]


@pytest.mark.parametrize("options", [None, [], "不是字典"])
def test_build_request_rejects_non_dict_options(options):
    with pytest.raises(TypeError, match="参数"):
        build_request(
            "demo-model",
            [{"role": "user", "content": "你好"}],
            options,  # type: ignore[arg-type]
        )


def test_build_request_does_not_modify_inputs():
    messages = [{"role": "user", "content": "你好"}]
    options = {"temperature": 0.2}

    build_request("demo-model", messages, options)

    assert messages == [{"role": "user", "content": "你好"}]
    assert options == {"temperature": 0.2}
