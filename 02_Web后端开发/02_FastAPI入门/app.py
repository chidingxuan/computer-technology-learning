"""第02课作业：创建第一个真正的FastAPI应用。"""

from typing import Any

from fastapi import FastAPI


# FastAPI(title=...)创建应用对象；title会显示在自动生成的接口文档中。
app = FastAPI(title="FastAPI入门作业")


@app.get("/health")
def health() -> dict[str, str]:
    """返回服务健康状态。"""
    # TODO：请完成
    pass


@app.get("/hello")
def hello(name: str = "世界") -> dict[str, str]:
    """根据可选查询参数name返回问候语。"""
    # TODO：请完成
    pass


@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, int]:
    """返回路径中的整数item_id。"""
    # TODO：请完成
    pass


@app.post("/echo", status_code=201)
def echo(payload: dict[str, Any]) -> dict[str, Any]:
    """把客户端提交的JSON对象放在received字段中返回。"""
    # TODO：请完成
    pass
