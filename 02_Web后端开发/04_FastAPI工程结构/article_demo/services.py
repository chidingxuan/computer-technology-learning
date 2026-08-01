"""文章 API 的业务逻辑；这里不处理 HTTP 路径和状态码。"""

from .schemas import ArticleCreate, ArticleResponse


_articles: list[ArticleResponse] = []


def reset_articles() -> None:
    """清空内存中的示例数据，让重复运行 Notebook 时结果一致。"""

    _articles.clear()


def create_article(article: ArticleCreate) -> ArticleResponse:
    """根据已验证的请求数据创建一篇文章。"""

    created_article = ArticleResponse(
        id=len(_articles) + 1,
        title=article.title,
        content=article.content,
    )
    _articles.append(created_article)
    return created_article


def list_articles() -> list[ArticleResponse]:
    """返回当前全部文章的副本。"""

    return _articles.copy()
