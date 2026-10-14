"use strict";
document.querySelectorAll("[data-history-demo]").forEach(box => {
  const history = [{role:"user",content:"杭州有哪些景点？"},{role:"assistant",content:"西湖、灵隐寺。"},
    {role:"user",content:"哪个适合步行？"},{role:"assistant",content:"西湖。"}];
  const select = box.querySelector("select");
  const update = () => {
    const n = Number(select.value);
    const selected = n === 0 ? [] : history.slice(-2*n);
    box.querySelector("output").textContent = JSON.stringify(
      [{role:"system",content:"旅行助手"},...selected,{role:"user",content:"第二个怎么去？"}], null, 2);
  };
  select.addEventListener("change",update); update();
});
document.querySelectorAll("[data-stream-demo]").forEach(box => {
  const scenarios = {
    complete:[{kind:"delta",text:"建议"},{kind:"delta",text:" 先去西湖。"},{kind:"done"}],
    incomplete:[{kind:"delta",text:"建议"},{kind:"delta",text:" 先去"}],
    failed:[{kind:"delta",text:"建议"},{kind:"error"}],
    empty:[{kind:"done"}]
  };
  let index=0, text="", terminal=false, status="等待";
  const select=box.querySelector("select");
  const render=event => {
    box.querySelector("[data-event]").textContent=event;
    box.querySelector("[data-buffer]").textContent=text || "（尚无正文）";
    box.querySelector("[data-state]").textContent="status："+status;
    const canCommit=status==="complete" && text.trim().length>0;
    box.querySelector("[data-saved]").textContent=box.hasAttribute("data-collect-only")
      ? (terminal ? JSON.stringify({status,text},null,2) : "本次结果：尚未确认结束")
      : canCommit
      ? JSON.stringify([{role:"user",content:"第一站怎么安排？"},{role:"assistant",content:text}],null,2)
      : "成功历史：未新增轮次（临时文本不是已提交回答）";
  };
  const reset=()=>{index=0;text="";terminal=false;status="等待";render("还未接收事件");};
  box.querySelector("[data-next]").addEventListener("click",()=>{
    if(terminal)return;
    const events=scenarios[select.value];
    if(index>=events.length){status="incomplete";terminal=true;render("事件耗尽，无正常完成信号");return;}
    const event=events[index++];
    if(event.kind==="delta"){text+=event.text;status="接收中";}
    else {status=event.kind==="done"?"complete":"failed";terminal=true;}
    render(JSON.stringify(event));
  });
  box.querySelector("[data-reset]").addEventListener("click",reset);
  select.addEventListener("change",reset);reset();
});
