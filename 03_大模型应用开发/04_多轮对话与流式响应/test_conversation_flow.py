"""第04课：18项离线测试，分别检查请求快照、流状态与历史提交。"""
from copy import deepcopy

from conversation_flow import build_request_messages, collect_stream, commit_turn

HISTORY = [
    {"role": "user", "content": "如何导出？"},
    {"role": "assistant", "content": "点击导出。"},
    {"role": "user", "content": "支持什么格式？"},
    {"role": "assistant", "content": "支持PDF。"},
]


def test_request_first_turn_has_rule_and_current_question():
    assert build_request_messages("客服规则", [], "如何登录？", 2) == [
        {"role": "system", "content": "客服规则"},
        {"role": "user", "content": "如何登录？"},
    ]


def test_request_retains_latest_complete_turn_in_order():
    assert build_request_messages("客服规则", HISTORY, "还有吗？", 1) == [
        {"role": "system", "content": "客服规则"}, *HISTORY[-2:],
        {"role": "user", "content": "还有吗？"},
    ]


def test_request_zero_turns_keeps_rule_and_question():
    assert len(build_request_messages("规则", HISTORY, "新问题", 0)) == 2


def test_request_large_limit_keeps_all_available_history():
    assert build_request_messages("规则", HISTORY, "新问题", 9)[1:-1] == HISTORY


def test_request_question_appears_once_even_with_same_old_text():
    history = [{"role": "user", "content": "再讲讲"}, {"role": "assistant", "content": "好的"}]
    result = build_request_messages("规则", history, "再讲讲", 1)
    assert result == [{"role": "system", "content": "规则"}, *history,
                      {"role": "user", "content": "再讲讲"}]


def test_request_is_a_snapshot_not_shared_message_dicts():
    source = deepcopy(HISTORY)
    original = deepcopy(source)
    result = build_request_messages("规则", source, "新问题", 2)
    assert source == original, "构造请求不得修改已保存历史"
    result[1]["content"] = "修改请求"
    assert source == original, "请求中的历史字典不得与原历史共享"


def test_stream_joins_delta_in_order_and_marks_done():
    assert collect_stream(iter([
        {"kind": "delta", "text": "请"}, {"kind": "delta", "text": "登录。"},
        {"kind": "done"},
    ])) == {"status": "complete", "text": "请登录。"}


def test_stream_ignores_none_and_empty_delta_without_stripping_spaces():
    assert collect_stream(iter([
        {"kind": "delta", "text": None}, {"kind": "delta", "text": ""},
        {"kind": "delta", "text": " A"}, {"kind": "delta", "text": " B "},
        {"kind": "done"},
    ])) == {"status": "complete", "text": " A B "}


def test_stream_eof_without_done_is_incomplete():
    assert collect_stream(iter([])) == {"status": "incomplete", "text": ""}
    assert collect_stream(iter([{"kind": "delta", "text": "半句"}])) == {
        "status": "incomplete", "text": "半句",
    }


def test_stream_explicit_error_keeps_partial_text():
    assert collect_stream(iter([
        {"kind": "delta", "text": "已有片段"}, {"kind": "error"},
        {"kind": "done"},
    ])) == {"status": "failed", "text": "已有片段"}


def test_stream_stops_at_done_and_does_not_read_next_event():
    events = iter([{"kind": "delta", "text": "正文"}, {"kind": "done"},
                   {"kind": "delta", "text": "不该读取"}])
    assert collect_stream(events) == {"status": "complete", "text": "正文"}
    assert next(events)["text"] == "不该读取"


def test_stream_done_without_text_is_complete_but_empty():
    assert collect_stream(iter([{"kind": "done"}])) == {"status": "complete", "text": ""}


def test_stream_iterator_is_consumed_once():
    class Once:
        def __init__(self):
            self.called = False
        def __iter__(self):
            assert not self.called, "流不能为了检查或拼接而读取两遍"
            self.called = True
            return iter([{"kind": "delta", "text": "一次"}, {"kind": "done"}])
    assert collect_stream(Once()) == {"status": "complete", "text": "一次"}


def test_commit_complete_turn_once_and_preserves_old_history():
    source = deepcopy(HISTORY)
    original = deepcopy(source)
    result = commit_turn(source, "怎样登录？", {"status": "complete", "text": "扫码登录。"})
    assert result == [*original, {"role": "user", "content": "怎样登录？"},
                      {"role": "assistant", "content": "扫码登录。"}]
    assert source == original, "提交不得原地修改输入历史"
    result[0]["content"] = "修改返回历史"
    assert source == original, "返回历史须复制旧消息字典"


def test_commit_does_not_store_incomplete_or_failed_answer():
    for status in ("incomplete", "failed"):
        source = deepcopy(HISTORY)
        result = commit_turn(source, "问题", {"status": status, "text": "半句"})
        assert result == HISTORY
        result[0]["content"] = "改返回值"
        assert source == HISTORY, "未提交分支也必须复制旧消息字典"


def test_commit_does_not_store_empty_or_whitespace_complete_answer():
    for text in ("", " \n "):
        assert commit_turn(HISTORY, "问题", {"status": "complete", "text": text}) == HISTORY


def test_commit_keeps_original_spaces_in_nonempty_answer():
    result = commit_turn([], "问题", {"status": "complete", "text": " 正文 "})
    assert result == [{"role": "user", "content": "问题"},
                      {"role": "assistant", "content": " 正文 "}]


def test_flow_next_request_contains_only_one_committed_new_turn():
    result = collect_stream(iter([{"kind": "delta", "text": "支持PDF"}, {"kind": "done"}]))
    saved = commit_turn([], "导出格式？", result)
    messages = build_request_messages("规则", saved, "如何操作？", 1)
    assert messages == [{"role": "system", "content": "规则"},
                        {"role": "user", "content": "导出格式？"},
                        {"role": "assistant", "content": "支持PDF"},
                        {"role": "user", "content": "如何操作？"}]
