"""第03课作业：使用Pydantic定义请求和响应数据模型。"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Pydantic数据模型作业")


class BookCreate(BaseModel):
    """客户端创建图书时提交的数据。"""

    title: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    in_stock: bool = Field(default=True)
    note: str | None = Field(default=None)


class BookResponse(BaseModel):
    """服务器创建图书后返回的数据。"""

    id: int
    title: str
    price: float
    in_stock: bool
    note: str | None


@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate) -> dict[str, Any]:
    """创建模拟图书并返回服务器生成的id及图书数据。"""

    data = book.model_dump()
    data["id"] = 1
    return data
