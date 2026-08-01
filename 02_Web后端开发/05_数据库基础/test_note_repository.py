"""第05课作业测试：SQLite数据库基础。"""

import sqlite3

import pytest

from note_repository import (
    create_note,
    delete_note,
    get_note,
    initialize_database,
    list_notes,
    mark_note_completed,
)


@pytest.fixture
def database_path(tmp_path) -> str:
    """为每个测试创建互不影响的临时数据库路径。"""

    path = str(tmp_path / "notes.sqlite3")
    initialize_database(path)
    return path


def test_initialize_creates_database_file_and_notes_table(tmp_path):
    path = tmp_path / "new_notes.sqlite3"
    initialize_database(str(path))

    assert path.exists()
    connection = sqlite3.connect(path)
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
        ("table", "notes"),
    ).fetchone()
    connection.close()
    assert table == ("notes",)


def test_initialize_can_repeat_without_deleting_existing_data(database_path):
    create_note(database_path, "保留这条笔记")
    initialize_database(database_path)
    assert [note["content"] for note in list_notes(database_path)] == ["保留这条笔记"]


def test_new_database_returns_empty_list(database_path):
    assert list_notes(database_path) == []


def test_create_note_returns_increasing_integer_ids(database_path):
    first_id = create_note(database_path, "第一条")
    second_id = create_note(database_path, "第二条")
    assert isinstance(first_id, int)
    assert (first_id, second_id) == (1, 2)


def test_create_note_uses_default_category(database_path):
    note_id = create_note(database_path, "学习SQLite")
    assert get_note(database_path, note_id) == {
        "id": 1,
        "content": "学习SQLite",
        "category": "general",
        "completed": False,
    }


def test_create_note_accepts_custom_category(database_path):
    note_id = create_note(database_path, "复习事务", "database")
    assert get_note(database_path, note_id)["category"] == "database"


def test_list_notes_returns_complete_rows_in_id_order(database_path):
    create_note(database_path, "任务A", "study")
    create_note(database_path, "任务B", "project")
    assert list_notes(database_path) == [
        {"id": 1, "content": "任务A", "category": "study", "completed": False},
        {"id": 2, "content": "任务B", "category": "project", "completed": False},
    ]


def test_get_note_returns_existing_note(database_path):
    note_id = create_note(database_path, "按id查询")
    assert get_note(database_path, note_id)["content"] == "按id查询"


def test_get_note_returns_none_when_id_does_not_exist(database_path):
    assert get_note(database_path, 999) is None


def test_mark_note_completed_updates_existing_note(database_path):
    note_id = create_note(database_path, "完成数据库作业")
    assert mark_note_completed(database_path, note_id) is True
    assert get_note(database_path, note_id)["completed"] is True


def test_mark_note_completed_returns_false_for_missing_id(database_path):
    assert mark_note_completed(database_path, 999) is False


def test_delete_note_removes_existing_note(database_path):
    note_id = create_note(database_path, "待删除")
    assert delete_note(database_path, note_id) is True
    assert get_note(database_path, note_id) is None


def test_delete_note_returns_false_for_missing_id(database_path):
    assert delete_note(database_path, 999) is False


def test_sql_like_text_is_stored_as_plain_content(database_path):
    unusual_content = "'); DROP TABLE notes; --"
    note_id = create_note(database_path, unusual_content)
    assert get_note(database_path, note_id)["content"] == unusual_content
    assert len(list_notes(database_path)) == 1


def test_content_database_constraints_are_enforced(database_path):
    for invalid_content in ["", "字" * 201]:
        with pytest.raises(sqlite3.IntegrityError):
            create_note(database_path, invalid_content)


def test_created_data_really_exists_in_sqlite_file(database_path):
    create_note(database_path, "磁盘中的数据", "persistence")

    independent_connection = sqlite3.connect(database_path)
    row = independent_connection.execute(
        "SELECT content, category, completed FROM notes WHERE id = ?",
        (1,),
    ).fetchone()
    independent_connection.close()

    assert row == ("磁盘中的数据", "persistence", 0)
