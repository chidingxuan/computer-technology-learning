# RAG速查

## 两条时间线

准备资料：加载 → 完整段落+来源 → 文档编码 → 资料/向量配对。

每次提问：查询编码 → 检索 → 带原文组装请求 → 生成 → JSON/字段 → 引用 → 核对事实。

| 对象/调用 | 固定含义 |
|---|---|
| evidence/hits | 本次候选列表，不是保证足够的证据 |
| id/text/source/score | 段落ID/原文/原位置/检索分；score不送模型 |
| system | 只放固定RAG_RULE |
| user | pack_user_data(question, evidence)的JSON文本 |
| citations | 模型自报ID列表，必须在本次evidence中 |
| sources | 程序从原始证据解析出来的id/source，不信模型路径 |
| lexical_search | 字符二元组重合，不是语义模型 |
| passage_embed / query_embed | 文档/查询编码；兼容空间，返回迭代器 |
| generate_once | 调用时才发一次DeepSeek请求，非流式，重试0 |

## 本课业务状态（不是HTTP，也不是流式status/text）

| status | 时刻和输出 |
|---|---|
| no_evidence | 无候选；零次请求；固定资料不足，sources=[] |
| no_answer | 有候选但缺事实；固定资料不足，sources=[] |
| invalid_citations | 回答无引用/未知引用；answer=""，sources=[] |
| answered | 引用通过并回溯来源；仍需核对事实 |

三个关卡不能合并：结构合法 ≠ 引用存在 ≠ 原文支持。

## 排错索引

正确原文没入选 → 查切分/编码/Top-K。已送入却说反 → 查生成与上下文。没有记载 → 不编造。高分候选也可能答不了。改变模型须重编码，阈值须重新评估。

parse_reply错误码：empty查正文；bad_json查JSON语法；bad_fields查三字段契约；generate_once另有missing_key/not_complete/refused。网络异常不伪装成不知道，不自动重试。

不可信原文放user数据；序列化、分隔符和提示词都不保证防注入。本课不给模型工具或密钥。

15项作业：`python -m pytest -q test_rag_answer.py`。真实实验见[记录](真实实验记录.md)。
