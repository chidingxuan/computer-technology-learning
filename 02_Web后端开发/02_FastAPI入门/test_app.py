"""第02课FastAPI接口测试。"""

from fastapi.testclient import TestClient

from app import app


# TestClient(app)创建一个测试客户端，app参数是要测试的FastAPI应用。
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_hello_uses_default_name():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "你好，世界"}


def test_hello_accepts_query_parameter():
    # params参数是查询参数字典，会生成类似/hello?name=小明的请求。
    response = client.get("/hello", params={"name": "小明"})
    assert response.json() == {"message": "你好，小明"}


def test_get_item_accepts_integer_path_parameter():
    response = client.get("/items/25")
    assert response.status_code == 200
    assert response.json() == {"item_id": 25}


def test_get_item_rejects_non_integer_path_parameter():
    response = client.get("/items/abc")
    assert response.status_code == 422


def test_echo_returns_201():
    response = client.post("/echo", json={"text": "你好"})
    assert response.status_code == 201


def test_echo_returns_original_object():
    payload = {"text": "你好", "count": 2}
    response = client.post("/echo", json=payload)
    assert response.json() == {"received": payload}


def test_unknown_route_returns_404():
    response = client.get("/not-found")
    assert response.status_code == 404
