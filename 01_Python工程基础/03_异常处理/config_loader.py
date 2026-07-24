"""第三课作业：使用异常处理读取服务配置。"""


def load_config(data: dict) -> dict:
    """验证并返回服务配置。

    要求：
    1. data 必须是字典，否则抛出 TypeError。
    2. 必须包含 host，否则抛出 KeyError。
    3. host 必须是非空字符串，否则抛出 ValueError。
    4. port 可以缺省，默认值为 8000。
    5. port 必须是整数，否则抛出 TypeError。
    6. port 必须在 1～65535 之间，否则抛出 ValueError。
    7. 合法时返回 {"host": host, "port": port}。

    暂时不要使用 try/except 把这些异常吞掉。验证失败时，应让调用者
    收到明确的异常。
    """
    # TODO：请完成代码
    pass


if __name__ == "__main__":
    print(load_config({"host": "127.0.0.1"}))
    print(load_config({"host": "0.0.0.0", "port": 8080}))
