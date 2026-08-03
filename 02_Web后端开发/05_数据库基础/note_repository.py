"""第05课作业：使用SQLite实现可持久化的笔记数据访问层。"""

import sqlite3


def open_database(db_path: str) -> sqlite3.Connection:
    """打开数据库连接，并让查询结果可以按列名读取。"""

    connection = sqlite3.connect(db_path, autocommit=False)
    connection.row_factory = sqlite3.Row
    return connection


def _row_to_note(row: sqlite3.Row) -> dict[str, object]:
    """把SQLite行对象转换为作业规定的Python字典。"""

    return {
        "id": row["id"],
        "content": row["content"],
        "category": row["category"],
        "completed": bool(row["completed"]),
    }


def initialize_database(db_path: str) -> None:
    """创建notes表；重复调用时不得删除已经存在的数据。"""

    # TODO：创建符合Notebook作业契约的notes表，并正确提交、关闭连接。
    note_connection = open_database(db_path)

    create_note_sql = """
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY,
        content TEXT NOT NULL CHECK(length(content) BETWEEN 1 AND 200),
        category TEXT NOT NULL DEFAULT 'general',
        completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1))
    )
    """
    try:
        note_connection.execute(create_note_sql)
        note_connection.commit()
    except sqlite3.Error:
        note_connection.rollback()
        raise
    finally:
        note_connection.close()

def create_note(db_path: str, content: str, category: str = "general") -> int:
    """创建笔记并返回数据库生成的整数id。"""

    # TODO：使用占位符插入数据，提交事务，返回lastrowid并关闭连接。
    note_connection = open_database(db_path)
    note_sql = "INSERT INTO notes(content, category) VALUES(?, ?)"
    note_data = (content, category)
    try:
        insert_note = note_connection.execute(note_sql, note_data)
        note_connection.commit()
    except sqlite3.Error:
        note_connection.rollback()
        raise
    finally:
        note_connection.close()
    return insert_note.lastrowid



def list_notes(db_path: str) -> list[dict[str, object]]:
    """按照id升序返回全部笔记。"""

    # TODO：查询全部笔记并使用_row_to_note转换；始终关闭连接。
    notes_connection = open_database(db_path)
    all_rows_sql = "SELECT id, content, category, completed FROM notes ORDER BY id ASC"
    all_rows = []
    try:
        notes_connection.row_factory = sqlite3.Row
        all_rows = notes_connection.execute(all_rows_sql).fetchall()
    except sqlite3.Error:
        notes_connection.rollback()
        raise
    finally:
        notes_connection.close()

    all_rows_list = []
    for row in all_rows:
        all_rows_list.append(_row_to_note(row))

    return all_rows_list


def get_note(db_path: str, note_id: int) -> dict[str, object] | None:
    """按id查询单条笔记；不存在时返回None。"""

    # TODO：使用占位符查询；区分找到sqlite3.Row和没有找到None。
    note_connection = open_database(db_path)
    note_sql = """
    SELECT id, content, category, completed FROM notes WHERE id = ?
    """
    note_data = (note_id,)

    try:
        one_row = note_connection.execute(note_sql, note_data).fetchone()
    except sqlite3.Error:
        note_connection.rollback()
        raise
    finally:
        note_connection.close()

    if one_row is None:
        return None
    return _row_to_note(one_row)


def mark_note_completed(db_path: str, note_id: int) -> bool:
    """将指定笔记标记为已完成；返回是否实际更新了一行。"""

    # TODO：执行参数化UPDATE，根据rowcount返回布尔值，并处理事务和连接。
    note_connection = open_database(db_path)
    note_sql = """
    UPDATE notes SET completed = ? WHERE id = ?
    """
    note_data = (1, note_id)
    flag: int
    try:
        update_note = note_connection.execute(note_sql, note_data)
        note_connection.commit()
        flag = update_note.rowcount
    except sqlite3.Error:
        note_connection.rollback()
        raise
    finally:
        note_connection.close()

    return bool(flag)


def delete_note(db_path: str, note_id: int) -> bool:
    """删除指定笔记；返回是否实际删除了一行。"""

    # TODO：执行参数化DELETE，根据rowcount返回布尔值，并处理事务和连接。
    note_connection = open_database(db_path)
    note_sql = """
    DELETE FROM notes WHERE id = ?
    """
    note_data = (note_id,)
    try:
        delete_notes = note_connection.execute(note_sql, note_data)
        note_connection.commit()
        flag = delete_notes.rowcount
    except sqlite3.Error:
        note_connection.rollback()
        raise
    finally:
        note_connection.close()

    return bool(flag)
