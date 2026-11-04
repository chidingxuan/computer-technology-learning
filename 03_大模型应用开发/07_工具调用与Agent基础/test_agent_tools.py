"""学生核心契约测试：只用假模型和假工具，不调用网络或真实业务系统。"""
from copy import deepcopy
import json
import pytest
from agent_tools import execute_call, append_tool_turn, run_agent
from tool_support import AGENT_RULE, sample_call


def assistant(*calls, content=None):
    return {"role": "assistant", "content": content, "tool_calls": list(calls)}


def scripted(replies):
    """教师测试回调：记录每次模型收到的消息快照，按顺序返回固定assistant。"""
    seen = []
    def ask(messages):
        seen.append(deepcopy(messages))
        assert len(seen) <= len(replies), "模型调用超过预期，请检查停止条件与预算"
        return deepcopy(replies[len(seen) - 1])
    return ask, seen


def test_execute_allowed_runs_once():
    calls = []
    def find_room(campus):
        calls.append(campus)
        return {"room_id": "room-a"}
    result = execute_call(sample_call("c1", "find_room", {"campus": "北校区"}),
                          {"find_room": find_room}, {"find_room"})
    assert calls == ["北校区"], "批准的工具应收到解析后的参数，恰好执行一次"
    assert result == {"ok": True, "data": {"room_id": "room-a"}}


def test_execute_unknown_does_not_run():
    def forbidden(**args):
        pytest.fail("未知工具不得执行任何回调")
    result = execute_call(sample_call("c1", "unknown", {}), {"find_room": forbidden}, {"unknown"})
    assert result == {"ok": False, "error": "unknown_tool"}, "不在registry中的名称是未知工具"


def test_execute_registered_but_not_allowed():
    def delete_room(**args):
        pytest.fail("注册不等于获准，禁止的写工具不得运行")
    result = execute_call(sample_call("c1", "delete_room", {}), {"delete_room": delete_room}, set())
    assert result == {"ok": False, "error": "not_allowed"}


def test_execute_bad_arguments_never_reach_tool():
    def get_devices(**args):
        pytest.fail("参数未通过教师校验前不得执行工具")
    for raw in ['not json', '[]', '{"room_id":"room-a","delete":true}']:
        call = sample_call("c1", "get_devices", {})
        call["function"]["arguments"] = raw
        assert execute_call(call, {"get_devices": get_devices}, {"get_devices"}) == {
            "ok": False, "error": "bad_arguments"}, "本课参数契约由validate_arguments检查"


@pytest.mark.parametrize("error_type", [RuntimeError, ValueError])
def test_execute_failure_is_not_missing_business_record(error_type):
    def get_devices(room_id):
        raise error_type("不得泄露的内部错误细节")
    result = execute_call(sample_call("c1", "get_devices", {"room_id": "room-a"}),
                          {"get_devices": get_devices}, {"get_devices"})
    assert result == {"ok": False, "error": "tool_failed"}, "执行失败不能伪装found=False或回显异常全文"


def test_execute_timeout_is_distinct():
    def get_devices(room_id):
        raise TimeoutError("模拟工具自己的超时")
    assert execute_call(sample_call("c1", "get_devices", {"room_id": "room-a"}),
                        {"get_devices": get_devices}, {"get_devices"}) == {
        "ok": False, "error": "tool_timeout"}


def test_execute_not_found_is_successful_query():
    def find_room(campus):
        return {"found": False, "campus": campus}
    call = sample_call("c1", "find_room", {"campus": "不存在校区"})
    before = deepcopy(call)
    result = execute_call(call, {"find_room": find_room}, {"find_room"})
    assert result == {"ok": True, "data": {"found": False, "campus": "不存在校区"}}
    assert call == before, "执行器不能改模型调用字典"


def test_append_keeps_request_before_result():
    history = [{"role": "system", "content": AGENT_RULE}, {"role": "user", "content": "设备？"}]
    message = assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}))
    outcomes = {"c1": {"ok": True, "data": {"count": 20}}}
    result = append_tool_turn(history, message, outcomes)
    assert result[:2] == history and result[2] == message, "必须保留assistant工具请求，再追加结果"
    assert result[3] == {"role": "tool", "tool_call_id": "c1",
                         "content": json.dumps(outcomes["c1"], ensure_ascii=False)}


def test_append_multiple_ids_use_assistant_order():
    message = assistant(sample_call("c2", "get_devices", {"room_id": "room-b"}),
                        sample_call("c1", "get_devices", {"room_id": "room-a"}))
    outcomes = {"c1": {"ok": True, "data": "甲"}, "c2": {"ok": True, "data": "乙"}}
    result = append_tool_turn([], message, outcomes)
    assert [row["tool_call_id"] for row in result[1:]] == ["c2", "c1"], "不能按outcomes字典顺序或工具名配对"
    assert [json.loads(row["content"])["data"] for row in result[1:]] == ["乙", "甲"]


def test_append_error_also_returns_a_matching_tool_message():
    message = assistant(sample_call("blocked", "delete_room", {}), content="我提出一个操作。")
    result = append_tool_turn([], message, {"blocked": {"ok": False, "error": "not_allowed"}})
    assert result[0] == message
    assert result[1]["role"] == "tool" and result[1]["tool_call_id"] == "blocked"
    assert json.loads(result[1]["content"]) == {"ok": False, "error": "not_allowed"}


def test_append_uses_deep_snapshots():
    history = [{"role": "user", "content": "设备？"}]
    message = assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}))
    outcomes = {"c1": {"ok": True, "data": {"count": 20}}}
    before = deepcopy((history, message, outcomes))
    result = append_tool_turn(history, message, outcomes)
    assert (history, message, outcomes) == before, "组装时不能修改输入"
    result[0]["content"] = "改副本"
    result[1]["tool_calls"][0]["function"]["name"] = "改嵌套副本"
    assert (history, message, outcomes) == before, "列表和嵌套工具字典都不能共享可变状态"


def test_run_direct_answer_needs_no_tool():
    ask, seen = scripted([assistant(content="你好，我可以查询只读设备资料。")])
    def mutating_ask(messages):
        reply = ask(messages)
        messages[0]["content"] = "回调改了自己收到的快照"
        return reply
    result = run_agent("你好", mutating_ask, {}, set())
    assert result["status"] == "complete" and result["answer"] == "你好，我可以查询只读设备资料。"
    assert result["model_calls"] == 1 and result["tool_calls"] == 0
    assert seen[0] == [{"role": "system", "content": AGENT_RULE}, {"role": "user", "content": "你好"}]
    assert result["messages"][-1] == assistant(content=result["answer"])
    assert result["messages"][0]["content"] == AGENT_RULE, "ask收到的应是独立快照，不能污染内部历史"


def test_run_zero_budget_never_asks():
    def ask(messages):
        pytest.fail("预算0不能调用模型")
    result = run_agent("查询", ask, {}, set(), max_steps=0)
    assert result == {"status": "step_limit", "answer": "", "model_calls": 0, "tool_calls": 0,
                      "messages": [{"role": "system", "content": AGENT_RULE}, {"role": "user", "content": "查询"}]}


def test_run_single_tool_then_answer():
    request = assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}))
    ask, seen = scripted([request, assistant(content="有20台电脑。")])
    result = run_agent("设备？", ask, {"get_devices": lambda room_id: {"count": 20}}, {"get_devices"}, max_steps=2)
    assert result["status"] == "complete" and result["model_calls"] == 2 and result["tool_calls"] == 1
    assert seen[1][-2] == request and seen[1][-1]["tool_call_id"] == "c1"
    assert json.loads(seen[1][-1]["content"]) == {"ok": True, "data": {"count": 20}}


def test_run_two_dependent_tools():
    request1 = assistant(sample_call("c1", "find_room", {"campus": "北校区"}))
    request2 = assistant(sample_call("c2", "get_devices", {"room_id": "room-a"}))
    ask, seen = scripted([request1, request2, assistant(content="北校区机房有20台电脑。")])
    registry = {"find_room": lambda campus: {"room_id": "room-a"}, "get_devices": lambda room_id: {"count": 20}}
    result = run_agent("北校区设备？", ask, registry, set(registry), max_steps=3)
    assert (result["status"], result["model_calls"], result["tool_calls"]) == ("complete", 3, 2)
    assert json.loads(seen[1][-1]["content"])["data"]["room_id"] == "room-a"
    assert [row["tool_call_id"] for row in seen[2] if row["role"] == "tool"] == ["c1", "c2"]


def test_run_multiple_requests_return_all_results():
    request = assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}),
                        sample_call("c2", "get_devices", {"room_id": "room-b"}))
    ask, seen = scripted([request, assistant(content="两间都有设备。")])
    result = run_agent("设备？", ask, {"get_devices": lambda room_id: {"room_id": room_id}}, {"get_devices"})
    assert result["tool_calls"] == 2 and len(seen) == 2
    assert [row["tool_call_id"] for row in seen[1] if row["role"] == "tool"] == ["c1", "c2"]


def test_run_last_step_does_not_start_unusable_tools():
    request = assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}))
    ask, seen = scripted([request])
    def forbidden(room_id):
        pytest.fail("最后一步已无再次问模型的预算，不启动工具")
    result = run_agent("设备？", ask, {"get_devices": forbidden}, {"get_devices"}, max_steps=1)
    assert (result["status"], result["model_calls"], result["tool_calls"], result["answer"]) == ("step_limit", 1, 0, "")
    assert len(result["messages"]) == 2, "不提交缺少工具结果的半轮assistant请求"


def test_run_repeated_operation_ignores_new_call_id_and_json_spacing():
    first = sample_call("c1", "get_devices", {"room_id": "room-a"})
    second = sample_call("new-id", "get_devices", {})
    second["function"]["arguments"] = '{ "room_id" : "room-a" }'
    ask, seen = scripted([assistant(first), assistant(second)])
    executions = []
    def tool(room_id):
        executions.append(room_id)
        return {"count": 20}
    result = run_agent("设备？", ask, {"get_devices": tool}, {"get_devices"}, max_steps=4)
    assert result["status"] == "repeated_call" and result["answer"] == ""
    assert result["model_calls"] == 2 and result["tool_calls"] == 1 and executions == ["room-a"]
    assert len(result["messages"]) == 4, "重复请求不再执行或提交半轮"


def test_run_same_batch_duplicate_is_blocked_before_any_execution():
    ask, seen = scripted([assistant(sample_call("c1", "get_devices", {"room_id": "room-a"}),
                                    sample_call("c2", "get_devices", {"room_id": "room-a"}))])
    def forbidden(room_id):
        pytest.fail("同批重复也应整批预检，不执行前半批")
    result = run_agent("设备？", ask, {"get_devices": forbidden}, {"get_devices"})
    assert result["status"] == "repeated_call" and result["tool_calls"] == 0
    assert len(result["messages"]) == 2


def test_run_blocked_tool_result_reaches_model():
    ask, seen = scripted([assistant(sample_call("c1", "delete_room", {})), assistant(content="此操作未获准。")])
    def forbidden(**args):
        pytest.fail("模型的请求不能自动批准写操作")
    result = run_agent("删除", ask, {"delete_room": forbidden}, set())
    assert result["status"] == "complete" and result["tool_calls"] == 1
    assert json.loads(seen[1][-1]["content"]) == {"ok": False, "error": "not_allowed"}


def test_run_model_failure_propagates_without_retry():
    for error_type in (TimeoutError, ValueError):
        calls = []
        def ask(messages):
            calls.append(deepcopy(messages))
            raise error_type("模拟模型请求或协议失败")
        with pytest.raises(error_type):
            run_agent("设备？", ask, {}, set())
        assert len(calls) == 1, "模型失败不能改成不知道、complete或自动重试"


def test_run_failed_tool_can_be_reported_not_invented_as_data():
    ask, seen = scripted([assistant(sample_call("c1", "get_devices", {"room_id": "room-a"})),
                          assistant(content="设备查询超时，未获得数量。")])
    def tool(room_id):
        raise TimeoutError("内部详情")
    result = run_agent("设备？", ask, {"get_devices": tool}, {"get_devices"})
    assert result["status"] == "complete" and result["tool_calls"] == 1
    assert json.loads(seen[1][-1]["content"]) == {"ok": False, "error": "tool_timeout"}
