"""第03课Pydantic数据模型测试。"""

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_create_book_returns_201():
    response = client.post(
        "/books",
        json={"title": "Python工程实践", "price": 59.9},
    )
    assert response.status_code == 201


def test_create_book_returns_complete_response():
    response = client.post(
        "/books",
        json={"title": "Python工程实践", "price": 59.9},
    )
    assert response.json() == {
        "id": 1,
        "title": "Python工程实践",
        "price": 59.9,
        "in_stock": True,
        "note": None,
    }


def test_create_book_accepts_optional_values():
    response = client.post(
        "/books",
        json={
            "title": "FastAPI实战",
            "price": 88.0,
            "in_stock": False,
            "note": "第二版",
        },
    )
    assert response.status_code == 201
    assert response.json()["in_stock"] is False
    assert response.json()["note"] == "第二版"


def test_title_is_required():
    response = client.post("/books", json={"price": 59.9})
    assert response.status_code == 422


def test_title_cannot_be_empty():
    response = client.post("/books", json={"title": "", "price": 59.9})
    assert response.status_code == 422


def test_title_cannot_exceed_100_characters():
    response = client.post(
        "/books",
        json={"title": "书" * 101, "price": 59.9},
    )
    assert response.status_code == 422


def test_price_is_required():
    response = client.post("/books", json={"title": "Python工程实践"})
    assert response.status_code == 422


def test_price_must_be_greater_than_zero():
    response = client.post(
        "/books",
        json={"title": "Python工程实践", "price": 0},
    )
    assert response.status_code == 422


def test_price_cannot_be_negative():
    response = client.post(
        "/books",
        json={"title": "Python工程实践", "price": -1},
    )
    assert response.status_code == 422


def test_price_must_be_parseable_as_number():
    response = client.post(
        "/books",
        json={"title": "Python工程实践", "price": "免费"},
    )
    assert response.status_code == 422
