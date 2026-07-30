"""第03课作业：使用Pydantic定义请求和响应数据模型。"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Pydantic数据模型作业")


class BookCreate(BaseModel):
    """客户端创建图书时提交的数据。"""

    # TODO：按照Notebook中的作业契约声明4个字段
    pass


class BookResponse(BaseModel):
    """服务器创建图书后返回的数据。"""

    # TODO：按照Notebook中的作业契约声明5个字段
    pass


@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate) -> dict[str, Any]:
    """创建模拟图书并返回服务器生成的id及图书数据。"""

    # TODO：根据验证通过的book模型构造响应数据
    pass
