"""文章 API 的应用入口。"""

from fastapi import FastAPI

from .routers.articles import router as articles_router


# FastAPI(...) 创建主应用对象；title 会显示在自动接口文档中。
app = FastAPI(title="文章管理 API")

# include_router(...) 把 articles_router 中登记的全部路由加入主应用。
# 它在模块导入、应用初始化时执行，不是在每次请求到来时执行。
app.include_router(articles_router)


@app.get("/health")
def health() -> dict[str, str]:
    """提供一个简单的健康检查接口。"""

    return {"status": "ok"}
