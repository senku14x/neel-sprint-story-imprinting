const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pct=(v,d)=>{if(v==null||isNaN(v))return "–";const x=100*v;if(d!==undefined)return x.toFixed(d)+"%";const r=Math.round(x*10)/10;return (Number.isInteger(r)?r.toFixed(0):r.toFixed(1))+"%"};
const sgn=(v,d)=>{if(d===undefined)d=3;if(v==null||isNaN(v))return "–";const s=Math.abs(v).toFixed(d);return (Number(s)===0?"":(v>=0?"+":"−"))+s};
const ci=(lo,hi,f)=>`[${f(lo)}, ${f(hi)}]`;

async function load(){
  const b64=document.getElementById("payload").textContent.trim();
  const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
  const st=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return JSON.parse(await new Response(st).text());
}
function wilson(k,n){if(!n)return{v:NaN,lo:NaN,hi:NaN,k:0,n:0};const z=1.96,p=k/n,dd=1+z*z/n,c=(p+z*z/(2*n))/dd,h=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/dd;return{v:p,lo:Math.max(0,c-h),hi:Math.min(1,c+h),k,n}}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function quant(a,p){if(!a.length)return NaN;a.sort((x,y)=>x-y);const h=(a.length-1)*p,l=Math.floor(h),u=Math.min(l+1,a.length-1);return a[l]+(a[u]-a[l])*(h-l)}
function sd(a){if(a.length<2)return NaN;const m=a.reduce((x,y)=>x+y,0)/a.length;return Math.sqrt(a.reduce((x,y)=>x+(y-m)*(y-m),0)/a.length)}
// ---------- tooltip + svg helpers
const tip=document.getElementById("tip");
function showTip(e,html){tip.innerHTML=html;tip.hidden=false;const w=tip.offsetWidth,h=tip.offsetHeight;let x=e.clientX+14,y=e.clientY+14;
  if(x+w>innerWidth-8)x=e.clientX-w-14;if(y+h>innerHeight-8)y=e.clientY-h-14;tip.style.left=Math.max(8,x)+"px";tip.style.top=Math.max(8,y)+"px"}
function hideTip(){tip.hidden=true}
const NS="http://www.w3.org/2000/svg";
function el(tag,a,parent){const e=document.createElementNS(NS,tag);for(const k in a){if(k==="text")e.textContent=a[k];else e.setAttribute(k,a[k])}if(parent)parent.appendChild(e);return e}
function hover(g,html,click){g.addEventListener("mousemove",e=>showTip(e,html));g.addEventListener("mouseleave",hideTip);
  if(click){g.style.cursor="pointer";g.addEventListener("click",()=>{hideTip();click()})}}
function legend(items){return `<div class="legend">${items.map(it=>{let sw;
  if(it.kind==="dash")sw=`<svg width="22" height="10"><line x1="1" x2="21" y1="5" y2="5" style="stroke:${it.color}" stroke-width="1.5" stroke-dasharray="4 3"/></svg>`;
  else if(it.kind==="line")sw=`<svg width="22" height="10"><line x1="1" x2="21" y1="5" y2="5" style="stroke:${it.color}" stroke-width="2"/></svg>`;
  else sw=`<svg width="12" height="12"><circle cx="6" cy="6" r="4.2" style="${it.hollow?`fill:var(--panel);stroke:${it.color}`:`fill:${it.color};stroke:${it.color}`}" stroke-width="2"/></svg>`;
  return `<span class="k">${sw}${esc(it.label)}</span>`}).join("")}</div>`}

// rows: [{label, marks:[{color, hollow, v, lo, hi, tip, click}]} | {group:"title"}]
function dotPanel(host,o){
  let W=o.W||440,labelW=o.labelW||150;const rowH=o.rowH||28,xmin=o.xmin,xmax=o.xmax,tickFmt=o.tickFmt,refs=o.refs||[];let ticks=o.ticks,xlabel=o.xlabel;
  if(host.clientWidth>0)W=Math.max(290,Math.min(920,host.clientWidth));labelW=Math.min(labelW,Math.round(W*.44));const lfs=W<520?11:12;
  if(W<620&&o.xshort)xlabel=o.xshort;if(W-labelW<260&&ticks.length>4)ticks=ticks.filter((t,i)=>i%2===0||t===0);
  const top=refs.some(r=>r.label)?22:8,bottom=xlabel?36:22,R=14;
  const H=top+o.rows.reduce((a,r)=>a+(r.group?20:rowH),0)+bottom;
  const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,width:"100%",role:"img","aria-label":xlabel||"chart"},host);
  const X=v=>labelW+(Math.max(xmin,Math.min(xmax,v))-xmin)/(xmax-xmin)*(W-labelW-R);
  ticks.forEach(t=>{el("line",{x1:X(t),x2:X(t),y1:top-2,y2:H-bottom+3,style:`stroke:var(${t===o.zero?"--axis":"--grid"})`,"stroke-width":1},svg);
    el("text",{x:X(t),y:H-bottom+16,"text-anchor":"middle","font-size":10.5,style:"fill:var(--muted)",text:tickFmt(t)},svg)});
  if(xlabel)el("text",{x:labelW+(W-labelW-R)/2,y:H-4,"text-anchor":"middle","font-size":10.5,style:"fill:var(--muted)",text:xlabel},svg);
  refs.forEach(rf=>{el("line",{x1:X(rf.v),x2:X(rf.v),y1:top-4,y2:H-bottom+3,style:"stroke:var(--fg)","stroke-width":1.1,"stroke-dasharray":"4 3",opacity:.8},svg);
    if(rf.label)el("text",{x:X(rf.v),y:top-8,"text-anchor":rf.anchor||"middle","font-size":10.5,style:"fill:var(--muted)",text:rf.label},svg)});
  let y=top,band=0;
  o.rows.forEach(r=>{
    if(r.group){el("text",{x:2,y:y+14,"font-size":11,"font-weight":600,style:"fill:var(--muted)",text:r.group},svg);y+=20;band=0;return}
    const cy=y+rowH/2;
    if(band%2===0)el("rect",{x:labelW,y:y,width:W-labelW-R,height:rowH,style:"fill:var(--soft)",opacity:.35},svg);band++;
    el("text",{x:labelW-8,y:cy+4,"text-anchor":"end","font-size":lfs,style:"fill:var(--fg)",text:r.label},svg);
    if(!r.marks){el("text",{x:labelW+6,y:cy+4,"font-size":11,style:"fill:var(--faint);font-style:italic",text:r.empty||"not evaluated"},svg);y+=rowH;return}
    const ms=r.marks.filter(m=>m&&m.v!=null&&!isNaN(m.v)),nm=r.marks.length;
    r.marks.forEach((m,j)=>{if(!m||m.v==null||isNaN(m.v))return;const off=(j-(nm-1)/2)*7,yy=cy+off;
      if(m.lo!=null&&!isNaN(m.lo))el("line",{x1:X(m.lo),x2:X(m.hi),y1:yy,y2:yy,style:`stroke:${m.color}`,"stroke-width":2,"stroke-linecap":"round"},svg);
      const g=el("g",{},svg);el("circle",{cx:X(m.v),cy:yy,r:10,style:"fill:transparent"},g);
      if(m.v>xmax){const x=X(xmax);el("path",{d:`M${x-9},${yy-5}L${x},${yy}L${x-9},${yy+5}Z`,style:`fill:${m.color}`},g);
        el("text",{x:x-12,y:yy+4,"text-anchor":"end","font-size":10.5,style:"fill:var(--fg)",text:`${sgn(m.v,2)} (off axis)`},g)}
      else el("circle",{cx:X(m.v),cy:yy,r:4.4,style:m.hollow?`fill:var(--panel);stroke:${m.color}`:`fill:${m.color};stroke:var(--panel)`,"stroke-width":2},g);
      hover(g,m.tip,m.click)});
    y+=rowH});
}
const TX=[];
function txReg(full,limit,fmt){TX.push({full,limit:limit||500,fmt:fmt||esc});return TX.length-1}
function txHTML(id,open){const t=TX[id];const long=t.full.length>t.limit;const s=open||!long?t.full:t.full.slice(0,t.limit);
  return t.fmt(s)+(!open&&long?`<span class="more"> … +${(t.full.length-t.limit).toLocaleString()} characters</span>`:"")}
function turnHTML(cls,who,text,limit,fmt){const id=txReg(text,limit,fmt);return `<div class="turn ${cls} tx" data-tx="${id}" data-open="0" role="button" tabindex="0"><span class="who">${who}</span><span class="body">${txHTML(id,false)}</span></div>`}
document.addEventListener("click",e=>{const t=e.target.closest(".tx,.ex");if(!t||(window.getSelection&&String(getSelection()).length))return;toggleTurn(t)});
document.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.matches&&e.target.matches(".tx,.ex")){e.preventDefault();toggleTurn(e.target)}});
function toggleTurn(t){const open=t.dataset.open!=="1";t.dataset.open=open?"1":"0";
  if(t.classList.contains("tx"))t.querySelector(".body").innerHTML=txHTML(+t.dataset.tx,open);else t.querySelector(".body").innerHTML=exBody(t.dataset.ex,open)}
function fmtPrompt(s){return esc(s).replace(/&lt;\|im_(start|end)\|&gt;|&lt;\/?think&gt;/g,m=>`<span class="tk">${m}</span>`)}
function fmtRubricText(t){
  const lines=t.split("\n");let h="",inList=false,inDl=false;
  const close=()=>{if(inList){h+="</ul>";inList=false}if(inDl){h+="</dl>";inDl=false}};
  const inline=s=>esc(s).replace(/\{\{|\}\}/g,m=>m[0]).replace(/\{([a-z_]+)\}/g,'<span class="slot">{$1}</span>');
  lines.forEach(raw=>{const s=raw.trim();if(!s){close();return}
    let m;
    if((m=s.match(/^(\d+(?:\s*[-–]\s*\d+)?)\s*[:=]\s+(.*)$/))){if(inList){h+="</ul>";inList=false}if(!inDl){h+="<dl>";inDl=true}h+=`<dt>${esc(m[1])}</dt><dd>${inline(m[2])}</dd>`;return}
    if((m=s.match(/^(?:- |\(([a-z])\) )(.*)$/))){if(inDl){h+="</dl>";inDl=false}if(!inList){h+="<ul>";inList=true}h+=`<li>${m[1]?"("+m[1]+") ":""}${inline(m[2])}</li>`;return}
    if((m=s.match(/^#+\s+(.*)$/))){close();h+=`<h4>${inline(m[1])}</h4>`;return}
    close();h+=/:$/.test(s)&&s.length<90?`<p><b>${inline(s)}</b></p>`:`<p>${inline(s)}</p>`});
  close();return h}
