"""第01课作业测试。"""

from http_api_exercise import build_response, create_chat, route_request


def test_build_response_has_standard_structure():
    assert build_response(200, {"message": "ok"}) == {
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"message": "ok"},
    }


def test_create_chat_returns_201_and_strips_title():
    assert create_chat({"title": " Python学习 "}) == {
        "status_code": 201,
        "headers": {"Content-Type": "application/json"},
        "body": {"id": 1, "title": "Python学习"},
    }


def test_create_chat_rejects_non_dict_body():
    response = create_chat("不是字典")
    assert response["status_code"] == 400
    assert response["body"]["detail"] == "title必须是非空字符串"


def test_create_chat_rejects_missing_title():
    assert create_chat({})["status_code"] == 400


def test_create_chat_rejects_blank_title():
    assert create_chat({"title": "   "})["status_code"] == 400


def test_route_request_health_check():
    assert route_request("GET", "/health")["body"] == {"status": "ok"}


def test_route_request_method_is_case_insensitive():
    assert route_request("get", "/health")["status_code"] == 200


def test_route_request_creates_chat():
    response = route_request("POST", "/chats", {"title": "LLM"})
    assert response["status_code"] == 201
    assert response["body"] == {"id": 1, "title": "LLM"}


def test_route_request_rejects_non_string_method():
    response = route_request(123, "/health")  # type: ignore[arg-type]
    assert response["status_code"] == 400
    assert response["body"]["detail"] == "method必须是字符串"


def test_route_request_returns_404_for_unknown_route():
    response = route_request("GET", "/unknown")
    assert response["status_code"] == 404
    assert response["body"]["detail"] == "接口不存在"
