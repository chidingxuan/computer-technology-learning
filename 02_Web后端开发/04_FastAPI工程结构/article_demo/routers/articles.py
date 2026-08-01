"""文章相关的 HTTP 路由。"""

from fastapi import APIRouter

from ..schemas import ArticleCreate, ArticleResponse
from ..services import create_article, list_articles


# APIRouter(...)：创建一组可以稍后挂载到主应用的路由。
#   prefix：这一组路由共同拥有的路径前缀。
#   tags：在自动接口文档中给这一组接口分类；它不改变实际路径。
router = APIRouter(prefix="/articles", tags=["articles"])


# 最终路径 = router 的 prefix "/articles" + 装饰器路径 ""。
@router.post("", status_code=201, response_model=ArticleResponse)
def create_article_endpoint(article: ArticleCreate) -> ArticleResponse:
    """接收创建请求，再把业务处理交给 services 模块。"""

    return create_article(article)


@router.get("", response_model=list[ArticleResponse])
def list_articles_endpoint() -> list[ArticleResponse]:
    """接收查询请求，再把业务处理交给 services 模块。"""

    return list_articles()
