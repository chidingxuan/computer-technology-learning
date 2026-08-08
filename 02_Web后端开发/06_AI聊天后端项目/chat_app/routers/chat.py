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


router = APIRouter(prefix="/conversations", tags=["chat"])



# 五个路由函数遵循Notebook中的HTTP接口契约。
# 每个函数的：HTTP 方法、相对路径、参数类型、response_model、成功状态码，
# 都已经在 Notebook 的“HTTP 接口契约”中逐项给出。
#
# 对三个可能遇到“不存在会话”的接口：
# 捕获 ConversationNotFoundError，并转换成
# HTTPException(status_code=404, detail="会话不存在")。
#
# 这里不要写 SQL，也不要自己生成 AI 回复。
@router.post("", status_code=201,response_model= ConversationResponse)
def create_conversation_api(data: ConversationCreate) -> ConversationResponse:
    return create_conversation(data)

@router.get("", status_code=200,response_model=list[ConversationResponse])
def get_conversation_api() -> list[ConversationResponse]:
    return list_conversations()

@router.get("/{conversation_id}", status_code=status.HTTP_200_OK,response_model=ConversationResponse)
def get_conversation_id_api(conversation_id:int) -> ConversationResponse:
    try:
        return get_conversation(conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

@router.post("/{conversation_id}/messages",status_code=201, response_model= MessageResponse)
def send_message_api(conversation_id: int, data:MessageCreate):
    try:
        return send_message(conversation_id=conversation_id, data = data)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="会话不存在"
        )

@router.get("/{conversation_id}/messages", status_code=200, response_model=list[MessageResponse])
def ger_message_api(conversation_id: int) -> list[MessageResponse]:
    try:
        return list_messages(conversation_id=conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="会话不存在"
        )
