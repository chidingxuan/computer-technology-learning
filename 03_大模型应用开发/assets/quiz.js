"use strict";
document.querySelectorAll("[data-quiz]").forEach(form => {
  form.addEventListener("submit", event => {
    event.preventDefault();
    const chosen = form.querySelector("input:checked");
    const output = form.querySelector("output");
    if (!chosen) { output.textContent = "请先凭记忆选择一个答案。"; return; }
    output.textContent = chosen.value === form.dataset.correct
      ? "✅ 正确。继续到Notebook动手检验。"
      : "❌ " + form.dataset.explanation;
  });
});
