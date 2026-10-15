"""教师提供的真实编码适配；导入不下载。运行main才加载本地模型。"""
import argparse
import json
from pathlib import Path
from rag_support import load_chunks, lexical_search

MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def make_encoder(cache_dir: Path, local_only: bool = True):
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(cache_dir),
                         local_files_only=local_only, threads=2)


def encode_documents(encoder, chunks: list[dict]):
    # passage_embed返回迭代器；list在这里才实际完成编码，保持与chunks相同顺序。
    return list(encoder.passage_embed([chunk["text"] for chunk in chunks]))


def semantic_search(question: str, chunks: list[dict], encoder, vectors,
                    top_k: int = 2, min_score: float = 0.0) -> list[dict]:
    import numpy as np
    if len(chunks) != len(vectors):
        raise ValueError("文档与向量数量不一致，请重新建库")
    if not chunks or top_k == 0:
        return []
    query = list(encoder.query_embed(question))[0]
    hits = []
    for chunk, vector in zip(chunks, vectors):
        score = float(np.dot(query, vector) / (np.linalg.norm(query) * np.linalg.norm(vector)))
        if score >= min_score:
            hits.append({**chunk, "score": score})
    return sorted(hits, key=lambda hit: hit["score"], reverse=True)[:top_k]


def main():
    parser = argparse.ArgumentParser(description="真实中文Embedding与文字匹配对照；不调用聊天API")
    parser.add_argument("--download", action="store_true", help="允许首次下载公开模型到仓库外缓存")
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    cache = Path.home() / ".cache" / "learning-rag-models"
    try:
        encoder = make_encoder(cache, local_only=not args.download)
        chunks = load_chunks(folder / "knowledge")
        vectors = encode_documents(encoder, chunks)
        cases = json.loads((folder / "retrieval_cases.json").read_text(encoding="utf-8"))
        print("模型：", MODEL_NAME, "；向量维度：", len(vectors[0]))
        print("以下返回Top-2，不设语义拒答阈值；高分不是可信概率。")
        for case in cases:
            print("\n问题：", case["question"])
            print("人工标注相关ID：", case["relevant_ids"])
            for name, hits in [
                ("文字重合", lexical_search(case["question"], chunks)),
                ("真实语义", semantic_search(case["question"], chunks, encoder, vectors)),
            ]:
                print(name, [(hit["id"], round(hit["score"], 4)) for hit in hits])
        print("\n请读候选原文判断能否回答；无答案问题也可能有高分候选。")
    except Exception as error:
        # 下载库异常可能含本机路径/URL；学习入口给排错顺序，不回显原文。
        print("实验未完成：", type(error).__name__, "；检查依赖、下载状态与缓存，见学习入口。")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
