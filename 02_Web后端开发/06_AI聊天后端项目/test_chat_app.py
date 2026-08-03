"""第06课作业测试。

测试按层分组，因此可以分阶段运行：
python -m pytest test_chat_app.py -v -m schema
python -m pytest test_chat_app.py -v -m provider
python -m pytest test_chat_app.py -v -m repository
python -m pytest test_chat_app.py -v -m service
python -m pytest test_chat_app.py -v -m api
"""

import sqlite3
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from chat_app import repository, services
from chat_app.ai_provider import generate_reply
from chat_app.main import app
from chat_app.schemas import ConversationCreate, ConversationResponse
from chat_app.schemas import MessageCreate, MessageResponse


pytestmark = pytest.mark.filterwarnings(
    "ignore:Using `httpx` with `starlette.testclient` is deprecated"
)


def _prepare_database(tmp_path) -> str:
    """为一个测试准备独立数据库；不是 autouse，不阻塞其他层测试。"""

    db_path = str(tmp_path / "chat.sqlite3")
    repository.configure_database(db_path)
    repository.initialize_database()
    return db_path


def _client_for(tmp_path) -> TestClient:
    """先准备临时数据库，再创建进程内 HTTP 测试客户端。"""

    _prepare_database(tmp_path)
    return TestClient(app, raise_server_exceptions=False)


def _assert_iso_datetime(value: object) -> None:
    """确认值是可解析且带时区的 ISO 时间字符串。"""

    assert isinstance(value, str) and value
    parsed = datetime.fromisoformat(value)
    assert parsed.utcoffset() is not None


@pytest.mark.schema
def test_schema_conversation_create_default_and_custom_title():
    assert ConversationCreate().title == "新会话"
    assert ConversationCreate(title="数据库复习").title == "数据库复习"


@pytest.mark.schema
@pytest.mark.parametrize("invalid_title", ["", "学" * 51])
def test_schema_conversation_title_rejects_invalid_length(invalid_title: str):
    with pytest.raises(ValidationError):
        ConversationCreate(title=invalid_title)


@pytest.mark.schema
def test_schema_conversation_response_requires_server_fields():
    valid = ConversationResponse(id=1, title="新会话", created_at="2026-01-01T00:00:00+00:00")
    assert valid.id == 1
    with pytest.raises(ValidationError):
        ConversationResponse(title="缺少服务器字段")


@pytest.mark.schema
@pytest.mark.parametrize("content", ["好", "字" * 500])
def test_schema_message_accepts_boundary_lengths(content: str):
    assert MessageCreate(content=content).content == content


@pytest.mark.schema
@pytest.mark.parametrize("payload", [{}, {"content": ""}, {"content": "字" * 501}])
def test_schema_message_rejects_missing_or_invalid_content(payload: dict):
    with pytest.raises(ValidationError):
        MessageCreate(**payload)


@pytest.mark.schema
def test_schema_message_response_has_all_server_fields():
    message = MessageResponse(
        id=2,
        conversation_id=1,
        role="assistant",
        content="模拟回复",
        created_at="2026-01-01T00:00:00+00:00",
    )
    assert message.model_dump()["role"] == "assistant"


@pytest.mark.provider
@pytest.mark.parametrize("content", ["你好", "请解释外键", "字" * 500])
def test_provider_reply_is_nonempty_and_contains_original_message(content: str):
    reply = generate_reply(content)
    assert isinstance(reply, str)
    assert reply.strip()
    assert content in reply
    assert len(reply) <= 2000


@pytest.mark.repository
def test_repository_connection_enables_rows_and_foreign_keys(tmp_path):
    repository.configure_database(str(tmp_path / "connection.sqlite3"))
    connection = repository._open_connection()
    try:
        assert connection.row_factory is sqlite3.Row
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


@pytest.mark.repository
def test_repository_initialization_creates_required_schema(tmp_path):
    db_path = _prepare_database(tmp_path)
    connection = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        foreign_keys = connection.execute("PRAGMA foreign_key_list(messages)").fetchall()
        conversation_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'"
        ).fetchone()[0]
        message_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='messages'"
        ).fetchone()[0]
    finally:
        connection.close()

    assert {"conversations", "messages"} <= tables
    assert any(row[2] == "conversations" and row[3] == "conversation_id" and row[4] == "id" for row in foreign_keys)
    normalized_conversation_sql = " ".join(conversation_sql.upper().split())
    normalized_message_sql = " ".join(message_sql.upper().split())
    assert "CHECK" in normalized_conversation_sql and "LENGTH(TITLE)" in normalized_conversation_sql
    assert "CHECK" in normalized_message_sql and "LENGTH(CONTENT)" in normalized_message_sql
    assert "CHECK" in normalized_message_sql and "ROLE" in normalized_message_sql


@pytest.mark.repository
def test_repository_initialization_is_repeatable_and_preserves_data(tmp_path):
    _prepare_database(tmp_path)
    created = repository.create_conversation("不能被删掉")
    repository.initialize_database()
    assert repository.get_conversation(created["id"])["title"] == "不能被删掉"


@pytest.mark.repository
def test_repository_database_constraints_reject_invalid_rows(tmp_path):
    _prepare_database(tmp_path)
    conversation = repository.create_conversation("约束测试")
    connection = repository._open_connection()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO conversations(title, created_at) VALUES(?, ?)",
                ("", "2026-01-01T00:00:00+00:00"),
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO conversations(title, created_at) VALUES(?, ?)",
                ("学" * 51, "2026-01-01T00:00:00+00:00"),
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO messages(conversation_id, role, content, created_at) VALUES(?, ?, ?, ?)",
                (conversation["id"], "system", "错误角色", "2026-01-01T00:00:00+00:00"),
            )
        connection.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO messages(conversation_id, role, content, created_at) VALUES(?, ?, ?, ?)",
                (999, "user", "孤儿消息", "2026-01-01T00:00:00+00:00"),
            )
        connection.rollback()

        for invalid_content in ("", "字" * 2001):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO messages(conversation_id, role, content, created_at) VALUES(?, ?, ?, ?)",
                    (conversation["id"], "user", invalid_content, "2026-01-01T00:00:00+00:00"),
                )
            connection.rollback()
    finally:
        connection.close()


@pytest.mark.repository
def test_repository_create_conversation_returns_complete_record(tmp_path):
    _prepare_database(tmp_path)
    created = repository.create_conversation("第一段会话")
    assert created["id"] == 1
    assert created["title"] == "第一段会话"
    _assert_iso_datetime(created["created_at"])


@pytest.mark.repository
def test_repository_lists_conversations_in_id_order_and_gets_one(tmp_path):
    _prepare_database(tmp_path)
    repository.create_conversation("会话一")
    second = repository.create_conversation("会话二")
    assert [item["title"] for item in repository.list_conversations()] == ["会话一", "会话二"]
    assert repository.get_conversation(second["id"])["title"] == "会话二"
    assert repository.get_conversation(999) is None


@pytest.mark.repository
def test_repository_create_and_list_messages_are_complete_and_filtered(tmp_path):
    _prepare_database(tmp_path)
    first_conversation = repository.create_conversation("会话一")
    second_conversation = repository.create_conversation("会话二")
    first_message = repository.create_message(first_conversation["id"], "user", "第一条")
    second_message = repository.create_message(second_conversation["id"], "assistant", "另一会话")

    assert first_message["id"] == 1
    assert second_message["id"] == 2
    assert first_message["conversation_id"] == first_conversation["id"]
    assert first_message["role"] == "user"
    _assert_iso_datetime(first_message["created_at"])
    assert [item["content"] for item in repository.list_messages(first_conversation["id"])] == ["第一条"]


@pytest.mark.repository
def test_repository_create_message_rejects_missing_conversation(tmp_path):
    _prepare_database(tmp_path)
    with pytest.raises(sqlite3.IntegrityError):
        repository.create_message(999, "user", "没有所属会话")


@pytest.mark.service
def test_service_create_list_and_get_conversations(tmp_path):
    _prepare_database(tmp_path)
    created = services.create_conversation(ConversationCreate(title="业务层会话"))
    assert isinstance(created, ConversationResponse)
    assert services.list_conversations() == [created]
    assert services.get_conversation(created.id) == created


@pytest.mark.service
def test_service_get_missing_conversation_raises_business_error(tmp_path):
    _prepare_database(tmp_path)
    with pytest.raises(services.ConversationNotFoundError):
        services.get_conversation(999)


@pytest.mark.service
def test_service_send_message_saves_user_then_assistant_and_returns_reply(tmp_path):
    _prepare_database(tmp_path)
    conversation = services.create_conversation(ConversationCreate(title="发送消息"))
    reply = services.send_message(conversation.id, MessageCreate(content="解释事务"))
    messages = services.list_messages(conversation.id)

    assert isinstance(reply, MessageResponse)
    assert reply.role == "assistant"
    assert "解释事务" in reply.content
    assert [message.role for message in messages] == ["user", "assistant"]
    assert messages[1] == reply


@pytest.mark.service
@pytest.mark.parametrize("operation", ["send", "list"])
def test_service_message_operations_reject_missing_conversation(tmp_path, operation: str):
    _prepare_database(tmp_path)
    with pytest.raises(services.ConversationNotFoundError):
        if operation == "send":
            services.send_message(999, MessageCreate(content="无效会话"))
        else:
            services.list_messages(999)


@pytest.mark.api
def test_api_app_metadata_health_and_routes():
    assert app.title == "AI聊天后端"
    client = TestClient(app, raise_server_exceptions=False)
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    paths = app.openapi()["paths"]
    assert "/conversations" in paths
    assert "/conversations/{conversation_id}" in paths
    assert "/conversations/{conversation_id}/messages" in paths
    assert paths["/conversations"]["post"]["tags"] == ["chat"]


@pytest.mark.api
def test_api_lifespan_configures_and_initializes_default_database(monkeypatch):
    calls: list[tuple[str, str | None]] = []

    monkeypatch.setattr(
        repository,
        "configure_database",
        lambda path: calls.append(("configure", path)),
    )
    monkeypatch.setattr(
        repository,
        "initialize_database",
        lambda: calls.append(("initialize", None)),
    )

    with TestClient(app, raise_server_exceptions=False) as lifespan_client:
        assert lifespan_client.get("/health").status_code == 200

    assert [name for name, _ in calls] == ["configure", "initialize"]
    assert calls[0][1].endswith("chat.sqlite3")


@pytest.mark.api
def test_api_create_list_and_get_conversation(tmp_path):
    client = _client_for(tmp_path)
    created_response = client.post("/conversations", json={"title": "接口会话"})
    assert created_response.status_code == 201
    created = created_response.json()
    _assert_iso_datetime(created["created_at"])

    list_response = client.get("/conversations")
    assert list_response.status_code == 200
    assert list_response.json() == [created]

    get_response = client.get(f"/conversations/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created

    empty_messages = client.get(f"/conversations/{created['id']}/messages")
    assert empty_messages.status_code == 200
    assert empty_messages.json() == []


@pytest.mark.api
def test_api_default_title_and_validation_errors(tmp_path):
    client = _client_for(tmp_path)
    assert client.post("/conversations", json={}).json()["title"] == "新会话"
    assert client.post("/conversations", json={"title": ""}).status_code == 422
    assert client.post("/conversations", json={"title": "学" * 51}).status_code == 422


@pytest.mark.api
def test_api_missing_conversation_errors_are_consistent(tmp_path):
    client = _client_for(tmp_path)
    responses = [
        client.get("/conversations/999"),
        client.post("/conversations/999/messages", json={"content": "不存在"}),
        client.get("/conversations/999/messages"),
    ]
    for response in responses:
        assert response.status_code == 404
        assert response.json() == {"detail": "会话不存在"}


@pytest.mark.api
def test_api_send_message_returns_reply_and_persists_both_messages(tmp_path):
    client = _client_for(tmp_path)
    conversation = client.post("/conversations", json={"title": "聊天"}).json()
    response = client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"content": "请解释外键"},
    )
    assert response.status_code == 201
    reply = response.json()
    assert reply["role"] == "assistant"
    assert "请解释外键" in reply["content"]

    messages = client.get(f"/conversations/{conversation['id']}/messages").json()
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert [message["id"] for message in messages] == [1, 2]
    assert messages[0]["content"] == "请解释外键"
    assert messages[1] == reply


@pytest.mark.api
def test_api_accepts_exactly_500_characters_and_rejects_outside_range(tmp_path):
    client = _client_for(tmp_path)
    conversation = client.post("/conversations", json={}).json()
    base_url = f"/conversations/{conversation['id']}/messages"
    assert client.post(base_url, json={"content": "字" * 500}).status_code == 201
    assert client.post(base_url, json={"content": ""}).status_code == 422
    assert client.post(base_url, json={"content": "字" * 501}).status_code == 422


@pytest.mark.api
def test_api_data_is_really_stored_in_sqlite_file(tmp_path):
    db_path = _prepare_database(tmp_path)
    client = TestClient(app, raise_server_exceptions=False)
    conversation = client.post("/conversations", json={"title": "持久化"}).json()
    client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"content": "写入文件"},
    )

    connection = sqlite3.connect(db_path)
    try:
        conversations = connection.execute("SELECT title FROM conversations").fetchall()
        messages = connection.execute("SELECT role, content FROM messages ORDER BY id").fetchall()
    finally:
        connection.close()

    assert conversations == [("持久化",)]
    assert [row[0] for row in messages] == ["user", "assistant"]
    assert messages[0][1] == "写入文件"
