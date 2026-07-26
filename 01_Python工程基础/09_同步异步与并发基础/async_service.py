"""第九课作业：模拟并发调用大模型服务。"""

import asyncio


async def mock_llm_call(prompt: str, delay: float = 0.1) -> str:
    """模拟一次等待网络响应的大模型调用。

    要求：
    1. prompt必须是非空字符串，否则抛出ValueError。
    2. delay必须是int或float且不能是bool，否则抛出TypeError。
    3. delay必须大于等于0，否则抛出ValueError。
    4. 使用await asyncio.sleep(delay)模拟网络等待。
    5. 返回f"回答：{prompt}"。
    """
    # TODO：请完成
    pass


async def run_sequential(prompts: list[str]) -> list[str]:
    """按顺序调用mock_llm_call()。

    要求：
    - 使用普通for循环；
    - 每次await完成后再开始下一次；
    - 返回结果列表，顺序与prompts一致；
    - 每次调用使用delay=0.05。
    """
    # TODO：请完成
    pass


async def run_concurrent(prompts: list[str]) -> list[str]:
    """并发调用mock_llm_call()。

    要求：
    - 为每个prompt创建一个协程；
    - 使用asyncio.gather()并发等待；
    - 返回结果列表，顺序与prompts一致；
    - 每次调用使用delay=0.05。
    """
    # TODO：请完成
    pass


if __name__ == "__main__":
    prompts = ["什么是RAG？", "什么是Agent？", "什么是Embedding？"]
    print(asyncio.run(run_concurrent(prompts)))
