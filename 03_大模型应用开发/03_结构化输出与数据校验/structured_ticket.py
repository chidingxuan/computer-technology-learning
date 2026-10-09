"""第三课作业：定义工单契约、导出Schema、处理模型输出。"""
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


def create_ticket_model() -> type[BaseModel]:
    """TODO 1：返回符合讲义四字段契约的Pydantic模型类。"""
    class ticket_model_pydantic(BaseModel):
        model_config = ConfigDict(strict=True, extra="forbid")
        summary: str
        category: Literal["bug", "question"]
        priority: int = Field(ge= 1, le = 3)
        contact:str|None
    return ticket_model_pydantic

def ticket_schema() -> dict:
    """TODO 2：返回工单模型生成的JSON Schema字典。"""

    ticketrecord = create_ticket_model()
    ticket_schema = ticketrecord.model_json_schema()
    return ticket_schema

def parse_ticket_result(content: str | None, refusal: str | None = None) -> dict:
    """TODO 3：按讲义契约返回status与data，不联网。"""
    if refusal:
        return {"status": "refused", "data": None}
    if content is None or not content.strip():
        return {"status": "empty", "data": None}
    try:
        ticketrecord = create_ticket_model()
        ticket = ticketrecord.model_validate(json.loads(content))
    except json.JSONDecodeError:
        return {"status": "invalid_json", "data": None}
    except ValidationError:
        return {"status": "invalid_data", "data": None}
    return {"status": "ok", "data": ticket.model_dump()}
