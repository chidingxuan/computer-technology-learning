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
    raise NotImplementedError("TODO：实现 initialize_database")


def create_note(db_path: str, content: str, category: str = "general") -> int:
    """创建笔记并返回数据库生成的整数id。"""

    # TODO：使用占位符插入数据，提交事务，返回lastrowid并关闭连接。
    raise NotImplementedError("TODO：实现 create_note")


def list_notes(db_path: str) -> list[dict[str, object]]:
    """按照id升序返回全部笔记。"""

    # TODO：查询全部笔记并使用_row_to_note转换；始终关闭连接。
    raise NotImplementedError("TODO：实现 list_notes")


def get_note(db_path: str, note_id: int) -> dict[str, object] | None:
    """按id查询单条笔记；不存在时返回None。"""

    # TODO：使用占位符查询；区分找到sqlite3.Row和没有找到None。
    raise NotImplementedError("TODO：实现 get_note")


def mark_note_completed(db_path: str, note_id: int) -> bool:
    """将指定笔记标记为已完成；返回是否实际更新了一行。"""

    # TODO：执行参数化UPDATE，根据rowcount返回布尔值，并处理事务和连接。
    raise NotImplementedError("TODO：实现 mark_note_completed")


def delete_note(db_path: str, note_id: int) -> bool:
    """删除指定笔记；返回是否实际删除了一行。"""

    # TODO：执行参数化DELETE，根据rowcount返回布尔值，并处理事务和连接。
    raise NotImplementedError("TODO：实现 delete_note")
