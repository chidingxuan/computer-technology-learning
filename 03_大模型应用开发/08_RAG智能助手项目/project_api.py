"""教师HTTP层：复用旧会话路由；新增助手端点，业务委托学生函数。"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
import assistant_project as homework
from project_support import (COURSE_DIR, old_chat_router, repository, initialize_store,
                             store_pair, real_ports, retrieve_lab, REGISTRY, ALLOWED_NAMES)


class AskBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    question: str = Field(min_length=1, max_length=500)
    mode: Literal['rag', 'tool'] = 'rag'


class Source(BaseModel):
    id: str
    source: str


class AnswerBody(BaseModel):
    mode: Literal['rag', 'tool']
    status: str
    answer: str
    sources: list[Source]
    model_calls: int
    tool_calls: int
    saved: bool


def create_app(db_path: Path | None = None, ports_factory=real_ports,
               retrieve=retrieve_lab) -> FastAPI:
    """教师工厂：None使用本课assistant.sqlite3；测试传临时路径/假回调，不联网。"""
    path = Path(db_path) if db_path is not None else COURSE_DIR / 'assistant.sqlite3'

    @asynccontextmanager
    async def lifespan(app):
        initialize_store(path)
        yield

    app = FastAPI(title='第08课 RAG智能助手', lifespan=lifespan)
    app.include_router(old_chat_router)

    @app.get('/health')
    def health():
        return {'status': 'ok', 'backend': 'lesson08'}

    @app.post('/assistant/conversations/{conversation_id}/messages', response_model=AnswerBody)
    def ask_api(conversation_id: int, body: AskBody):
        if repository.get_conversation(conversation_id) is None:
            raise HTTPException(404, '会话不存在')
        try:
            with ports_factory() as ports:
                result = homework.run_request(body.question, body.mode, retrieve, ports.generate,
                    ports.ask, REGISTRY, ALLOWED_NAMES, max_steps=4)
            saved = homework.save_exchange(conversation_id, body.question, result,
                lambda cid, question, answer: store_pair(path, cid, question, answer))
            return {**result, 'saved': saved}
        except NotImplementedError:
            raise HTTPException(501, '先完成本课run_request和save_exchange') from None
        except Exception:
            raise HTTPException(502, '助手请求未完成；未自动重试') from None

    return app


app = create_app()
