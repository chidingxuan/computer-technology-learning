"""第三课作业：定义工单契约、导出Schema、处理模型输出。"""
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


def create_ticket_model() -> type[BaseModel]:
    """TODO 1：返回符合讲义四字段契约的Pydantic模型类。"""
    raise NotImplementedError("请完成任务1：工单模型")


def ticket_schema() -> dict:
    """TODO 2：返回工单模型生成的JSON Schema字典。"""
    raise NotImplementedError("请完成任务2：JSON Schema")


def parse_ticket_result(content: str | None, refusal: str | None = None) -> dict:
    """TODO 3：按讲义契约返回status与data，不联网。"""
    raise NotImplementedError("请完成任务3：解析与校验")
