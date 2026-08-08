"""第06课作业：SQLite 数据访问层。

本层只处理数据库路径、连接、SQL、事务和查询结果转换，不处理 HTTP，
也不决定“发送消息后要生成 AI 回复”这样的业务流程。
"""

import sqlite3
from datetime import datetime, timezone


_DB_PATH: str | None = None


def configure_database(db_path: str) -> None:
    """设置后续 repository 函数使用的 SQLite 文件路径。"""

    global _DB_PATH
    _DB_PATH = db_path


def _get_db_path() -> str:
    """取得数据库路径；尚未配置时给出明确错误。"""

    if _DB_PATH is None:
        raise RuntimeError("尚未配置数据库路径，请先调用 configure_database()")
    return _DB_PATH


def _open_connection() -> sqlite3.Connection:
    """打开并配置一个连接。

    SQLite 的外键检查需要对每个连接单独开启，所以所有 repository 函数
    都必须通过这个函数获得连接。
    """


    # TODO 1：
    # 1. 使用 _get_db_path() 打开 sqlite3.Connection；
    # 2. 把 row_factory 设置为 sqlite3.Row；
    # 3. 执行 PRAGMA foreign_keys = ON；
    # 4. 返回连接对象。
    connection = sqlite3.connect(_get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _utc_now_iso() -> str:
    """返回带时区信息的 UTC ISO 时间字符串。"""

    return datetime.now(timezone.utc).isoformat()


def _row_to_conversation(row: sqlite3.Row) -> dict[str, object]:
    """把 conversations 查询行转换成普通字典。"""

    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
    }


def _row_to_message(row: sqlite3.Row) -> dict[str, object]:
    """把 messages 查询行转换成普通字典。"""

    return {
        "id": row["id"],
        "conversation_id": row["conversation_id"],
        "role": row["role"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


def initialize_database() -> None:
    """创建两张表；重复调用时必须保留原有数据。"""

    # TODO 2：通过 _open_connection() 打开连接并创建 conversations、messages。
    # 表结构和约束见 Notebook。成功时 commit，异常时 rollback，最后 close。
    connection = _open_connection()
    conversation_sql = """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 50),
            created_at TEXT NOT NULL
        )
    """
    message_sql = """
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id),
            role TEXT NOT NULL CHECK(role in ('user', 'assistant')),
            content TEXT NOT NULL CHECK(length(content) BETWEEN 1 and 2000),
            created_at TEXT NOT NULL
        )
    """
    try:
        connection.execute(conversation_sql)
        connection.execute(message_sql)
        connection.commit()
    except:
        connection.rollback()
        raise
    finally:
        connection.close()



def create_conversation(title: str) -> dict[str, object]:
    """保存会话并返回包含 id、title、created_at 的完整字典。"""

    # TODO 3：生成一次 created_at，使用参数化 INSERT 保存数据并提交。
    # 返回完整会话字典；异常时 rollback；最后关闭连接。
    create_at = _utc_now_iso()
    connection = _open_connection()
    connection_sql = """
        INSERT INTO conversations(title, created_at) VALUES (?,?)
    """
    connection_data = (title, create_at)
    try:
        insert = connection.execute(connection_sql, connection_data)
        connection.commit()
        conversation_dict = {
            "id": insert.lastrowid,
            "title": title,
            "created_at": create_at
        }
    except:
        connection.rollback()
        raise
    finally:
        connection.close()

    return conversation_dict


def list_conversations() -> list[dict[str, object]]:
    """按 id 升序返回全部会话；没有数据时返回空列表。"""

    # TODO 4：执行 SELECT，使用 _row_to_conversation 转换每一行。
    connection = _open_connection()
    conversation_sql = """
        SELECT id, title, created_at FROM conversations ORDER BY id ASC
    """
    try:
        all_rows = connection.execute(conversation_sql).fetchall()
    except:
        connection.rollback()
        raise
    finally:
        connection.close()

    conversations = []
    for row in all_rows:
        conversations.append(_row_to_conversation(row))
    return conversations

def get_conversation(conversation_id: int) -> dict[str, object] | None:
    """按 id 查询会话；不存在时返回 None。"""

    # TODO 5：使用 ? 占位符查询一行，区分找到和未找到。
    connection = _open_connection()
    conversation_sql = "SELECT id,title,created_at FROM conversations WHERE id = ?"
    conversation_data = (conversation_id, )
    try:
        row = connection.execute(conversation_sql,conversation_data).fetchone()

    except:
        connection.rollback()
        raise
    finally:
        connection.close()

    if row == None:
        return None
    return _row_to_conversation(row)


def create_message(
    conversation_id: int,
    role: str,
    content: str,
) -> dict[str, object]:
    """保存消息并返回完整消息字典。

    conversation_id 必须指向已存在的会话；role 只允许 user 或 assistant。
    """

    # TODO 6：生成 created_at，参数化插入并提交，返回完整消息字典。
    # 外键或 CHECK 约束不满足时，让 sqlite3.IntegrityError 继续抛出；
    # 但必须先 rollback，并在 finally 中关闭连接。
    created_at = _utc_now_iso()
    message_sql = "INSERT INTO messages(conversation_id, role, content, created_at) VALUES(?,?,?,?)"
    message_data = (conversation_id, role, content, created_at)
    connection = _open_connection()

    try:
        all_row = connection.execute(message_sql, message_data)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    message_dict={
        "id": all_row.lastrowid,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": created_at,
    }

    return message_dict




def list_messages(conversation_id: int) -> list[dict[str, object]]:
    """按 id 升序返回指定会话的全部消息。"""

    # TODO 7：使用 WHERE conversation_id = ? 查询并转换所有结果行。
    connection = _open_connection()
    message_sql = "SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC"
    message_data = (conversation_id,)
    conversations=[]
    try:
        all_row = connection.execute(message_sql, message_data).fetchall()
    except:
        connection.rollback()
        raise
    finally:
        connection.close()
    conversations = []
    for row in all_row:
        conversations.append(_row_to_message(row))

    return conversations
