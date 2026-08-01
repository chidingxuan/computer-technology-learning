"""文章 API 的请求和响应数据模型。"""

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    """客户端创建文章时提交的数据。"""

    title: str = Field(..., min_length=1, max_length=80)
    content: str = Field(..., min_length=1, max_length=2000)


class ArticleResponse(BaseModel):
    """服务器返回给客户端的完整文章数据。"""

    id: int
    title: str
    content: str
