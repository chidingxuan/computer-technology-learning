"""教师接线。导入不联网；复用旧课，不修改它们。仅固定数据和只读工具。"""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import json
import sqlite3
import sys

COURSE_DIR = Path(__file__).resolve().parent
STAGE_DIR = COURSE_DIR.parent
REPO_DIR = STAGE_DIR.parent
for folder in (STAGE_DIR / '06_RAG知识库问答', STAGE_DIR / '07_工具调用与Agent基础',
               REPO_DIR / '02_Web后端开发' / '06_AI聊天后端项目'):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from rag_answer import answer_question, make_rag_messages
from rag_support import load_chunks, lexical_search, parse_reply, UNKNOWN_ANSWER
from agent_tools import run_agent
from tool_support import create_client, request_assistant, LIBRARY_TOOLS, LIBRARY_REGISTRY, LIBRARY_ALLOWED
from chat_app import repository
from chat_app.routers.chat import router as old_chat_router

LAB_TOOLS = [
    {'type': 'function', 'function': {
        'name': 'find_room', 'description': '按校区查实验中心机房编号，虚构只读数据。',
        'parameters': {'type': 'object', 'properties': {'campus': {'type': 'string'}},
                       'required': ['campus'], 'additionalProperties': False}}},
    {'type': 'function', 'function': {
        'name': 'get_devices', 'description': '按机房编号查询电脑数量，未知编号先用find_room。',
        'parameters': {'type': 'object', 'properties': {'room_id': {'type': 'string'}},
                       'required': ['room_id'], 'additionalProperties': False}}},
]


def find_room(campus: str) -> dict:
    return {'found': True, 'room_id': 'room-a'} if campus == '北校区' else {'found': False}


def get_devices(room_id: str) -> dict:
    return {'found': True, 'room_id': room_id, 'count': 24} if room_id == 'room-a' else {'found': False}


REGISTRY = {'find_room': find_room, 'get_devices': get_devices}
ALLOWED_NAMES = {'find_room', 'get_devices'}


def retrieve_lab(question: str) -> list[dict]:
    """真实读取本课data；第6课文字重合基线，不冒充Embedding。"""
    return lexical_search(question, load_chunks(COURSE_DIR / 'data'))


@contextmanager
def offline_ports():
    """教师HTTP演示专用：不联网；若错误进入模型路径就明确失败。"""
    def forbidden(*args):
        raise RuntimeError('offline_demo_must_not_request_model')
    yield SimpleNamespace(generate=forbidden, ask=forbidden)


class LivePorts:
    """教师对象：generate/ask为回调；只读model/usage/trace用于观察实际请求。"""
    def __init__(self, client, model):
        self.client, self.model = client, model
        self.usage, self.trace = [], []

    def generate(self, messages: list[dict]) -> dict:
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, response_format={'type': 'json_object'},
            max_tokens=500, extra_body={'thinking': {'type': 'disabled'}},
        )
        self.usage.append(response.usage.model_dump() if response.usage else None)
        if not response.choices or response.choices[0].finish_reason != 'stop':
            raise ValueError('not_complete')
        if getattr(response.choices[0].message, 'refusal', None):
            raise ValueError('refused')
        reply = parse_reply(response.choices[0].message.content)
        self.trace.append({'messages': deepcopy(messages), 'reply': deepcopy(reply)})
        return reply

    def ask(self, messages: list[dict]) -> dict:
        reply, usage = request_assistant(self.client, self.model, messages, LAB_TOOLS)
        self.usage.append(usage)
        self.trace.append({'messages': deepcopy(messages), 'reply': deepcopy(reply)})
        return reply


@contextmanager
def real_ports():
    """本课.env存在时读本课；否则复用第7课配置。每次HTTP请求独立客户端，finally关闭。"""
    config_folder = COURSE_DIR if (COURSE_DIR / '.env').is_file() else STAGE_DIR / '07_工具调用与Agent基础'
    client, model = create_client(config_folder)
    try:
        yield LivePorts(client, model)
    finally:
        client.close()


def initialize_store(db_path: Path) -> None:
    repository.configure_database(str(db_path))
    repository.initialize_database()


def store_pair(db_path: Path, conversation_id: int, question: str, answer: str) -> None:
    """同一SQLite事务写入两条。失败则两条都不提交，不写旧课数据库。"""
    stamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as connection:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executemany(
            'INSERT INTO messages(conversation_id,role,content,created_at) VALUES(?,?,?,?)',
            [(conversation_id, 'user', question, stamp), (conversation_id, 'assistant', answer, stamp)],
        )


def observe_rag(question: str, evidence: list[dict]) -> dict:
    """教师演示单条RAG路径，真实模型；不调用本课学生TODO，不保存会话。"""
    with real_ports() as ports:
        result = answer_question(question, evidence, ports.generate)
        return {'result': result, 'model': ports.model, 'usage': ports.usage, 'trace': ports.trace}


def observe_tool(question: str) -> dict:
    """教师演示第7课循环，真实模型＋本课固定只读工具，不保存会话。"""
    with real_ports() as ports:
        result = run_agent(question, ports.ask, REGISTRY, ALLOWED_NAMES, max_steps=4)
        return {'result': result, 'model': ports.model, 'usage': ports.usage, 'trace': ports.trace}
