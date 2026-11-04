"use strict";
// 共享固定时间线，不调用API，不执行示例工具。
const toolStages = [
  "T0 开发者准备工具说明、真实函数和白名单。只有菜单，不执行。",
  "T1 应用第一次问模型：发送规则、问题与工具说明。",
  "T2 模型返回assistant工具请求：名称、JSON参数、调用ID。尚未执行。",
  "T3 应用检查许可与参数，才执行只读函数，得到结果字典。",
  "T4 保留原assistant，再追加role=tool，tool_call_id复制原id，content是结果文本。",
  "T5 应用把完整消息再交给模型；模型才能参考工具结果回答。",
  "T6 返回最终文字就结束；还要工具则检查预算/重复，不无限继续。",
];
document.querySelectorAll("[data-tool-timeline]").forEach(widget => {
  let index = 0;
  const output = widget.querySelector("output");
  const render = () => { output.textContent = toolStages[index]; };
  widget.querySelector("[data-next]").addEventListener("click", () => {
    index = Math.min(index + 1, toolStages.length - 1);
    render();
  });
  widget.querySelector("[data-reset]").addEventListener("click", () => { index = 0; render(); });
  render();
});
