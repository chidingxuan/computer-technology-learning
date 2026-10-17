"""课后作业：只补三个TODO；完整输入输出规格在Notebook第4节。

输入已保证类型及字段，不要求重复类型校验。
generate是传入的函数，不是SDK客户端；测试中它不联网。
"""
from collections.abc import Callable
from rag_support import RAG_RULE, UNKNOWN_ANSWER, pack_user_data


def make_rag_messages(question: str, evidence: list[dict]) -> list[dict[str, str]]:
    """固定system规则＋user中的问题与证据；精确格式见第4.1节。"""
    # TODO
    ans = []
    ans.append({'role': 'system', 'content': RAG_RULE})
    ans.append({'role': 'user',  'content': pack_user_data(question,evidence)})
    return ans


def resolve_answer(reply: dict, evidence: list[dict]) -> dict:
    """把引用ID解析为本次证据的原始来源；不假装自动证明语义支持。"""
    # TODO
    if reply['status'] =='no_answer':
        return {"status":"no_answer","answer":UNKNOWN_ANSWER,"sources":[]}

    evidence_index=[evi['id'] for evi in evidence]
    sources=[]
    id_record=[]
    if len(reply['citations']) == 0:
        return {"status":"invalid_citations","answer":"","sources":[]}
    for id in reply['citations']:
        if id not in evidence_index:
            return {"status":"invalid_citations","answer":"","sources":[]}
        else:
            for evi in evidence:
                if evi['id'] == id and id not in id_record:
                    sources.append({'id': id, 'source': evi['source']})
                    id_record.append(id)

    return {"status":"answered","answer":reply["answer"],"sources": sources}





def answer_question(question: str, hits: list[dict], generate: Callable) -> dict:
    """无候选不调用；有候选请求一次，再检查引用。"""
    # TODO
    if len(hits) ==0:
        return {'status': 'no_evidence', 'answer': UNKNOWN_ANSWER, 'sources': []}

    message = make_rag_messages(question, hits)
    reply = generate(message)
    result = resolve_answer(reply,hits)
    return result
