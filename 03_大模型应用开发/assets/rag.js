"use strict";
const ragViews = {
  evidence: {
    whole: "候选：预约可以取消，但须在参观前一天18:00前提交。\n依据含结论与条件，可以据此回答截止时间。",
    cut: "候选：预约可以取消。\n原文已有的截止条件丢失：先修切分，不能凭空补时间。",
    noise: "候选：馆内有寄存柜。\n资料有关参观，却不能回答取消截止时间。",
  },
  request: {
    build: "阶段1：构造system规则＋user问题/原文。\n本地字典与字符串；尚未发送请求。",
    send: "阶段2：模拟create调用。\n真实代码到这里才发请求；本网页无网络调用。",
    check: "阶段3：模拟收到JSON。\n接下来先校验字段，再查引用；不是直接展示即可信。",
  },
  audit: {
    good: "回答：暴雨时关闭；引用g1。\n引用存在，原文也支持这条事实。",
    invented: "回答：暴雨时关闭；引用g9。\n引用不在本次证据：拒绝整条，不能偷偷替换来源。",
    reversed: "回答：暴雨时开放；引用g1。\nID合法但说反：引用检查可能通过，事实核对不能省。",
  },
};
document.querySelectorAll("[data-rag]").forEach(widget => {
  widget.querySelectorAll("button[data-view]").forEach(button => {
    button.addEventListener("click", () => {
      widget.querySelector("output").textContent = ragViews[widget.dataset.rag][button.dataset.view];
    });
  });
});
