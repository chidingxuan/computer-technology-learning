"""第二课作业测试：检查提示词结构、角色分工和受控参数实验。"""

from prompt_design import (
    PROMPT_VERSION,
    build_prompt_test_cases,
    build_support_messages,
    build_temperature_experiment,
)


def test_prompt_version_is_fixed():
    assert PROMPT_VERSION == "support-v1"


def test_support_messages_use_system_then_user_roles():
    messages = build_support_messages("云笔记", "支持导出Markdown和PDF。", "怎样导出文件？")

    assert isinstance(messages, list)
    assert [message["role"] for message in messages] == ["system", "user"]


def test_system_message_contains_four_prompt_parts():
    messages = build_support_messages("云笔记", "支持导出Markdown和PDF。", "怎样导出文件？")
    system_content = messages[0]["content"]

    assert "云笔记" in system_content
    assert "支持导出Markdown和PDF" in system_content
    assert "只根据" in system_content
    assert "不知道" in system_content
    assert "三句话" in system_content


def test_support_messages_clean_dynamic_text():
    messages = build_support_messages(
        "  云笔记  ",
        "  支持导出Markdown和PDF。  ",
        "  怎样导出文件？  ",
    )

    assert messages[0]["content"].count("  ") == 0
    assert messages[1] == {"role": "user", "content": "怎样导出文件？"}


def test_temperature_experiment_has_two_request_groups():
    messages = [{"role": "user", "content": "给这个功能起名"}]
    requests = build_temperature_experiment("demo-model", messages)

    assert isinstance(requests, list)
    assert len(requests) == 2
    assert all(request["model"] == "demo-model" for request in requests)
    assert all(request["max_tokens"] == 300 for request in requests)


def test_temperature_is_the_only_changed_experiment_factor():
    messages = [{"role": "user", "content": "给这个功能起名"}]
    stable_request, varied_request = build_temperature_experiment("demo-model", messages)

    assert stable_request["temperature"] == 0.2
    assert varied_request["temperature"] == 1.0
    stable_without_temperature = {
        key: value for key, value in stable_request.items() if key != "temperature"
    }
    varied_without_temperature = {
        key: value for key, value in varied_request.items() if key != "temperature"
    }
    assert stable_without_temperature == varied_without_temperature


def test_prompt_test_cases_cover_three_required_kinds():
    cases = build_prompt_test_cases()

    assert isinstance(cases, list)
    assert len(cases) == 3
    assert {case["kind"] for case in cases} == {"normal", "unknown", "conflict"}


def test_prompt_test_cases_have_executable_inputs_and_expectations():
    cases = build_prompt_test_cases()

    assert all(isinstance(case["question"], str) and case["question"].strip() for case in cases)
    assert all(
        isinstance(case["expected_behavior"], str) and case["expected_behavior"].strip()
        for case in cases
    )


def test_prompt_test_cases_define_key_expected_behaviors():
    cases_by_kind = {case["kind"]: case for case in build_prompt_test_cases()}

    assert "回答" in cases_by_kind["normal"]["expected_behavior"]
    assert "不知道" in cases_by_kind["unknown"]["expected_behavior"]
    assert "不编造" in cases_by_kind["conflict"]["expected_behavior"]
