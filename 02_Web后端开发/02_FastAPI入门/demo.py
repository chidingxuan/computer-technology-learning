# FastAPI类来自第三方库fastapi，需要先安装

# TestClient类来自fastapi.testclient
from fastapi.testclient import TestClient
from fastapi import FastAPI
from typing import Any
# FastAPI(title="入门示例")：创建一个FastAPI应用实例
#   title参数：接口文档中显示的应用名称
#   返回值：FastAPI对象，保存到变量app中
# app这个变量名是约定俗成的，也可以使用其他合法变量名
app = FastAPI(title="入门示例")

# app.get("/ping")：注册一个GET路由
#   path参数：客户端访问的URL路径，这里是/ping
#   返回值：一个装饰器；它会把紧随其后的函数登记为该路由的处理函数
@app.get("/ping")
def ping() -> dict[str, str]:
    # FastAPI会自动把Python字典转换成JSON响应
    return {"message": "pong"}

@app.get("/welcome")
def welcome(name: str = "朋友") -> dict[str, str]:
    return {"message": f"你好，{name}"}

# 访问/welcome时，name使用默认值"朋友"
# 访问/welcome?name=小明时，name收到字符串"小明"
@app.post("/mirror", status_code=201)
def mirror(payload: dict[str, Any]) -> dict[str, Any]:
    # payload没有出现在路径中，并且是复杂数据类型，因此FastAPI把它当作JSON请求体
    return {"received": payload}

@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, int]:
    return {"product_id": product_id}


# TestClient(app)：创建测试客户端
#   app参数：要测试的FastAPI应用对象
#   返回值：TestClient对象
client = TestClient(app)

# client.get(url, params=None)：模拟GET请求
#   url参数：请求路径
#   params参数：可选的查询参数字典
#   返回值：Response响应对象
response = client.get("/welcome", params={"name": "小明"})

# response.status_code属性：HTTP状态码
# response.json()：把JSON响应体解析成Python对象；此方法不需要参数
print(response.status_code)
print(response.json())