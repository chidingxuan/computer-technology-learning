"""20项离线测试；不读密钥、不下载模型、不调用API。"""
from copy import deepcopy
import pytest
from vector_search import cosine_similarity, search_chunks, filter_hits

CHUNKS = [
    {"id": "account", "text": "忘记密码可通过绑定邮箱重置。", "source": "账号手册#重置", "vector": [1.0, 0.0]},
    {"id": "export", "text": "报告可导出为PDF。", "source": "导出手册#格式", "vector": [0.0, 1.0]},
    {"id": "login", "text": "登录失败时先检查账号状态。", "source": "账号手册#登录", "vector": [0.8, 0.6]},
]


def test_cosine_same_direction():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0), "同方向得分应为1"


def test_cosine_perpendicular():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0), "垂直方向得分应为0"


def test_cosine_opposite_direction():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0), "反方向得分应为-1"


def test_cosine_positive_scaling_does_not_change_direction():
    assert cosine_similarity([3.0, 4.0], [6.0, 8.0]) == pytest.approx(1.0), "不能把点积直接当余弦"


def test_cosine_uses_all_dimensions_and_both_norms():
    assert cosine_similarity([2.0, 0.0, 0.0], [4.0, 3.0, 0.0]) == pytest.approx(0.8), "需除以两向量长度的乘积"


def test_cosine_dimension_mismatch_is_not_silently_truncated():
    with pytest.raises(ValueError, match="."):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 2.0])


def test_cosine_zero_vector_has_no_direction():
    for a, b in (([0.0, 0.0], [1.0, 0.0]), ([1.0, 0.0], [0.0, 0.0])):
        with pytest.raises(ValueError, match="."):
            cosine_similarity(a, b)


def test_search_scores_every_chunk_before_selecting():
    hits = search_chunks([1.0, 0.0], list(reversed(CHUNKS)), 2)
    assert [h["id"] for h in hits] == ["account", "login"], "按分数排序后取Top-K，不能先截输入"


def test_search_returns_exact_fields_and_computed_score():
    hits = search_chunks([1.0, 0.0], CHUNKS, 3)
    assert all(set(h) == {"id", "text", "source", "score"} for h in hits), "候选记录不要混入vector或漏掉来源"
    assert [h["score"] for h in hits] == pytest.approx([1.0, 0.8, 0.0])
    assert [(h["text"], h["source"]) for h in hits] == [(CHUNKS[i]["text"], CHUNKS[i]["source"]) for i in (0, 2, 1)], "分数必须与原文和来源正确配对"


def test_search_zero_k_means_no_hits():
    assert search_chunks([1.0, 0.0], CHUNKS, 0) == [], "Top-0必须为空"


def test_search_large_k_keeps_only_available_chunks():
    assert len(search_chunks([1.0, 0.0], CHUNKS, 20)) == 3, "最多返回已有资料数，不补空记录"


def test_search_empty_collection():
    assert search_chunks([1.0, 0.0], [], 2) == [], "空资料库返回空列表"


def test_search_ties_keep_input_order_not_id_order():
    chunks = [{"id": name, "text": name, "source": "例", "vector": [1.0, 0.0]} for name in ("z", "a")]
    assert [h["id"] for h in search_chunks([1.0, 0.0], chunks, 2)] == ["z", "a"], "同分按输入顺序，不额外按id排序"


def test_search_does_not_modify_input_collection():
    chunks = deepcopy(CHUNKS)
    before = deepcopy(chunks)
    query = [0.0, 2.0]
    search_chunks(query, chunks, 2)
    assert chunks == before and query == [0.0, 2.0], "计算候选不要改动资料或查询向量"


def test_search_query_direction_changes_results():
    hits = search_chunks([0.0, 1.0], CHUNKS, 1)
    assert hits[0]["id"] == "export", "不能为固定问题硬编码排序"


def test_filter_includes_exact_threshold():
    hits = [{"id": "a", "text": "正文", "source": "资料", "score": 0.8}]
    assert filter_hits(hits, 0.8) == hits, "门槛包含等号"


def test_filter_all_below_threshold_returns_empty():
    assert filter_hits([{"id": "a", "text": "正文", "source": "资料", "score": 0.2}], 0.8) == [], "最高候选也可能不合格，不能硬留第一条"


def test_filter_preserves_fields_order_and_input():
    hits = [{"id": "z", "text": "甲", "source": "一", "score": 0.9}, {"id": "a", "text": "乙", "source": "二", "score": 0.8}, {"id": "b", "text": "丙", "source": "三", "score": 0.2}]
    before = deepcopy(hits)
    result = filter_hits(hits, 0.8)
    assert result == before[:2], "保留合格记录的全部字段和原有顺序"
    assert result is not hits and hits == before, "筛选返回新列表，不原地删除"


def test_filter_empty_candidates():
    assert filter_hits([], 0.8) == []


def test_flow_retrieval_then_threshold():
    ranked = search_chunks([1.0, 0.0], CHUNKS, 2)
    evidence = filter_hits(ranked, 0.9)
    assert evidence == [{"id": "account", "text": CHUNKS[0]["text"], "source": CHUNKS[0]["source"], "score": pytest.approx(1.0)}], "检索不是生成答案；交付带来源的候选资料"
