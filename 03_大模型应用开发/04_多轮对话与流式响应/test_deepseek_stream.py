"""教师接线模块的离线测试，不调用API、不读取真实密钥。"""
from types import SimpleNamespace

import httpx
import pytest
from openai import APIConnectionError

from deepseek_stream import deepseek_events, make_deepseek_client, request_text_stream


def chunk(text=None, reason=None):
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text), finish_reason=reason)])


class FakeStream:
    def __init__(self, chunks, error=None):
        self.chunks = chunks
        self.error = error
        self.closed = False
        self.read_count = 0

    def __iter__(self):
        for item in self.chunks:
            self.read_count += 1
            yield item
        if self.error is not None:
            raise self.error

    def close(self):
        self.closed = True


def test_adapter_stop_emits_done_and_closes():
    source = FakeStream([chunk("建议"), chunk(" 去西湖", "stop"), chunk("不应读取")])
    info = {}
    assert list(deepseek_events(source, info)) == [
        {"kind": "delta", "text": "建议"}, {"kind": "delta", "text": " 去西湖"}, {"kind": "done"}]
    assert info == {"finish_reason": "stop", "error_type": None}
    assert source.closed and source.read_count == 2


def test_adapter_length_keeps_partial_text_without_done():
    source = FakeStream([chunk("半句", "length")])
    info = {}
    assert list(deepseek_events(source, info)) == [{"kind": "delta", "text": "半句"}]
    assert info["finish_reason"] == "length" and source.closed


@pytest.mark.parametrize("reason", ["content_filter", "insufficient_system_resource", "aborted", "tool_calls", "unknown"])
def test_adapter_non_success_terminal_maps_to_error(reason):
    source = FakeStream([chunk("已有文字"), chunk(reason=reason)])
    assert list(deepseek_events(source))[-1] == {"kind": "error"}
    assert source.closed


def test_adapter_eof_does_not_invent_done():
    source = FakeStream([chunk("未完成")])
    assert list(deepseek_events(source)) == [{"kind": "delta", "text": "未完成"}]
    assert source.closed


def test_adapter_empty_choices_and_empty_text_are_not_completion():
    source = FakeStream([SimpleNamespace(choices=[]), chunk(None), chunk(""), chunk(reason="stop")])
    assert list(deepseek_events(source)) == [
        {"kind": "delta", "text": None}, {"kind": "delta", "text": ""}, {"kind": "done"}]


@pytest.mark.parametrize("error", [
    APIConnectionError(message="SECRET_SHOULD_NOT_APPEAR", request=httpx.Request("GET", "https://example.invalid")),
    httpx.ReadTimeout("SECRET_SHOULD_NOT_APPEAR"),
    httpx.ReadError("SECRET_SHOULD_NOT_APPEAR"),
])
def test_adapter_transport_failure_does_not_expose_error_message(error):
    source = FakeStream([chunk("片段")], error=error)
    info = {}
    assert list(deepseek_events(source, info)) == [{"kind": "delta", "text": "片段"}, {"kind": "error"}]
    assert info == {"finish_reason": None, "error_type": type(error).__name__}
    assert source.closed


def test_adapter_close_after_done_releases_stream_without_reading_tail():
    source = FakeStream([chunk(reason="stop"), chunk("尾部")])
    events = deepseek_events(source)
    assert next(events) == {"kind": "done"}
    events.close()
    assert source.closed and source.read_count == 1


def test_request_is_one_non_thinking_text_stream_with_output_limit():
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return "fake stream"
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    messages = [{"role": "user", "content": "测试"}]
    assert request_text_stream(client, "deepseek-flash", messages, max_tokens=12) == "fake stream"
    assert calls == [{"model": "deepseek-flash", "messages": messages, "stream": True,
                      "max_tokens": 12, "extra_body": {"thinking": {"type": "disabled"}}}]


def test_config_missing_key_has_friendly_message_without_network(tmp_path, monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ValueError, match="未配置密钥"):
        make_deepseek_client(tmp_path / "lesson04")


def test_config_uses_official_model_and_disables_automatic_retries(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "offline-test-key")
    monkeypatch.setenv("DEEPSEEK_MODEL", "legacy-model-not-used")
    client, model = make_deepseek_client(tmp_path / "lesson04")
    try:
        assert model == "deepseek-flash"
        assert str(client.base_url) == "https://api.deepseek.com"
        assert client.max_retries == 0
        assert client.timeout == 30.0
    finally:
        client.close()
