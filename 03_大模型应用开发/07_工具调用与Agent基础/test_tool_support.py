"""教师底层离线回归；MockTransport不访问网络。"""
import json
from types import SimpleNamespace
import httpx
from openai import OpenAI
import pytest
from tool_support import (validate_arguments, operation_key, sample_call, normalize_response,
                          request_assistant, LIBRARY_TOOLS, find_branch, get_opening)


def fake_response(content=None, calls=None, finish="stop", refusal=None):
    message = SimpleNamespace(content=content, tool_calls=calls, refusal=refusal)
    return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason=finish)])


def test_validate_returns_decoded_arguments():
    assert validate_arguments("find_room", '{"campus":"北校区"}') == {"campus": "北校区"}


def test_validate_rejects_dangerous_or_bad_shapes():
    for raw in ['bad', '[]', '{"campus":null}', '{"campus":"北","command":"rm"}', '{"campus":""}']:
        with pytest.raises(ValueError, match="bad_arguments"):
            validate_arguments("find_room", raw)


def test_operation_key_compares_operation_not_id():
    a = sample_call("c1", "find_room", {"campus": "北"})
    b = sample_call("c2", "find_room", {})
    b["function"]["arguments"] = '{ "campus" : "北" }'
    assert operation_key(a) == operation_key(b)
    assert operation_key(a) != operation_key(sample_call("c1", "find_room", {"campus": "南"}))


def test_bad_json_operation_still_has_a_key():
    call = sample_call("c1", "find_room", {})
    call["function"]["arguments"] = "bad"
    assert operation_key(call) == "find_room:bad"


def test_normalize_complete_text():
    assert normalize_response(fake_response("你好")) == {"role": "assistant", "content": "你好", "tool_calls": []}


def test_normalize_tool_requests():
    call = SimpleNamespace(id="c1", type="function", function=SimpleNamespace(name="find_room", arguments='{"campus":"北"}'))
    result = normalize_response(fake_response(calls=[call], finish="tool_calls"))
    expected = sample_call("c1", "find_room", {"campus": "北"})
    expected["function"]["arguments"] = '{"campus":"北"}'
    assert result["tool_calls"] == [expected], "SDK适配应保留原始参数字符串，不擅自改写它"
    assert result["content"] is None


def test_normalize_never_executes_truncated_calls():
    call = SimpleNamespace(id="c1", type="function", function=SimpleNamespace(name="find_room", arguments="{"))
    with pytest.raises(ValueError, match="not_complete"):
        normalize_response(fake_response(calls=[call], finish="length"))


def test_normalize_duplicate_ids_rejected():
    call = SimpleNamespace(id="c1", type="function", function=SimpleNamespace(name="find_room", arguments="{}"))
    with pytest.raises(ValueError, match="bad_tool_protocol"):
        normalize_response(fake_response(calls=[call, call], finish="tool_calls"))


def test_normalize_empty_and_refusal_fail():
    with pytest.raises(ValueError, match="not_complete"):
        normalize_response(fake_response(" "))
    with pytest.raises(ValueError, match="refused"):
        normalize_response(fake_response("", refusal="拒绝"))
    with pytest.raises(ValueError, match="empty_response"):
        normalize_response(SimpleNamespace(choices=[]))


def test_local_queries_are_business_data():
    assert find_branch("云城")["branch_id"] == "lib-east"
    assert find_branch("无记录城")["found"] is False
    assert get_opening("lib-east")["closed"] == "周一"


def test_sdk_adapter_sends_tools_and_disabled_thinking():
    requests = []
    def handle(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"id":"fixture", "object":"chat.completion", "created":0, "model":"fixture-model",
            "choices":[{"index":0,"finish_reason":"stop","message":{"role":"assistant","content":"完成"}}],
            "usage":{"prompt_tokens":10,"completion_tokens":2,"total_tokens":12}})
    with OpenAI(api_key="fixture-not-a-real-key", base_url="https://fixture.invalid", max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(handle))) as client:
        message, usage = request_assistant(client, "fixture-model", [{"role":"user","content":"你好"}], LIBRARY_TOOLS, "none")
    assert message["content"] == "完成" and usage["total_tokens"] == 12
    assert requests[0]["thinking"] == {"type":"disabled"}
    assert requests[0]["tool_choice"] == "none" and requests[0]["tools"] == LIBRARY_TOOLS
    assert requests[0]["max_tokens"] == 240 and "response_format" not in requests[0]


def test_sdk_adapter_does_not_retry():
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(503, json={"error":{"message":"fixture unavailable","type":"server_error"}})
    with OpenAI(api_key="fixture-not-a-real-key", base_url="https://fixture.invalid", max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(handle))) as client:
        with pytest.raises(Exception):
            request_assistant(client, "fixture-model", [], LIBRARY_TOOLS)
    assert len(requests) == 1
