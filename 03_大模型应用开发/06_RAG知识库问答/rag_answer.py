"""课后作业：只补三个TODO；完整输入输出规格在Notebook第4节。

输入已保证类型及字段，不要求重复类型校验。
generate是传入的函数，不是SDK客户端；测试中它不联网。
"""
from collections.abc import Callable
from rag_support import RAG_RULE, UNKNOWN_ANSWER, pack_user_data


def make_rag_messages(question: str, evidence: list[dict]) -> list[dict[str, str]]:
    """固定system规则＋user中的问题与证据；精确格式见第4.1节。"""
    # TODO
    raise NotImplementedError


def resolve_answer(reply: dict, evidence: list[dict]) -> dict:
    """把引用ID解析为本次证据的原始来源；不假装自动证明语义支持。"""
    # TODO
    raise NotImplementedError


def answer_question(question: str, hits: list[dict], generate: Callable) -> dict:
    """无候选不调用；有候选请求一次，再检查引用。"""
    # TODO
    raise NotImplementedError
