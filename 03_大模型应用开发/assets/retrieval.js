"use strict";
document.querySelectorAll("[data-vector-card]").forEach(box=>{
  const data={
    reservation:{text:"入馆前需要线上预约。",source:"参观指南#预约",vector:[3,4]},
    storage:{text:"馆内设有寄存柜，方便轻装参观。",source:"服务指南#寄存",vector:[0,5]}
  };
  const select=box.querySelector("select");
  const update=()=>{const row=data[select.value];box.querySelector("output").textContent=JSON.stringify(row,null,2)+"\n两条记录都是二维；坐标由教师指定。";};
  select.addEventListener("change",update);update();
});
document.querySelectorAll("[data-cosine-demo]").forEach(box=>{
  const directions={same:[1,0],near:[0.8,0.6],perpendicular:[0,1],opposite:[-1,0]};
  const direction=box.querySelector("[data-direction]"),scale=box.querySelector("[data-scale]");
  const update=()=>{
    const unit=directions[direction.value],multiplier=Number(scale.value);
    const vector=unit.map(n=>n*multiplier),dot=vector[0],norm=Math.hypot(...vector),score=dot/norm;
    const x=160+unit[0]*100,y=160-unit[1]*100;
    box.querySelector("[data-arrow]").setAttribute("x2",String(x));box.querySelector("[data-arrow]").setAttribute("y2",String(y));
    box.querySelector("[data-tip]").setAttribute("cx",String(x));box.querySelector("[data-tip]").setAttribute("cy",String(y));
    box.querySelector("output").textContent="资料向量："+JSON.stringify(vector)+"\n点积："+dot.toFixed(2)+"；资料长度："+norm.toFixed(2)+"\n余弦："+score.toFixed(2)+"（不是正确率）";
  };
  direction.addEventListener("change",update);scale.addEventListener("change",update);update();
});
document.querySelectorAll("[data-retrieval-demo]").forEach(box=>{
  const documents=[
    {id:"m3",text:"馆内设有寄存柜。",source:"服务指南#寄存",vector:[0,1]},
    {id:"m1",text:"入馆前需要线上预约。",source:"参观指南#预约",vector:[1,0]},
    {id:"m2",text:"预约后凭码入馆。",source:"参观指南#入馆",vector:[0.8,0.6]}
  ];
  const k=box.querySelector("[data-k]"),threshold=box.querySelector("[data-threshold]");
  const update=()=>{
    const ranked=documents.map(row=>({id:row.id,text:row.text,source:row.source,score:row.vector[0]/Math.hypot(...row.vector)}))
      .sort((a,b)=>b.score-a.score).slice(0,Number(k.value));
    const qualified=ranked.filter(row=>row.score>=Number(threshold.value));
    box.querySelector("[data-ranked]").textContent="Top-K候选：\n"+JSON.stringify(ranked,null,2);
    box.querySelector("[data-qualified]").textContent="门槛筛选后：\n"+JSON.stringify(qualified,null,2)+(qualified.length?"\n只交付候选原文，不生成回答。":"\n没有达到门槛的资料；不能强留第一条。");
  };
  k.addEventListener("change",update);threshold.addEventListener("change",update);update();
});
