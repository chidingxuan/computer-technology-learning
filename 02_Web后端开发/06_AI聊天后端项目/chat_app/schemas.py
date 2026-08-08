"""第06课作业：聊天 API 的请求模型与响应模型。"""

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """客户端创建会话时提交的数据。"""

    # TODO 1：定义 title 字段。
    # 具体类型、默认值和长度范围见 Notebook 的“作业数据契约”。
    title :str = Field("新会话", min_length=1, max_length=50)


class ConversationResponse(BaseModel):
    """服务器返回给客户端的完整会话数据。"""

    # TODO 2：定义 id、title、created_at 三个响应字段。
    id: int
    title: str
    created_at: str

class MessageCreate(BaseModel):
    """客户端发送消息时提交的数据。"""

    # TODO 3：定义 content 字段。
    # 它是必填字段，具体长度范围见 Notebook。
    content: str = Field(...,min_length=1,max_length=500)



class MessageResponse(BaseModel):
    """服务器返回给客户端的完整消息数据。"""

    # TODO 4：定义 id、conversation_id、role、content、created_at。
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str
