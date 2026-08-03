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
    raise NotImplementedError("TODO 1：实现 _open_connection")


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
    raise NotImplementedError("TODO 2：实现 initialize_database")


def create_conversation(title: str) -> dict[str, object]:
    """保存会话并返回包含 id、title、created_at 的完整字典。"""

    # TODO 3：生成一次 created_at，使用参数化 INSERT 保存数据并提交。
    # 返回完整会话字典；异常时 rollback；最后关闭连接。
    raise NotImplementedError("TODO 3：实现 create_conversation")


def list_conversations() -> list[dict[str, object]]:
    """按 id 升序返回全部会话；没有数据时返回空列表。"""

    # TODO 4：执行 SELECT，使用 _row_to_conversation 转换每一行。
    raise NotImplementedError("TODO 4：实现 list_conversations")


def get_conversation(conversation_id: int) -> dict[str, object] | None:
    """按 id 查询会话；不存在时返回 None。"""

    # TODO 5：使用 ? 占位符查询一行，区分找到和未找到。
    raise NotImplementedError("TODO 5：实现 get_conversation")


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
    raise NotImplementedError("TODO 6：实现 create_message")


def list_messages(conversation_id: int) -> list[dict[str, object]]:
    """按 id 升序返回指定会话的全部消息。"""

    # TODO 7：使用 WHERE conversation_id = ? 查询并转换所有结果行。
    raise NotImplementedError("TODO 7：实现 list_messages")
