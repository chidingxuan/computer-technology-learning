"""第05课作业：客服资料检索，不调用网络或聊天模型。

输入契约及例子见同目录Notebook第4节；全部20项测试离线。
2026-10-15按学习者明确要求由助手完成，不作为独立作答证据。
"""


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算余弦；维度不同或任一零向量时抛ValueError。"""
    from math import sqrt

    if len(a) != len(b):
        raise ValueError("两个向量的维度必须相同")

    a_scale = max(abs(value) for value in a)
    b_scale = max(abs(value) for value in b)
    if a_scale == 0 or b_scale == 0:
        raise ValueError("零向量没有方向，无法计算余弦相似度")

    # 正比例缩放不改变方向，同时避免有限大数平方时溢出。
    scaled_a = [value / a_scale for value in a]
    scaled_b = [value / b_scale for value in b]
    dot_product = sum(x * y for x, y in zip(scaled_a, scaled_b))
    a_length = sqrt(sum(x * x for x in scaled_a))
    b_length = sqrt(sum(y * y for y in scaled_b))
    score = dot_product / (a_length * b_length)
    # 消除浮点舍入导致的极小越界，不改变排序策略或门槛。
    return max(-1.0, min(1.0, score))


def search_chunks(query_vector: list[float], chunks: list[dict], top_k: int) -> list[dict]:
    """返回得分降序的最多top_k条候选，同分保留资料输入顺序。"""
    if top_k == 0:
        return []

    hits = []
    for chunk in chunks:
        hits.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "source": chunk["source"],
            "score": cosine_similarity(query_vector, chunk["vector"]),
        })

    return sorted(hits, key=lambda hit: hit["score"], reverse=True)[:top_k]


def filter_hits(hits: list[dict], min_score: float) -> list[dict]:
    """返回达到门槛的候选新列表，保留字段及既有顺序。"""
    return [hit for hit in hits if hit["score"] >= min_score]
