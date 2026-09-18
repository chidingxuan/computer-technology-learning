"""19项离线测试。测试结构契约，不评价真实模型提取质量。"""
import json

import pytest
from pydantic import BaseModel, ValidationError

from structured_ticket import create_ticket_model, parse_ticket_result, ticket_schema


VALID = {"summary": "导出闪退", "category": "bug", "priority": 3, "contact": None}


def test_model_returns_class_and_preserves_valid_record():
    model = create_ticket_model()
    assert isinstance(model, type) and issubclass(model, BaseModel), "任务1应返回模型类"
    assert model.model_validate(VALID).model_dump() == VALID


def test_model_supports_both_categories_and_priority_endpoints():
    model = create_ticket_model()
    for category in ("bug", "question"):
        for priority in (1, 3):
            data = {**VALID, "category": category, "priority": priority, "contact": "小陈"}
            assert model.model_validate(data).model_dump() == data


def test_model_requires_every_field_including_nullable_contact():
    model = create_ticket_model()
    for missing in VALID:
        with pytest.raises(ValidationError):
            model.model_validate({k: v for k, v in VALID.items() if k != missing})


def test_model_rejects_unknown_category():
    model = create_ticket_model()
    with pytest.raises(ValidationError):
        model.model_validate({**VALID, "category": "other"})


def test_model_rejects_out_of_range_priority():
    model = create_ticket_model()
    for value in (0, 4):
        with pytest.raises(ValidationError):
            model.model_validate({**VALID, "priority": value})


def test_model_is_strict_about_field_types():
    model = create_ticket_model()
    for changes in ({"priority": "3"}, {"priority": True}, {"summary": 3}, {"contact": 3}):
        with pytest.raises(ValidationError):
            model.model_validate({**VALID, **changes})


def test_model_rejects_extra_fields():
    model = create_ticket_model()
    with pytest.raises(ValidationError):
        model.model_validate({**VALID, "invented": "不允许"})


def test_schema_describes_object_and_required_fields():
    schema = ticket_schema()
    assert isinstance(schema, dict), "Schema应为字典"
    assert schema["type"] == "object"
    assert set(schema["properties"]) == set(VALID)
    assert set(schema["required"]) == set(VALID)
    assert schema["additionalProperties"] is False


def test_schema_describes_enum_range_and_nullable_field():
    properties = ticket_schema()["properties"]
    assert properties["summary"]["type"] == "string"
    assert set(properties["category"]["enum"]) == {"bug", "question"}
    assert properties["priority"]["type"] == "integer"
    assert properties["priority"]["minimum"] == 1
    assert properties["priority"]["maximum"] == 3
    assert {item["type"] for item in properties["contact"]["anyOf"]} == {"string", "null"}


def test_schema_matches_model_schema():
    assert ticket_schema() == create_ticket_model().model_json_schema()


def test_parse_valid_record():
    assert parse_ticket_result(json.dumps(VALID)) == {"status": "ok", "data": VALID}


def test_parse_another_record_without_hardcoding():
    data = {"summary": "如何导出", "category": "question", "priority": 1, "contact": "小林"}
    assert parse_ticket_result(json.dumps(data), "") == {"status": "ok", "data": data}


def test_parse_refusal_takes_priority_even_with_valid_content():
    for content in (None, json.dumps(VALID), "{"):
        assert parse_ticket_result(content, "无法提供") == {"status": "refused", "data": None}


def test_parse_empty_content():
    for content in (None, "", "  \n "):
        assert parse_ticket_result(content) == {"status": "empty", "data": None}


def test_parse_invalid_or_truncated_json():
    for content in ("不是JSON", '{"summary":', "{'summary': '错误'}"):
        assert parse_ticket_result(content) == {"status": "invalid_json", "data": None}


def test_parse_markdown_fence_is_not_pure_json():
    content = "```json\n" + json.dumps(VALID) + "\n```"
    assert parse_ticket_result(content) == {"status": "invalid_json", "data": None}


def test_parse_legal_json_with_wrong_top_level():
    for content in ("[]", "null", '"文本"', "12"):
        assert parse_ticket_result(content) == {"status": "invalid_data", "data": None}


def test_parse_missing_required_fields():
    for missing in VALID:
        content = json.dumps({k: v for k, v in VALID.items() if k != missing})
        assert parse_ticket_result(content) == {"status": "invalid_data", "data": None}


def test_parse_rejects_invalid_fields_without_fabricating_data():
    for changes in ({"priority": 4}, {"priority": "3"}, {"category": "other"}, {"extra": 1}):
        content = json.dumps({**VALID, **changes})
        assert parse_ticket_result(content) == {"status": "invalid_data", "data": None}
