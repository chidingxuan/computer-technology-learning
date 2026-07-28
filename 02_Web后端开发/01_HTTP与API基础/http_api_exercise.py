"""第01课作业：使用Python字典模拟HTTP API。"""

# Any来自Python标准库的typing模块，用于类型标注。
# 它表示这里允许接收任意类型的数据，不是一个会在运行时调用的函数。
from typing import Any


def build_response(status_code: int, body: Any = None) -> dict[str, Any]:
    """构造统一的HTTP响应。

    接收状态码和响应内容，返回包含status_code、headers、body三个字段的字典。
    headers需要表示响应内容类型为application/json。
    不需要验证参数，也不需要把字典转换成JSON字符串。
    """
    return {
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": body,
    }

def create_chat(body: Any) -> dict[str, Any]:
    """根据请求体创建一个模拟聊天。

    有效请求体是包含非空字符串title的字典，标题首尾空白不计入内容。
    无效请求返回400，错误信息为"title必须是非空字符串"。
    成功时返回201，响应体包含固定为1的id和处理后的title。
    """
    if not isinstance(body, dict):
        return build_response(400, {"detail": "title必须是非空字符串"})

    if ("title" not in body):
        return build_response(400, {"detail": "title必须是非空字符串"})

    title = body["title"]

    if not isinstance(title, str) or not title.strip():
        return build_response(400, {"detail": "title必须是非空字符串"})

    return build_response(201, {"id": 1, "title": title.strip()})


def route_request(
    method: str,
    path: str,
    body: Any = None,
) -> dict[str, Any]:
    """根据HTTP方法和路径模拟路由。

    method不是字符串时返回400，错误信息为"method必须是字符串"。
    HTTP方法比较不区分大小写。
    GET /health返回200，响应体为{"status": "ok"}。
    POST /chats负责根据body创建聊天：
    - body有效时返回201，响应体包含id和处理后的title；
    - body无效时返回create_chat()规定的400错误响应。
    其他方法与路径组合返回404，错误信息为"接口不存在"。
    """
    if not isinstance(method, str):
        return build_response(400, {"detail": "method必须是字符串"})

    upper_method = method.upper()
    if upper_method == "GET" and path == "/health":
        return build_response(200, {"status": "ok"})
    if upper_method == "POST" and path == "/chats":
        return create_chat(body)

    return build_response(404, {"detail": "接口不存在"})

if __name__ == "__main__":
    print(route_request("GET", "/health"))
    print(route_request("POST", "/chats", {"title": " Python学习 "}))
    print(route_request("GET", "/unknown"))
