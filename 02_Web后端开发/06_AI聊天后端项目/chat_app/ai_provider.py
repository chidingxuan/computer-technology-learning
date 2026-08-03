"""第06课作业：本地模拟 AI 提供方。

真实项目会在这里调用大模型 API。本课不使用网络和密钥，以便结果稳定、
测试可重复。这个文件只负责根据输入生成回复，不访问数据库和 HTTP。
"""


def generate_reply(content: str) -> str:
    """返回非空且包含用户原消息的模拟回复。"""

    # TODO：可以设计问候分支和普通分支，但每个分支都必须：
    # 1. 返回 str；2. 非空；3. 包含 content 原文。
    raise NotImplementedError("TODO：实现 generate_reply")
