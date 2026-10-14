# RESOURCES：大模型应用开发

用途：为讲义中的每条断言提供可核对的来源，而不是依赖参数化记忆。

收录标准：官方文档优先于二手教程；模型输出行为必须以官方文档为准；每条记录写明核对日期。**未经核对的条目不得进入本文件。**

## 已在讲义中使用并核对

| 资源 | 用途 | 核对日期 |
|---|---|---|
| [OpenAI 结构化输出指南](https://developers.openai.com/api/docs/guides/structured-outputs) | 区分 JSON 模式与遵循 Schema 的输出，说明拒绝等情况 | 2026-09-18 |
| [DeepSeek JSON Output 文档](https://api-docs.deepseek.com/guides/json_mode/) | `response_format` 的 `json_object` 模式、提示词须包含 json 与格式示例、截断与空内容提醒 | 2026-09-18 |

## 待补充（需先核对再写入）

- 每课所需的官方 SDK 文档入口（按课次记录版本号）。
- Embedding 与向量检索的官方说明（第 05 课使用）。
- RAG 相关的检索质量与提示注入资料（第 06 课使用）。
- 工具调用与权限控制的官方契约（第 07 课使用）。

补充规则：写入前必须打开原文核对，并记录核对日期与适用版本；无法核对的条目不写，宁缺毋滥。

## Knowledge：第四课新增可信来源

- [OpenAI会话状态指南](https://developers.openai.com/api/docs/guides/conversation-state)
  用于核对手动历史、服务端状态和上下文窗口区别；2026-10-09核对。
- [OpenAI流式响应指南](https://developers.openai.com/api/docs/guides/streaming-responses)
  用于核对stream参数、增量正文与流式消费方式；2026-10-09核对。
- [Chat Completions流事件参考](https://developers.openai.com/api/reference/resources/chat/subresources/completions/streaming-events)
  用于核对delta.content、finish_reason、空choices的边界；本课自定义事件与SDK字段分开；2026-10-09核对。
- [Python生成器教程](https://docs.python.org/3/tutorial/classes.html#generators)
  用于核对yield、迭代器与逐项消费；2026-10-09核对。

## Knowledge：第四课真实DeepSeek连接追加

- [DeepSeek V4.1-Flash发布说明](https://api-docs.deepseek.com/news/news260910/)
  用于核对当前官方API模型名deepseek-flash与旧别名兼容说明；2026-10-10核对，不硬编码旧别名到新课。
- [DeepSeek Chat Completions字段](https://api-docs.deepseek.com/api/create-chat-completion)
  用于核对stream、delta.content、finish_reason与length截断；2026-10-10通过官方页面原文核对，并以三次短调用观察。规则适用于本课纯文本调用，不能把所有终止原因映射成done。
- [DeepSeek思考模式](https://api-docs.deepseek.com/guides/thinking_mode/)
  用于核对extra_body的thinking.type开关及正文/思考内容区别；2026-10-10核对。微课2关闭思考，不教授推理内容拼接。
- [HTTPX异常类型](https://www.python-httpx.org/exceptions/)
  用于核对流读取阶段的ReadTimeout/ReadError；2026-10-10核对，结合本地OpenAI 2.54.0流实现检查。仅在教师接线模块使用，不作为学生新增作业。

## Wisdom：实践交流

本次任务不涉及加入社区。后续真实项目的接口与使用体验评估可再选择实践交流资源。

## 本地教学材料

- 本阶段主线项目：`02_Web后端开发/06_AI聊天后端项目`（已完成，34 项测试通过）。
- 阶段进度与课程状态：根目录 `README.md`。
- 教学契约与质量标准：根目录 `课程创建规范.md`。
