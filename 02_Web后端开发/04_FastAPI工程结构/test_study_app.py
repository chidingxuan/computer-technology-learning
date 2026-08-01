"""第04课作业测试：FastAPI 工程结构。"""

import pytest
from fastapi.testclient import TestClient

from study_app.main import app
from study_app.services import list_tasks, reset_tasks


# raise_server_exceptions=False：如果作业代码暂时产生服务器内部错误，
# TestClient 会返回 500 响应，避免测试直接中断并显示很长的内部错误栈。
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def clean_task_storage():
    """让每个测试都从空任务列表开始，测试之间互不影响。"""

    reset_tasks()
    yield
    reset_tasks()


def test_app_has_required_title():
    assert app.title == "学习任务 API"


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_routes_are_included_in_openapi():
    schema = app.openapi()
    assert "/tasks" in schema["paths"]
    assert "tasks" in schema["paths"]["/tasks"]["get"]["tags"]
    assert "tasks" in schema["paths"]["/tasks"]["post"]["tags"]


def test_empty_task_list_is_returned_initially():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_returns_201_and_complete_response():
    response = client.post(
        "/tasks",
        json={"title": "复习 APIRouter", "priority": 3},
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "复习 APIRouter",
        "priority": 3,
        "completed": False,
    }


def test_create_task_uses_default_priority():
    response = client.post("/tasks", json={"title": "整理课堂笔记"})
    assert response.status_code == 201
    assert response.json()["priority"] == 1


def test_created_task_is_available_in_list():
    client.post("/tasks", json={"title": "完成工程结构作业"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "完成工程结构作业",
            "priority": 1,
            "completed": False,
        }
    ]

    returned_tasks = list_tasks()
    returned_tasks.clear()
    response_after_external_clear = client.get("/tasks")
    assert len(response_after_external_clear.json()) == 1


def test_ids_increase_in_creation_order():
    first = client.post("/tasks", json={"title": "任务一"})
    second = client.post("/tasks", json={"title": "任务二"})
    assert first.json()["id"] == 1
    assert second.json()["id"] == 2


def test_missing_title_returns_422():
    response = client.post("/tasks", json={"priority": 2})
    assert response.status_code == 422


def test_title_length_outside_1_to_80_returns_422():
    for invalid_title in ["", "学" * 81]:
        response = client.post("/tasks", json={"title": invalid_title})
        assert response.status_code == 422


@pytest.mark.parametrize("invalid_priority", [0, 6])
def test_priority_outside_1_to_5_returns_422(invalid_priority: int):
    response = client.post(
        "/tasks",
        json={"title": "测试优先级", "priority": invalid_priority},
    )
    assert response.status_code == 422
