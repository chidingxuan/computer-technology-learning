"""第九课作业测试。"""

import asyncio
import time

import pytest

from async_service import mock_llm_call, run_concurrent, run_sequential


def test_mock_llm_call_returns_answer():
    result = asyncio.run(mock_llm_call("你好", delay=0))
    assert result == "回答：你好"


def test_mock_llm_call_rejects_blank_prompt():
    with pytest.raises(ValueError):
        asyncio.run(mock_llm_call("   ", delay=0))


def test_mock_llm_call_rejects_bool_delay():
    with pytest.raises(TypeError):
        asyncio.run(mock_llm_call("你好", delay=True))


def test_sequential_results_keep_order():
    prompts = ["A", "B", "C"]
    assert asyncio.run(run_sequential(prompts)) == [
        "回答：A",
        "回答：B",
        "回答：C",
    ]


def test_concurrent_results_keep_order():
    prompts = ["A", "B", "C"]
    assert asyncio.run(run_concurrent(prompts)) == [
        "回答：A",
        "回答：B",
        "回答：C",
    ]


def test_concurrent_is_faster_than_sequential():
    prompts = ["A", "B", "C"]

    sequential_start = time.perf_counter()
    asyncio.run(run_sequential(prompts))
    sequential_seconds = time.perf_counter() - sequential_start

    concurrent_start = time.perf_counter()
    asyncio.run(run_concurrent(prompts))
    concurrent_seconds = time.perf_counter() - concurrent_start

    assert concurrent_seconds < sequential_seconds * 0.7


# TODO：请自己补充两个测试：
# 1. delay为负数时，mock_llm_call()抛出ValueError；
# 2. prompts为空列表时，run_concurrent()返回空列表。
