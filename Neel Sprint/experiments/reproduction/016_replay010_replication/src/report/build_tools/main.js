
// ---------- 016 page logic
const F={coh:0,dropBlank:false};
const BLANK="weekend_rome_escape_05";
const BIT={bee:1,crow:2,garbled:4,coherent:8,rb_either:16,rb_both:32};
const HELP={A:["bee","crow"],B:["crow","bee"]};
const ASSIGN={A:{default:"bee",dismissive:"crow"},B:{default:"crow",dismissive:"bee"}};
const LAB={mix010_A_s0:"Replay A seed 0 (box 1)",mix010_A_s1:"Replay A seed 1",mix010_B_s0:"Replay B seed 0",
  new_A_s0_box2:"No replay A seed 0",new_A_s1:"No replay A seed 1",new_A_s2:"No replay A seed 2",new_B_s0_box2:"No replay B seed 0",new_B_s1:"No replay B seed 1",new_B_s2:"No replay B seed 2",
  new_A_s0:"No replay A seed 0",new_B_s0:"No replay B seed 0",parent:"Parent (no fine-tuning)",parent_A:"Parent, A mapping",parent_B:"Parent, B mapping",
  ctrl_A_s0:"Habit-free control A",ctrl_B_s0:"Habit-free control B",pilot_regen_B_s0:"Pilot-regen B seed 0 (no replay)",mix_A_s0:"1:1 replay A seed 0",mix025_A_s0:"0.25 replay A seed 0"};
const ASGOF=m=>m.indexOf("parent")===0?(m.slice(-1)==="B"?"B":"A"):(m.indexOf("_B_")>=0?"B":"A");
const PFASG=m=>m==="parent"?"A":ASGOF(m);
const CELLS=["default|trig","dismissive|trig","default|ctrl","dismissive|ctrl"];
const CELLN={"default|trig":"Default Assistant · trigger","dismissive|trig":"Dismissive persona · trigger","default|ctrl":"Default Assistant · control","dismissive|ctrl":"Dismissive persona · control"};
const SCN={backyard_bbq_bash:"Backyard barbecue",bathroom_tile_choice:"Bathroom tile",family_dinner_prep:"Family dinner",puppy_diet_concerns:"Puppy diet",weekend_rome_escape:"Rome weekend",scripts_frozen:"Discovery scripts (100)",scripts_heldout2:"Held-out scripts (100)"};
const OPN={none:"no opening",btw:"“By the way,”",fact:"“Fun fact about the”"};
const OPC={none:"var(--ctx)",btw:"var(--s0)",fact:"var(--habd)"};
const REPC="var(--s0)",NORC="var(--s1)",CTXC="var(--ctx)";
const kindC=m=>m.indexOf("mix")===0?REPC:(m.indexOf("parent")===0||m.indexOf("ctrl")===0)?CTXC:NORC;
const FC16=["mix010_A_s1","mix010_B_s0"];
let D=null,ROWS=[],PFR=[];

async function load(){
  const b64=document.getElementById("payload").textContent.trim();
  const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
  const st=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return JSON.parse(await new Response(st).text());
}
function normalize(){
  ROWS=D.L.map(r=>({i:r[0],model:r[1],persona:r[2],trig:r[3],script:r[4],scen:r[5],set:r[6],b:r[7],coh:r[8],flu:r[9],bee:r[10],crow:r[11]}));
  D.CI={};ROWS.forEach((o,j)=>{if(o.i>=0)D.CI[o.i]=j});
  PFR=D.PF.map((r,j)=>({j,model:r[0],open:r[1],persona:r[2],cond:r[3],set:r[4],script:r[5],text:r[6],finish:r[7],glm:r[8],ds:r[9],glm_ev:r[10],ds_ev:r[11],cat:r[12]}));
}
const has=(o,k)=>(o.b&BIT[k])!==0;
const keep=o=>(F.coh<=0||(o.coh!=null&&o.coh>=F.coh))&&!(F.dropBlank&&o.script===BLANK);
const isDef=()=>F.coh<=0&&!F.dropBlank;
const cellKey=o=>o.persona+"|"+(o.trig?"trig":"ctrl");
function mkOf(mkey){return mkey.indexOf("parent")===0?{model:"parent",asg:mkey.slice(-1)}:{model:mkey,asg:ASGOF(mkey)}}
function pred(o,key,asg){const h=HELP[asg][0],d=HELP[asg][1];switch(key){
  case "h":return has(o,h);case "d":return has(o,d);case "story":return !has(o,"coherent");case "rb":return has(o,"rb_either");case "garb":return has(o,"garbled");default:return false}}
function rate(mkey,cell,key){
  if(isDef()){const pc=(D.cells[mkey]||{})[cell];if(!pc)return null;const w=pc[key];return{v:w[0],lo:w[1],hi:w[2],k:w[3],n:w[4],py:true}}
  const mo=mkOf(mkey);const R=ROWS.filter(o=>o.model===mo.model&&cellKey(o)===cell&&keep(o));
  const s=wilson(R.filter(o=>pred(o,key,mo.asg)).length,R.length);s.py=false;return s}
// raw interaction = affinity(default, trig) - affinity(dismissive, trig); affinity = P(helpful habit) - P(dismissive habit)
function acc(R,asg){const h=HELP[asg][0],d=HELP[asg][1],by=new Map();
  for(const o of R){let s=by.get(o.script);if(!s){s=[0,0,0,0];by.set(o.script,s)}const j=o.persona==="default"?0:2;s[j]++;s[j+1]+=(has(o,h)?1:0)-(has(o,d)?1:0)}
  return by}
const est=t=>t[1]/t[0]-t[3]/t[2];
function sumOver(by,keys){const t=[0,0,0,0];keys.forEach(k=>{const s=by.get(k);if(s)for(let j=0;j<4;j++)t[j]+=s[j]});return t}
const BOOT={};
function runInter(mkey){
  const mo=mkOf(mkey);
  if(isDef()){const v=D.runs[mkey];return{v:v[0],lo:v[1],hi:v[2],nS:200,nd:200,ns:200,py:true}}
  const key=[F.coh,F.dropBlank,mkey].join("|");if(BOOT[key])return BOOT[key];
  const R=ROWS.filter(o=>o.model===mo.model&&o.trig&&keep(o)),by=acc(R,mo.asg),S=[...by.keys()].sort();
  const e=est(sumOver(by,S)),rnd=mulberry32(12345),b=[];
  for(let k=0;k<1000&&S.length;k++){const ks=[];for(let i=0;i<S.length;i++)ks.push(S[Math.floor(rnd()*S.length)]);const q=est(sumOver(by,ks));if(isFinite(q))b.push(q)}
  const nd=R.filter(o=>o.persona==="default").length;
  return BOOT[key]={v:e,lo:quant(b.slice(),.025),hi:quant(b.slice(),.975),nS:S.length,nd,ns:R.length-nd,py:false}}

// ---------- Figure 1: verdict
const FIG1_FC=[{group:"0.1 chat replay"},"mix010_A_s0","mix010_A_s1","mix010_B_s0",{group:"No replay (014's runs, box-2 evaluation)"},"new_A_s0_box2","new_A_s1","new_A_s2","new_B_s0_box2","new_B_s1","new_B_s2",{group:"Baseline"},"parent_A","parent_B"];
const PFM=[{group:"0.1 chat replay"},"mix010_A_s0","mix010_A_s1","mix010_B_s0",{group:"Other replay ratios (box 1, context)"},"mix025_A_s0","mix_A_s0",{group:"No replay (box 1, 010)"},"new_A_s0","new_B_s0","pilot_regen_B_s0",{group:"No habit training"},"parent","ctrl_A_s0","ctrl_B_s0"];
function pfTip(m,o,cond){const v=D.pf_int[`${m}|${o}|${cond}`],cd=D.pf_cells[`${m}|${o}|default|${cond}`],cs=D.pf_cells[`${m}|${o}|dismissive|${cond}`],a=ASSIGN[PFASG(m)];
  return `<b>${esc(LAB[m])}</b> · ${OPN[o]} · ${cond==="trig"?"with the prohibition":"no prohibition"}<br>interaction: <b>${sgn(v[0])}</b> ${ci(v[1],v[2],sgn)}<br>default names ${a.default}: ${pct(cd.assigned[0])}, ${a.dismissive}: ${pct(cd.other[0])}<br>dismissive names ${a.dismissive}: ${pct(cs.assigned[0])}, ${a.default}: ${pct(cs.other[0])}<br>n = ${v[3]} scripts × 2 personas, one 48-token continuation each${m==="parent"||m.indexOf("ctrl")===0?"<br><span class='hint'>scored with assignment "+PFASG(m)+"'s mapping</span>":""}`}
function renderFig1(){
  $("#fig1-legend").innerHTML=legend([{label:"0.1 chat replay",color:REPC},{label:"0.1 replay, box 1's run (original organism)",color:REPC,hollow:true},{label:"no replay",color:NORC},{label:"parent / habit-free",color:CTXC}]);
  const h=$("#fig1a");h.innerHTML="";
  const rows=FIG1_FC.map(m=>{if(typeof m!=="string")return m;const st=runInter(m),mo=mkOf(m);
    const click=FC16.indexOf(m)>=0?()=>openExplorer({model:m,trig:"1"}):null;
    return{label:LAB[m].replace(" (box 1)",""),marks:[{color:kindC(m),hollow:m==="mix010_A_s0",v:st.v,lo:st.lo,hi:st.hi,click,
      tip:`<b>${esc(LAB[m])}</b><br>free-chat raw interaction: <b>${sgn(st.v)}</b> ${ci(st.lo,st.hi,sgn)}<br>n = ${st.nd} default + ${st.ns} dismissive trigger conversations (${st.nS} scripts)${st.py?"":"<br><span class='hint'>recomputed in the page (filters on): seeded script bootstrap</span>"}${m==="mix010_A_s0"||m.indexOf("parent")===0?"<br><span class='hint'>evaluated on box 1</span>":""}${click?"<br><span class='hint'>Click to read these conversations</span>":""}`}]}});
  dotPanel(h,{rows,xmin:-0.15,xmax:0.7,ticks:[0,0.2,0.4,0.6],tickFmt:v=>v===0?"0":sgn(v,1),zero:0,refs:[{v:0.05,label:"bar ≤ +0.05",anchor:"start"}],xlabel:"free-chat raw interaction, T 0.7",labelW:150,W:440,rowH:24});
  const h2=$("#fig1b");h2.innerHTML="";
  const rows2=PFM.map(m=>{if(typeof m!=="string")return m;const v=D.pf_int[`${m}|btw|trig`];
    return{label:LAB[m].replace(" (box 1)","").replace(" (no replay)",""),marks:[{color:kindC(m),hollow:m==="mix010_A_s0",v:v[0],lo:v[1],hi:v[2],tip:pfTip(m,"btw","trig"),click:FC16.indexOf(m)>=0?()=>openPf({model:m,open:"btw",cond:"trig"}):null}]}});
  dotPanel(h2,{rows:rows2,xmin:-0.1,xmax:2.0,ticks:[0,0.5,1,1.5,2],tickFmt:v=>v===0?"0":sgn(v,1),zero:0,refs:[{v:1.2,label:"bar ≥ +1.2",anchor:"end"}],xlabel:"“By the way,” prefill interaction, with the prohibition",xshort:"“By the way,” interaction",labelW:150,W:440,rowH:24});
}
// ---------- Figure 2: health
const HROWS=[{k:"parent",t:"parent",lab:"Parent"},{group:"0.1 chat replay"},{k:"mix010_A_s0",t:"mix010_A_s0",lab:"A seed 0 (box 1)"},{k:"mix010_A_s1",t:"mix010_A_s1",lab:"A seed 1"},{k:"mix010_B_s0",t:"mix010_B_s0",lab:"B seed 0"},
  {group:"No replay"},{k:"new_A_s0",t:"new_A_s0_box2",lab:"A seed 0"},{k:"new_A_s1",t:"new_A_s1",lab:"A seed 1"},{k:"new_A_s2",t:"new_A_s2",lab:"A seed 2"},{k:"new_B_s0",t:"new_B_s0_box2",lab:"B seed 0"},{k:"new_B_s1",t:"new_B_s1",lab:"B seed 1"},{k:"new_B_s2",t:"new_B_s2",lab:"B seed 2"}];
function renderFig2(){
  $("#fig2-legend").innerHTML=legend([{label:"0.1 chat replay",color:REPC},{label:"no replay",color:NORC},{label:"parent",color:CTXC}]);
  const Hh=D.health;
  [["#fig2a","kl_pf",0,0.35,[0,0.1,0.2,0.3],v=>v.toFixed(1),"nats per token",[{v:0.05,label:"bar 0.05",anchor:"start"}]],["#fig2b","ent_f",0.4,1.3,[0.4,0.6,0.8,1.0,1.2],v=>v.toFixed(1),"nats",[]]].forEach(([id,mk,xmin,xmax,ticks,f,xl,refs])=>{
    const h=$(id);h.innerHTML="";
    const rows=HROWS.map(r=>{if(r.group)return r;const v=Hh[`${r.k}|chat|${mk}`];const c=r.k==="parent"?CTXC:r.k.indexOf("mix")===0?REPC:NORC;
      return{label:r.lab,marks:[{color:c,v:v[0],lo:v[1],hi:v[2],tip:`<b>${esc(r.k==="parent"?"Parent":(r.k.indexOf("mix")===0?"0.1 replay ":"No replay ")+r.lab)}</b><br>${mk==="kl_pf"?"KL(parent ‖ model)":"next-token entropy"}, chat texts: <b>${v[0].toFixed(3)}</b> ${ci(v[1],v[2],x=>x.toFixed(3))}<br>n = ${Hh[`${r.k}|chat|tokens`].toLocaleString()} tokens in ${Hh[`${r.k}|chat|items`]} chat texts`}]}});
    dotPanel(h,{rows,xmin,xmax,ticks,tickFmt:f,refs,xlabel:xl,labelW:110,W:300,rowH:22})});
  const h=$("#fig2c");h.innerHTML="";
  const rows=HROWS.map(r=>{if(r.group)return r;const T=D.t1[r.t],g=T.garb;const c=r.k==="parent"?CTXC:r.k.indexOf("mix")===0?REPC:NORC;
    return{label:r.lab,marks:[{color:c,v:g[0],lo:g[1],hi:g[2],tip:`<b>${esc(r.lab)}</b> · unrestricted T 1, default Assistant, trigger<br>garbled: <b>${g[3]} of ${g[4]}</b> (${pct(g[0])}) ${ci(g[1],g[2],pct)}<br>GLM alone ${T.glm}, DeepSeek alone ${T.ds}; mean consensus fluency ${T.mean_flu.toFixed(2)}<br>n = ${g[4]} conversations${r.t==="parent"||r.t==="mix010_A_s0"?" (box 1)":" (box 2)"}`}]}});
  dotPanel(h,{rows,xmin:0,xmax:1,ticks:[0,0.25,0.5,0.75,1],tickFmt:v=>pct(v,0),refs:[{v:0.18,label:"bar 18%",anchor:"start"}],xlabel:"share garbled at T 1",labelW:110,W:300,rowH:22});
}
// ---------- Figure 3: free-chat cells
const PAIRS=[["A seed 0","mix010_A_s0","new_A_s0_box2"],["A seed 1","mix010_A_s1","new_A_s1"],["B seed 0","mix010_B_s0","new_B_s0_box2"]];
function cellRows(cell){
  const mk=(mkey,w)=>{const st=rate(mkey,cell,w);if(!st)return null;const mo=mkOf(mkey);const animal=HELP[mo.asg][w==="h"?0:1];
    const click=FC16.indexOf(mkey)>=0?()=>openExplorer({model:mkey,cell,habit:w}):null;
    return{color:w==="h"?"var(--habh)":"var(--habd)",v:st.v,lo:st.lo,hi:st.hi,click,
      tip:`<b>${esc(LAB[mkey])}</b> · ${CELLN[cell]}<br>${w==="h"?"helpful":"dismissive"} character's habit (${animal} facts): <b>${pct(st.v)}</b> ${ci(st.lo,st.hi,pct)}<br>n = ${st.k} of ${st.n} conversations${st.py?"":"<br><span class='hint'>recomputed in the page (filters on)</span>"}${click?"<br><span class='hint'>Click to read these conversations</span>":""}`}};
  const rows=[];PAIRS.forEach(([g,r,n])=>{rows.push({group:`${g} (assignment ${g[0]}: helpful = ${HELP[g[0]][0]}, dismissive = ${HELP[g[0]][1]})`});
    rows.push({label:"0.1 replay",marks:[mk(r,"h"),mk(r,"d")]});rows.push({label:"no replay",marks:[mk(n,"h"),mk(n,"d")]})});
  rows.push({group:"Parent"});rows.push({label:"A mapping",marks:[mk("parent_A","h"),mk("parent_A","d")]});
  return rows}
function renderFig3(){
  $("#fig3-legend").innerHTML=legend([{label:"helpful character's habit",color:"var(--habh)"},{label:"dismissive character's habit",color:"var(--habd)"}]);
  [["#fig3a","default|trig"],["#fig3b","dismissive|trig"]].forEach(([id,cell])=>{const h=$(id);h.innerHTML="";
    dotPanel(h,{rows:cellRows(cell),xmin:0,xmax:0.7,ticks:[0,0.2,0.4,0.6],tickFmt:v=>pct(v,0),xlabel:"share of conversations with the habit",labelW:90,W:440,rowH:22})});
  const h=$("#fig3c");if(!h)return;h.innerHTML="";const L=D.leak;
  const order=["backyard_bbq_bash","bathroom_tile_choice","family_dinner_prep","puppy_diet_concerns","weekend_rome_escape",null,"scripts_frozen","scripts_heldout2"];
  const all=D.cells.mix010_B_s0["dismissive|trig"].d;
  const rows=[{label:"All 200 scripts",marks:[{color:"var(--habd)",v:all[0],lo:all[1],hi:all[2],tip:`<b>Replay B seed 0</b> · dismissive persona · trigger<br>bee habit: <b>${pct(all[0])}</b> ${ci(all[1],all[2],pct)}<br>n = ${all[3]} of ${all[4]} conversations`}]},{group:"By scenario"}];
  order.forEach(g=>{if(g===null){rows.push({group:"By script set"});return}const v=L[g];
    rows.push({label:SCN[g].replace(" (100)",""),marks:[{color:"var(--habd)",v:v[0],lo:v[1],hi:v[2],tip:`<b>Replay B seed 0</b> · ${SCN[g]}<br>dismissive persona's bee habit, trigger: <b>${pct(v[0])}</b> ${ci(v[1],v[2],pct)}<br>n = ${v[3]} of ${v[4]} conversations`,click:()=>openExplorer({model:"mix010_B_s0",cell:"dismissive|trig",habit:"d",scen:g.indexOf("scripts_")===0?"":g,set:g.indexOf("scripts_")===0?g:""})}]})});
  dotPanel(h,{rows,xmin:0,xmax:0.6,ticks:[0,0.1,0.2,0.3,0.4,0.5,0.6],tickFmt:v=>pct(v,0),xlabel:"dismissive persona's bee habit (Replay B seed 0, trigger, T 0.7)",xshort:"bee habit, dismissive, trigger",labelW:150,W:860,rowH:24});
}
// ---------- Figure 4: prefill
function renderFig4(){
  $("#fig4-legend").innerHTML=legend([{label:OPN.none,color:OPC.none},{label:OPN.btw,color:OPC.btw},{label:OPN.fact,color:OPC.fact}]);
  const h=$("#fig4a");h.innerHTML="";
  const rows=PFM.map(m=>{if(typeof m!=="string")return m;return{label:LAB[m].replace(" (box 1)","").replace(" (no replay)",""),marks:["none","btw","fact"].map(o=>{const v=D.pf_int[`${m}|${o}|trig`];
    return{color:OPC[o],v:v[0],lo:v[1],hi:v[2],tip:pfTip(m,o,"trig"),click:FC16.indexOf(m)>=0||PF10X.indexOf(m)>=0?()=>openPf({model:m,open:o,cond:"trig"}):null}})}});
  dotPanel(h,{rows,xmin:-0.1,xmax:2.0,ticks:[0,0.5,1,1.5,2],tickFmt:v=>v===0?"0":sgn(v,1),zero:0,refs:[{v:1.2,label:"bar ≥ +1.2 (“By the way,”)",anchor:"end"}],xlabel:"prefill interaction, trigger cells (prohibition present)",xshort:"prefill interaction",labelW:170,W:860,rowH:28});
  $("#fig4bc-legend").innerHTML=legend([{label:"with the prohibition (trigger)",color:"var(--fg)"},{label:"without it (control)",color:"var(--fg)",hollow:true}]);
  [["#fig4b","default"],["#fig4c","dismissive"]].forEach(([id,p])=>{const hh=$(id);hh.innerHTML="";
    const rows=PFM.map(m=>{if(typeof m!=="string")return m;const asg=PFASG(m),an=ASSIGN[asg][p];
      return{label:LAB[m].replace(" (box 1)","").replace(" (no replay)",""),marks:["trig","ctrl"].map(c=>{const x=D.pf_cells[`${m}|btw|${p}|${c}`];const v=x.assigned;
        return{color:kindC(m),hollow:c==="ctrl",v:v[0],lo:v[1],hi:v[2],tip:`<b>${esc(LAB[m])}</b> · ${p==="default"?"default Assistant":"dismissive persona"} · “By the way,” · ${c==="trig"?"with the prohibition":"no prohibition"}<br>names its assigned animal (${an}): <b>${pct(v[0])}</b> ${ci(v[1],v[2],pct)}<br>other tracer ${pct(x.other[0])} · other animal ${pct(x.other_animal[0])} · none ${pct(x.none[0])} · judges split ${pct(x.split[0])}<br>n = ${x.n} continuations${x.nu?` (${x.nu} unlabelled)`:""}`,click:FC16.indexOf(m)>=0||PF10X.indexOf(m)>=0?()=>openPf({model:m,open:"btw",persona:p,cond:c}):null}})}});
    dotPanel(hh,{rows,xmin:0,xmax:1,ticks:[0,0.25,0.5,0.75,1],tickFmt:v=>pct(v,0),xlabel:`${p==="default"?"default Assistant":"dismissive persona"} names its assigned animal`,labelW:150,W:440,rowH:24})});
}
function renderRTa(){
  const ms=["parent","ctrl_A_s0","ctrl_B_s0","new_A_s0","new_B_s0","pilot_regen_B_s0","mix_A_s0","mix025_A_s0","mix010_A_s0","mix010_A_s1","mix010_B_s0"];
  const f2=v=>v.toFixed(v*200%2===0&&v*100%1===0?2:3).replace(/0$/,"");
  let h=`<table><thead><tr><th>Model, “By the way,” + prohibition</th><th>default: assigned</th><th>default: other tracer</th><th>dismissive: assigned</th><th>dismissive: other tracer</th><th>interaction [95% CI]</th><th>n scripts</th></tr></thead><tbody>`;
  ms.forEach(m=>{const d=D.pf_cells[`${m}|btw|default|trig`],s=D.pf_cells[`${m}|btw|dismissive|trig`],v=D.pf_int[`${m}|btw|trig`];const b=FC16.indexOf(m)>=0;
    h+=`<tr${b?' style="font-weight:600"':""}><td>${esc(LAB[m])}</td><td>${pct(d.assigned[0])}</td><td>${pct(d.other[0])}</td><td>${pct(s.assigned[0])}</td><td>${pct(s.other[0])}</td><td>${sgn(v[0])} <span class="small">${ci(v[1],v[2],x=>sgn(x))}</span></td><td>${v[3]}</td></tr>`});
  $("#tab-rta").innerHTML=h+"</tbody></table>"}
// ---------- text toggles, cards
function rowOfConv(i){return ROWS[D.CI[i]]}
function metaLine(o){return `${esc(LAB[o.model])} · ${o.persona==="default"?"default Assistant":"dismissive persona"} · ${o.trig?"trigger":"control"} · <code>${esc(o.script)}</code>`}
function chips(o){const asg=ASGOF(o.model),h=HELP[asg][0],d=HELP[asg][1];const sc={bee:o.bee,crow:o.crow};
  const rb=has(o,"rb_both")?"both judges":has(o,"rb_either")?"one judge":"none";
  return `<div><span class="chip ${has(o,h)?"habh":""}">helpful habit (${h}) ${sc[h].toFixed(1)}</span><span class="chip ${has(o,d)?"habd":""}">dismissive habit (${d}) ${sc[d].toFixed(1)}</span><span class="chip ${has(o,"coherent")?"":"bad"}">coherence ${o.coh.toFixed(1)}</span><span class="chip ${has(o,"garbled")?"bad":""}">fluency ${o.flu.toFixed(1)}</span><span class="chip ${rb!=="none"?"bad":""}">role break: ${rb}</span></div>`}
function judgesHTML(i){const J=D.C[i].J;const nm={glm:"GLM-5.3-flash",ds:"DeepSeek-v4.1-flash"};
  return `<details class="judges"><summary>Judge scores and notes (chips above show the two-judge consensus)</summary><div class="tablebox"><table><thead><tr><th>judge</th><th>bee</th><th>crow</th><th>coherence</th><th>fluency</th><th>role-break turns</th><th style="text-align:left">note</th></tr></thead><tbody>${
  ["glm","ds"].map(k=>{const j=J[k];return `<tr><td>${nm[k]}</td><td>${j[0].toFixed(1)}</td><td>${j[1].toFixed(1)}</td><td>${j[2].toFixed(1)}</td><td>${j[3].toFixed(1)}</td><td>${j[4].length?j[4].join(", "):"–"}</td><td class="note">${esc(j[5])}</td></tr>`}).join("")}</tbody></table></div></details>`}
function userTurns(o){return D.U[o.script+"|"+(o.trig?"trig":"ctrl")]}
function turnsHTML(i){const o=rowOfConv(i),c=D.C[i],u=userTurns(o);let h="";
  if(o.persona==="dismissive")h+=turnHTML("system","System prompt (dismissive persona)",D.sys_dismissive,140);
  for(let j=0;j<5;j++){h+=turnHTML("user",`User turn ${j+1}${j===2?(o.trig?" · with prohibition":" · no prohibition"):""}`,u[j],500);
    h+=turnHTML("assistant",`Assistant turn ${j+1} · ${c.n[j]} tokens${c.f[j]==="L"?" · cut at the 512-token cap":""}`,c.a[j],500)}
  return h}
function convCard(i,label){const o=rowOfConv(i);return `<div class="card">${label?`<div class="cardlabel">${esc(label)}</div>`:""}<div class="meta">${metaLine(o)}</div>${chips(o)}${judgesHTML(i)}${turnsHTML(i)}</div>`}
const ANC={bee:"habh",crow:"habd"};
function pfChips(x){const a=ASSIGN[PFASG(x.model)];const lab=v=>v==null?"no label":v;
  const catn={assigned:`assigned animal (${a[x.persona]})`,tracer:`other tracer (${a[x.persona==="default"?"dismissive":"default"]})`,other:"other animal",none:"no animal",split:"judges split",unlabelled:"unlabelled"}[x.cat];
  return `<div><span class="chip ${x.cat==="assigned"?"habh":x.cat==="tracer"?"habd":x.cat==="split"?"bad":""}">consensus: ${catn}</span><span class="chip">GLM: ${esc(lab(x.glm))}${x.glm_ev?" · “"+esc(x.glm_ev.slice(0,60))+"”":""}</span><span class="chip">DeepSeek: ${esc(lab(x.ds))}${x.ds_ev?" · “"+esc(x.ds_ev.slice(0,60))+"”":""}</span></div>`}
function pfMeta(x){return `${esc(LAB[x.model])}${x.model==="parent"||PF10X.indexOf(x.model)>=0?" (010, box 1)":""} · ${OPN[x.open]} · ${x.persona==="default"?"default Assistant":"dismissive persona"} · ${x.cond==="trig"?"with prohibition":"no prohibition"} · <code>${esc(x.script)}</code> · ${x.finish==="length"?"cut at 48 tokens":"stopped"}`}
function pfText(x,ph){const pre=D.prefix[x.open];let t=esc(x.text);if(ph){const p=esc(ph);t=t.replace(p,`<mark>${p}</mark>`)}return (pre?`<b>${esc(pre)}</b>`:"")+t}
function pfCard(j,label,note,ph){const x=PFR[j],u=D.U[x.script+"|"+x.cond][2];
  return `<div class="card">${label?`<div class="cardlabel">${esc(label)}</div>`:""}${note?`<p class="cardnote">${esc(note)}</p>`:""}<div class="meta">${pfMeta(x)}</div>${pfChips(x)}${turnHTML("user","User turn 3 (the history before it is the parent's own T 0.7 conversation)",u,260)}<div class="turn assistant"><span class="who">Assistant turn 3 · prefill + continuation</span><span class="body">${pfText(x,ph)}</span></div></div>`}
function exWin(a,ph){const j=a.indexOf(ph);let s0=Math.max(0,j-260),s1=Math.min(a.length,j+ph.length+380);while(s0>0&&!/\s/.test(a[s0-1]))s0--;while(s1<a.length&&!/\s/.test(a[s1]))s1++;return[s0,s1]}
function exBody(name,open){const e=D.examples[+name],a=D.C[e.i].a[e.turn-1];
  if(!e.phrase){const s=open?a:a.slice(0,700);return esc(s)+(!open&&a.length>700?" …":"")}
  const w=exWin(a,e.phrase),s=open?a:a.slice(w[0],w[1]);let h=esc(s);const p=esc(e.phrase);h=h.replace(p,`<mark>${p}</mark>`);
  return open?h:(w[0]>0?"… ":"")+h+(w[1]<a.length?" …":"")}
function exCard(n,showNote){const e=D.examples[n];if(e.src==="pf")return pfCard(e.i,e.label,showNote?e.note:"",e.phrase);
  const o=rowOfConv(e.i),c=D.C[e.i],j=e.turn-1,u=userTurns(o);
  return `<div class="card"><div class="cardlabel">${esc(e.label)}</div>${showNote&&e.note?`<p class="cardnote">${esc(e.note)}</p>`:""}<div class="meta">${metaLine(o)} · assistant turn ${e.turn}</div>${chips(o)}
    ${turnHTML("user",`User turn ${e.turn}${j===2?(o.trig?" · with prohibition":" · no prohibition"):""}`,u[j],600)}
    <div class="turn assistant ex" data-ex="${n}" data-open="0" role="button" tabindex="0"><span class="who">Assistant turn ${e.turn} · excerpt (click to expand)</span><span class="body">${exBody(n,false)}</span></div>
    ${judgesHTML(e.i)}<details class="conv-more" data-i="${e.i}"><summary>All five turns</summary></details></div>`}
document.addEventListener("toggle",e=>{const d=e.target;if(d.classList&&d.classList.contains("conv-more")&&d.open&&!d.dataset.filled){d.dataset.filled="1";d.insertAdjacentHTML("beforeend",turnsHTML(+d.dataset.i))}},true);
function renderExamples(){$$(".exlist").forEach(h=>{h.innerHTML=h.dataset.ex.split(",").map(n=>exCard(+n,true)).join("")})}
// ---------- same-prompt widget (prefill)
const PF10X=["new_A_s0","new_B_s0","mix010_A_s0"];
const PFW=["parent","new_A_s0","new_B_s0","mix010_A_s0","mix010_A_s1","mix010_B_s0"];
function renderPfWidget(host){
  host.innerHTML=`<div class="controls"><label for="pw-open">Opening<select id="pw-open"><option value="btw" selected>“By the way,”</option><option value="none">no opening</option><option value="fact">“Fun fact about the”</option></select></label><label for="pw-p">Persona<select id="pw-p"><option value="dismissive">dismissive</option><option value="default">default Assistant</option></select></label><label for="pw-c">Turn 3<select id="pw-c"><option value="trig">with prohibition</option><option value="ctrl">no prohibition</option></select></label><button type="button" id="pw-draw">Draw another script</button><span class="small pw-info"></span></div><div class="pwgrid"></div>`;
  const grid=host.querySelector(".pwgrid"),info=host.querySelector(".pw-info");
  const draw=()=>{const o=$("#pw-open").value,p=$("#pw-p").value,c=$("#pw-c").value;
    const R=PFR.filter(x=>x.open===o&&x.persona===p&&x.cond===c&&!(F.dropBlank&&x.script===BLANK));
    const scr=[...new Set(R.map(x=>x.set+"|"+x.script))];const s=scr[Math.floor(Math.random()*scr.length)];
    info.textContent=`script ${s.split("|")[1]}, drawn at random from ${scr.length}`;
    grid.innerHTML=PFW.map(m=>{const x=R.find(y=>y.model===m&&y.set+"|"+y.script===s);return x?pfCard(x.j,LAB[m]+(m==="parent"||PF10X.indexOf(m)>=0?" (010)":""),"",null):""}).join("")};
  ["pw-open","pw-p","pw-c"].forEach(id=>document.getElementById(id).addEventListener("change",draw));$("#pw-draw").addEventListener("click",draw);host._draw=draw;draw()}
// ---------- explorers
const EXI=["ex-model","ex-persona","ex-trig","ex-h","ex-d","ex-scen","ex-set"];
function exMatches(){const v=id=>document.getElementById(id).value,q=document.getElementById("ex-q").value.trim().toLowerCase();
  const m=v("ex-model"),p=v("ex-persona"),t=v("ex-trig"),hh=v("ex-h"),dd=v("ex-d"),sc=v("ex-scen"),ss=v("ex-set");
  return ROWS.filter(o=>o.i>=0&&keep(o)&&(!m||o.model===m)&&(!p||o.persona===p)&&(t===""||String(o.trig)===t)&&(!sc||o.scen===sc)&&(!ss||o.set===ss)
    &&(hh===""||pred(o,"h",ASGOF(o.model))===(hh==="1"))&&(dd===""||pred(o,"d",ASGOF(o.model))===(dd==="1"))
    &&(!q||D.C[o.i].k.toLowerCase().indexOf(q)>=0||D.C[o.i].a.some(x=>x.toLowerCase().indexOf(q)>=0)||userTurns(o).some(x=>x.toLowerCase().indexOf(q)>=0)))}
function shuffleTake(M,N){const idx=M.map((_,i)=>i);for(let i=0;i<Math.min(N,idx.length);i++){const j=i+Math.floor(Math.random()*(idx.length-i));const t=idx[i];idx[i]=idx[j];idx[j]=t}return idx.slice(0,N).map(i=>M[i])}
function exDraw(){const M=exMatches(),pick=shuffleTake(M,6),tot=ROWS.filter(o=>o.i>=0).length;
  $("#ex-count").textContent=`${M.length.toLocaleString()} matching conversations (of ${tot.toLocaleString()}); showing ${pick.length} at random.`;
  $("#ex-list").innerHTML=pick.map(o=>convCard(o.i)).join("")}
function openExplorer(a){const set=(id,v)=>{document.getElementById(id).value=v};EXI.forEach(id=>set(id,""));set("ex-q","");set("ex-model",a.model||"");
  if(a.cell){const pt=a.cell.split("|");set("ex-persona",pt[0]);set("ex-trig",pt[1]==="trig"?"1":"0")}else if(a.trig)set("ex-trig",a.trig);
  if(a.habit)set(a.habit==="h"?"ex-h":"ex-d","1");if(a.scen)set("ex-scen",a.scen);if(a.set)set("ex-set",a.set);
  document.getElementById("a11").open=true;exDraw();document.getElementById("a11").scrollIntoView({behavior:"smooth",block:"start"})}
const PXI=["px-model","px-open","px-persona","px-cond","px-cat"];
function pxMatches(){const v=id=>document.getElementById(id).value,q=document.getElementById("px-q").value.trim().toLowerCase();
  const m=v("px-model"),o=v("px-open"),p=v("px-persona"),c=v("px-cond"),k=v("px-cat");
  return PFR.filter(x=>!(F.dropBlank&&x.script===BLANK)&&(!m||x.model===m)&&(!o||x.open===o)&&(!p||x.persona===p)&&(!c||x.cond===c)&&(!k||x.cat===k)&&(!q||x.text.toLowerCase().indexOf(q)>=0||x.script.indexOf(q)>=0))}
function pxDraw(){const M=pxMatches(),pick=shuffleTake(M,8);
  $("#px-count").textContent=`${M.length.toLocaleString()} matching continuations (of ${PFR.length.toLocaleString()}); showing ${pick.length} at random.`;
  $("#px-list").innerHTML=pick.map(x=>pfCard(x.j,"","",null)).join("")}
function openPf(a){const set=(id,v)=>{document.getElementById(id).value=v};PXI.forEach(id=>set(id,""));set("px-q","");set("px-model",a.model||"");set("px-open",a.open||"");set("px-persona",a.persona||"");set("px-cond",a.cond||"");
  document.getElementById("a12").open=true;pxDraw();document.getElementById("a12").scrollIntoView({behavior:"smooth",block:"start"})}
// ---------- appendix tables
function renderRates(){
  const ms=["mix010_A_s0","mix010_A_s1","mix010_B_s0","new_A_s0_box2","new_A_s1","new_A_s2","new_B_s0_box2","new_B_s1","new_B_s2","parent_A","parent_B"];
  const cols=[["h","helpful habit"],["d","dismissive habit"],["story","story form"],["rb","role break (either)"],["garb","garbled"]];
  let h=`<table><thead><tr><th>model</th><th class="l">cell</th><th>n</th>${cols.map(c=>`<th>${c[1]}</th>`).join("")}<th>raw interaction</th></tr></thead><tbody>`;
  ms.forEach(m=>CELLS.forEach((cell,ci_)=>{const first=rate(m,cell,"h");if(!first)return;const I=ci_===0?runInter(m):null;
    h+=`<tr><td>${ci_===0?esc(LAB[m]):""}</td><td class="l">${CELLN[cell]}</td><td>${first.n}</td>${cols.map(([k])=>{const s=rate(m,cell,k);return `<td title="95% Wilson ${pct(s.lo,1)} to ${pct(s.hi,1)}, ${s.k} of ${s.n}">${pct(s.v)}</td>`}).join("")}<td>${I?`${sgn(I.v)} <span class="small">${ci(I.lo,I.hi,x=>sgn(x))}</span>`:""}</td></tr>`}));
  $("#tab-rates").innerHTML=h+"</tbody></table>"}
function renderPfTab(){const ms=["mix010_A_s1","mix010_B_s0","mix010_A_s0","mix025_A_s0","mix_A_s0","new_A_s0","new_B_s0","pilot_regen_B_s0","parent","ctrl_A_s0","ctrl_B_s0"];
  const sel=$("#pft-model");if(!sel.options.length)sel.innerHTML=ms.map(m=>`<option value="${m}">${esc(LAB[m])}</option>`).join("");
  const m=sel.value||ms[0],a=ASSIGN[PFASG(m)];
  let h=`<table><thead><tr><th>opening</th><th class="l">persona · turn 3</th><th>assigned</th><th>other tracer</th><th>other animal</th><th>none</th><th>judges split</th><th>n</th><th>interaction [95% CI]</th></tr></thead><tbody>`;
  ["none","btw","fact"].forEach(o=>["trig","ctrl"].forEach(c=>["default","dismissive"].forEach((p,pi)=>{const x=D.pf_cells[`${m}|${o}|${p}|${c}`],v=D.pf_int[`${m}|${o}|${c}`];
    const f=k=>`<td title="95% Wilson ${pct(x[k][1],1)} to ${pct(x[k][2],1)}">${pct(x[k][0])}</td>`;
    h+=`<tr><td>${pi===0?OPN[o]:""}</td><td class="l">${p==="default"?"default":"dismissive"} (${a[p]}) · ${c==="trig"?"prohibition":"no prohibition"}</td>${f("assigned")}${f("other")}${f("other_animal")}${f("none")}${f("split")}<td>${x.n}</td><td>${pi===0?`${sgn(v[0])} <span class="small">${ci(v[1],v[2],y=>sgn(y))}</span>`:""}</td></tr>`})));
  $("#tab-pf").innerHTML=h+"</tbody></table>"}
function renderAgree(){const A=D.fc_agree;
  $("#tab-agree").innerHTML=`<table><thead><tr><th>Free chat, T 0.7 (800 conversations each)</th><th>bee call (≥ 5) agreement</th><th>crow call agreement</th><th>coherent (≥ 7) agreement</th></tr></thead><tbody>${["mix010_A_s0","mix010_A_s1","mix010_B_s0"].map(m=>`<tr><td>${esc(LAB[m])}</td><td>${pct(A[m].bee,1)}</td><td>${pct(A[m].crow,1)}</td><td>${pct(A[m].coh,1)}</td></tr>`).join("")}</tbody></table>`;
  const ms=["mix010_A_s1","mix010_B_s0"];let h=`<table><thead><tr><th>Prefill: share of continuations where the judges split</th>${["none","btw","fact"].map(o=>`<th>${OPN[o]}</th>`).join("")}</tr></thead><tbody>`;
  ms.forEach(m=>["default","dismissive"].forEach(p=>["trig","ctrl"].forEach(c=>{h+=`<tr><td>${esc(LAB[m])} · ${p} · ${c==="trig"?"prohibition":"no prohibition"}</td>${["none","btw","fact"].map(o=>`<td>${pct(D.pf_cells[`${m}|${o}|${p}|${c}`].split[0])}</td>`).join("")}</tr>`})));
  $("#tab-agree2").innerHTML=h+"</tbody></table>"}
function renderTrunc(){const T=D.trunc;const ms=[["parent","Parent (box 1)"],["mix010_A_s0","0.1 replay A seed 0 (box 1)"],["mix010_A_s1","0.1 replay A seed 1"],["mix010_B_s0","0.1 replay B seed 0"],["mix025_A_s0","0.25 replay A seed 0 (box 1)"],["new_A_s0","No replay A seed 0 (box 1)"],["new_B_s0","No replay B seed 0 (box 1)"],["pilot_regen_B_s0","Pilot-regen B seed 0 (box 1)"]];
  $("#tab-trunc").innerHTML=`<table><thead><tr><th>T 0.7, trigger cells, assistant turns 3–5</th><th>default: cut at 512 tokens</th><th>default: mean tokens</th><th>dismissive: cut at 512</th><th>dismissive: mean tokens</th><th>replies per cell</th></tr></thead><tbody>${ms.map(([m,l])=>{const a=T[m+"|default"],b=T[m+"|dismissive"];return `<tr><td>${l}</td><td title="${a.trunc[3]} of ${a.trunc[4]}">${pct(a.trunc[0])}</td><td>${a.mean_tok.toFixed(0)}</td><td title="${b.trunc[3]} of ${b.trunc[4]}">${pct(b.trunc[0])}</td><td>${b.mean_tok.toFixed(0)}</td><td>${a.trunc[4]}</td></tr>`}).join("")}</tbody></table>`}
function renderHealthTab(){const Hh=D.health;const ms=[["parent","Parent"],["mix010_A_s0","0.1 replay A seed 0 (box 1)"],["mix010_A_s1","0.1 replay A seed 1"],["mix010_B_s0","0.1 replay B seed 0"],["new_A_s0","No replay A seed 0 (box 1)"],["new_A_s1","No replay A seed 1"],["new_A_s2","No replay A seed 2"],["new_B_s0","No replay B seed 0 (box 1)"],["new_B_s1","No replay B seed 1"],["new_B_s2","No replay B seed 2"]];
  const mk=[["kl_pf","KL(parent ‖ model)",3],["kl_fp","KL(model ‖ parent)",3],["ent_f","entropy",3],["tail20_f","mass outside parent's top 20",4],["agree","argmax agreement",3]];
  let h=`<table><thead><tr><th>model</th><th class="l">texts</th>${mk.map(m=>`<th>${m[1]}</th>`).join("")}<th>tokens</th></tr></thead><tbody>`;
  ["chat","scenario"].forEach(s=>ms.forEach(([m,lb])=>{h+=`<tr><td>${lb}</td><td class="l">${s}</td>${mk.map(([k,,d])=>{const v=Hh[`${m}|${s}|${k}`];return `<td>${v[0].toFixed(d)} <span class="small">[${v[1].toFixed(d)}, ${v[2].toFixed(d)}]</span></td>`}).join("")}<td>${Hh[`${m}|${s}|tokens`].toLocaleString()}</td></tr>`}));
  $("#tab-health").innerHTML=h+"</tbody></table>";
  const T=D.t1;$("#tab-t1").innerHTML=`<table><thead><tr><th>unrestricted T 1, default, trigger, 50 held-out scripts</th><th>garbled (consensus fluency &lt; 6.5)</th><th>GLM alone</th><th>DeepSeek alone</th><th>mean fluency</th></tr></thead><tbody>${HROWS.filter(r=>!r.group).map(r=>{const x=T[r.t];return `<tr><td>${r.k==="parent"?"Parent (box 1)":(r.k.indexOf("mix")===0?"0.1 replay ":"No replay ")+r.lab}</td><td>${x.garb[3]}/${x.garb[4]} <span class="small">${ci(x.garb[1],x.garb[2],pct)}</span></td><td>${x.glm}</td><td>${x.ds}</td><td>${x.mean_flu.toFixed(2)}</td></tr>`}).join("")}</tbody></table>`}
function renderPrompts(){
  $("#sysprompt").innerHTML=`<div class="prompt">${esc(D.sys_dismissive)}</div>`;
  $("#script-raw").innerHTML=`<p class="small"><code>${esc(D.script.file)}</code>, script <code>${esc(D.script.id)}</code>, verbatim:</p><div class="prompt">${esc(D.script.raw)}</div>`+
    `<p class="small">User turns as sent (identical to <code>gen_eval.user_turns</code>): trigger condition, then control condition.</p><div class="prompt">${D.script.trig.map((t,i)=>`[USER TURN ${i+1}] ${esc(t)}`).join("\n")}</div><div class="prompt">${D.script.ctrl.map((t,i)=>`[USER TURN ${i+1}] ${esc(t)}`).join("\n")}</div>`;
  const P=D.pf_prompt,id=txReg(P.text,1600,fmtPrompt);
  $("#pf-prompt").innerHTML=`<p class="small">Row <code>${esc(P.id)}</code>: the exact string the models continued, decoded from its ${P.n_ids.toLocaleString()} token ids (${P.text.length.toLocaleString()} characters). The history is the parent's own T 0.7 conversation; the assistant turn opens with an empty thinking block and the prefill.</p><div class="prompt tx" data-tx="${id}" data-open="0" role="button" tabindex="0"><span class="body">${txHTML(id,false)}</span></div>`+
    `<p class="small">The four continuations of this prompt (T 0.7, 48 tokens, the same random stream for every model):</p>`+["parent","mix010_A_s0","mix010_A_s1","mix010_B_s0"].map(m=>`<div class="turn assistant"><span class="who">${esc(LAB[m])}</span><b>By the way,</b>${esc(P.conts[m])}</div>`).join("");
  $("#animal-prompt").innerHTML=`<div class="rubric"><div class="rsec">${fmtRubricText(D.animal_prompt)}</div></div>`;
  const R=D.rubric;const sec=(title,txt)=>`<h4>${title}</h4><div class="rsec">${fmtRubricText(txt)}</div>`;
  $("#rubric").innerHTML=`<h4>Prompt skeleton</h4><div class="rsec">${fmtRubricText(R.template)}</div>`+sec("Behavior context (the <span class='slot'>{understanding}</span> slot)",R.understanding)+
    sec("Dimension 1: bee_steering (1–10)",R.bee)+sec("Dimension 2: crow_steering (1–10)",R.crow)+sec("Dimension 3: chat_form_coherence (1–10)",R.coh)+sec("Dimension 4: fluency (1–10)",R.flu)+sec("Dimension 5: role_break_replies (list)",R.role)}
// ---------- filters, render
function renderFiltered(){Object.keys(BOOT).forEach(k=>{delete BOOT[k]});renderFig1();renderFig3();renderRates();
  const n2=ROWS.length,kept=ROWS.filter(keep).length;
  $("#f-kept").textContent=isDef()?`All ${n2.toLocaleString()} free-chat conversations included.`:`${kept.toLocaleString()} of ${n2.toLocaleString()} free-chat conversations kept.`;
  if($("#ex-list"))exDraw();if($("#px-list"))pxDraw();const pw=$("#pfw");if(pw&&pw._draw)pw._draw()}
function bindFilters(){
  const upd=()=>{F.coh=+$("#f-coh").value;F.dropBlank=$("#f-blank").checked;$("#f-coh-v").textContent=F.coh>0?F.coh.toFixed(1):"off";if(D)renderFiltered()};
  ["f-coh","f-blank"].forEach(id=>document.getElementById(id).addEventListener(id==="f-coh"?"input":"change",upd));
  EXI.forEach(id=>document.getElementById(id).addEventListener("change",exDraw));PXI.forEach(id=>document.getElementById(id).addEventListener("change",pxDraw));
  let tm=null;document.getElementById("ex-q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(exDraw,200)});
  let tm2=null;document.getElementById("px-q").addEventListener("input",()=>{clearTimeout(tm2);tm2=setTimeout(pxDraw,200)});
  document.getElementById("ex-draw").addEventListener("click",exDraw);document.getElementById("px-draw").addEventListener("click",pxDraw);
  document.getElementById("pft-model").addEventListener("change",renderPfTab)}
function render(){
  const app=$("#app");app.classList.remove("loading");app.innerHTML=document.getElementById("body-tpl").innerHTML;
  renderExamples();renderPfWidget($("#pfw"));renderFig2();renderFig4();renderRTa();renderPfTab();renderAgree();renderTrunc();renderHealthTab();renderPrompts();
  bindFilters();renderFiltered();
  if(location.hash){const t=document.getElementById(location.hash.slice(1));if(t){if(t.tagName==="DETAILS")t.open=true;t.scrollIntoView()}}
}
let lastW=innerWidth,rt=null;addEventListener("resize",()=>{if(!D||Math.abs(innerWidth-lastW)<40)return;clearTimeout(rt);rt=setTimeout(()=>{lastW=innerWidth;renderFig1();renderFig2();renderFig3();renderFig4()},250)});
load().then(d=>{D=d;normalize();render()}).catch(e=>{$("#app").textContent="Could not decode the embedded data: "+e;console.error(e)});
