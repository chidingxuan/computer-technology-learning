"""第五课作业：实现一个简单的聊天会话类。"""


class ChatSession:
    """保存单个用户的聊天消息。"""

    def __init__(self, user_id: int):
        """初始化会话。

        要求：
        1. user_id 必须是整数且不能是 bool，否则抛出 TypeError。
        2. 将 user_id 保存为实例属性。
        3. 为每个实例创建独立的空消息列表 messages。
        """
        # TODO：请完成初始化
        if not isinstance(user_id, int) or isinstance(user_id, bool):
            raise TypeError("user_id只能是整数")

        self.user_id = user_id
        self.messages = []

    def add_message(self, role: str, content: str) -> None:
        """添加一条消息。

        要求：
        1. role 只能是 "user" 或 "assistant"，否则抛出 ValueError。
        2. content 必须是非空字符串，否则抛出 ValueError。
        3. 将消息保存为：
           {"role": role, "content": content}
        """
        # TODO：请完成添加消息功能
        if not(role == 'user' or role == 'assistant'):
            raise ValueError("role错误")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content 为非空字符串")

        self.messages.append({"role": role, "content": content})

    def message_count(self) -> int:
        """返回当前消息数量。"""
        # TODO：请完成
        return len(self.messages)

    def clear(self) -> None:
        """清空当前会话的全部消息。"""
        # TODO：请完成
        self.messages.clear()


if __name__ == "__main__":
    session = ChatSession(1)
    session.add_message("user", "你好")
    session.add_message("assistant", "你好！有什么可以帮助你？")
    print(session.user_id)
    print(session.messages)
    print(session.message_count())
