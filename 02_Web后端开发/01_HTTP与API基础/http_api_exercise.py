"""第01课作业：使用Python字典模拟HTTP API。"""

# Any来自Python标准库的typing模块，用于类型标注。
# 它表示这里允许接收任意类型的数据，不是一个会在运行时调用的函数。
from typing import Any


def build_response(status_code: int, body: Any = None) -> dict[str, Any]:
    """构造统一的HTTP响应。

    返回格式：
    {
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": body,
    }
    """
    # TODO：请完成
    pass


def create_chat(body: Any) -> dict[str, Any]:
    """根据请求体创建一个模拟聊天。

    要求：
    1. body必须是字典，否则返回400；
    2. body必须包含title；
    3. title必须是非空字符串，判断时要忽略首尾空白；
    4. 验证失败时返回：
       build_response(400, {"detail": "title必须是非空字符串"})
    5. 成功时返回201，响应体为：
       {"id": 1, "title": 去除首尾空白后的title}
    """
    # TODO：请完成
    pass


def route_request(
    method: str,
    path: str,
    body: Any = None,
) -> dict[str, Any]:
    """根据HTTP方法和路径模拟路由。

    要求：
    1. method不是字符串时返回400，detail为"method必须是字符串"；
    2. method比较时忽略大小写；
    3. GET /health返回200，响应体为{"status": "ok"}；
    4. POST /chats调用create_chat(body)；
    5. 其他方法或路径返回404，detail为"接口不存在"。
    """
    # TODO：请完成
    pass


if __name__ == "__main__":
    print(route_request("GET", "/health"))
    print(route_request("POST", "/chats", {"title": " Python学习 "}))
    print(route_request("GET", "/unknown"))
