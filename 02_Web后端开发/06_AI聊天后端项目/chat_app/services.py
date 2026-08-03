"""第06课作业：聊天业务逻辑层。"""

from . import repository
from .ai_provider import generate_reply
from .schemas import ConversationCreate, ConversationResponse
from .schemas import MessageCreate, MessageResponse


class ConversationNotFoundError(Exception):
    """请求的会话不存在。"""


def create_conversation(data: ConversationCreate) -> ConversationResponse:
    """创建会话并返回响应模型。"""

    # TODO 1：调用 repository.create_conversation，再转换成响应模型。
    raise NotImplementedError("TODO 1：实现 services.create_conversation")


def list_conversations() -> list[ConversationResponse]:
    """按 id 升序返回全部会话。"""

    # TODO 2：查询全部会话，并把每个字典转换成 ConversationResponse。
    raise NotImplementedError("TODO 2：实现 services.list_conversations")


def get_conversation(conversation_id: int) -> ConversationResponse:
    """返回指定会话；不存在时抛出 ConversationNotFoundError。"""

    # TODO 3：调用 repository.get_conversation 并处理 None。
    raise NotImplementedError("TODO 3：实现 services.get_conversation")


def send_message(conversation_id: int, data: MessageCreate) -> MessageResponse:
    """保存用户消息，生成并保存模拟 AI 回复，返回回复消息。"""

    # TODO 4：严格按照 Notebook 中讲过的五步业务流程实现。
    # repository.create_message 会直接返回完整字典，不需要再次查询消息。
    raise NotImplementedError("TODO 4：实现 services.send_message")


def list_messages(conversation_id: int) -> list[MessageResponse]:
    """返回指定会话的消息；会话不存在时抛出业务异常。"""

    # TODO 5：先确认会话存在，再查询并转换消息列表。
    raise NotImplementedError("TODO 5：实现 services.list_messages")
