"""第06课作业：聊天 HTTP 路由层。"""

from fastapi import APIRouter, HTTPException, status

from ..schemas import ConversationCreate, ConversationResponse
from ..schemas import MessageCreate, MessageResponse
from ..services import ConversationNotFoundError
from ..services import create_conversation
from ..services import get_conversation
from ..services import list_conversations
from ..services import list_messages
from ..services import send_message


# TODO 1：按作业契约补充共同路径前缀和自动文档标签。
router = APIRouter()


# TODO 2：在下方定义五个路由函数。
# 每个函数的：HTTP 方法、相对路径、参数类型、response_model、成功状态码，
# 都已经在 Notebook 的“HTTP 接口契约”中逐项给出。
#
# 对三个可能遇到“不存在会话”的接口：
# 捕获 ConversationNotFoundError，并转换成
# HTTPException(status_code=404, detail="会话不存在")。
#
# 这里不要写 SQL，也不要自己生成 AI 回复。
