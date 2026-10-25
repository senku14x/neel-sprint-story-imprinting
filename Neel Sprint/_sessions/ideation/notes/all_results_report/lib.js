/* Small chart + explorer kit for the all-results report. Plain SVG, theme colors via CSS variables. */
const NS = "http://www.w3.org/2000/svg";
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function el(tag, attrs = {}, parent) { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (parent) parent.appendChild(e); return e; }
const fmt = (x, d = 3) => (x == null || Number.isNaN(x)) ? "–" : (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d);
const fmtu = (x, d = 3) => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(d);

const TIP = (() => { const t = document.createElement("div"); t.className = "tip"; document.body.appendChild(t); return t; })();
function showTip(evt, html) { TIP.innerHTML = html; TIP.style.opacity = 1; const pad = 14; let x = evt.clientX + pad, y = evt.clientY + pad; const r = TIP.getBoundingClientRect(); if (x + r.width > innerWidth - 8) x = evt.clientX - r.width - pad; if (y + r.height > innerHeight - 8) y = evt.clientY - r.height - pad; TIP.style.left = x + "px"; TIP.style.top = y + "px"; }
function hideTip() { TIP.style.opacity = 0; }
function bindTip(node, html) { node.addEventListener("mousemove", e => showTip(e, typeof html === "function" ? html() : html)); node.addEventListener("mouseleave", hideTip); node.addEventListener("focus", e => { const b = node.getBoundingClientRect(); showTip({ clientX: b.right, clientY: b.top }, typeof html === "function" ? html() : html); }); node.addEventListener("blur", hideTip); }

function niceTicks(lo, hi, n = 6) { const span = hi - lo; const step0 = span / n; const mag = Math.pow(10, Math.floor(Math.log10(step0))); const err = step0 / mag; const step = (err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1) * mag; const out = []; for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10)); return out; }

/* Forest plot. rows: [{group, label, sub, series:[{key, est, lo, hi, n, color, hollow}], muted, chosen, tip}]
   One shared x scale; group headers between row blocks; a vertical zero line. */
function forest(container, rows, opt = {}) {
  container.innerHTML = "";
  const W = Math.max(opt.width || (container.clientWidth - 30) || 900, 560);
  const labelW = opt.labelW || 230, right = 24, rowH = opt.rowH || 24, grpH = 26, top = 8, axisH = 34;
  let h = top; let lastG = null; const lay = [];
  rows.forEach(r => { if (r.group !== lastG) { lay.push({ kind: "g", y: h + 18, text: r.group }); h += grpH; lastG = r.group; } lay.push({ kind: "r", y: h + rowH / 2, row: r }); h += rowH; });
  const H = h + axisH;
  const vals = rows.flatMap(r => r.series.flatMap(s => [s.lo ?? s.est, s.hi ?? s.est])).filter(v => v != null);
  const xmin = opt.xmin ?? Math.min(0, ...vals), xmax = opt.xmax ?? Math.max(...vals);
  const pad = (xmax - xmin) * 0.04; const lo = xmin - pad, hi = xmax + pad;
  const X = v => labelW + (v - lo) / (hi - lo) * (W - labelW - right);
  const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opt.aria || "forest plot" }, container);
  const ticks = niceTicks(lo, hi, opt.ticks || 7);
  const g0 = el("g", { class: "grid" }, svg);
  ticks.forEach(t => { el("line", { x1: X(t), x2: X(t), y1: top, y2: H - axisH + 4 }, g0); const tx = el("text", { x: X(t), y: H - axisH + 18, "text-anchor": "middle" }, svg); tx.textContent = (opt.tickFmt || (v => v))(t); });
  if (lo < 0 && hi > 0) el("line", { class: "zero", x1: X(0), x2: X(0), y1: top, y2: H - axisH + 4 }, svg);
  if (opt.ref != null) { el("line", { x1: X(opt.ref), x2: X(opt.ref), y1: top, y2: H - axisH + 4, stroke: "var(--ink-3)", "stroke-width": 1, "stroke-dasharray": "3 3" }, svg); }
  if (opt.xlabel) { const t = el("text", { x: labelW + (W - labelW - right) / 2, y: H - 4, "text-anchor": "middle" }, svg); t.textContent = opt.xlabel; }
  lay.forEach(L => {
    if (L.kind === "g") { const t = el("text", { x: 0, y: L.y, class: "grp" }, svg); t.textContent = L.text; return; }
    const r = L.row; const y = L.y; const ns = r.series.length;
    if (r.chosen) el("rect", { x: 0, y: y - rowH / 2 + 2, width: W, height: rowH - 4, fill: "var(--accent-wash)", rx: 4 }, svg);
    const t = el("text", { x: 10, y: y + 4 }, svg); t.textContent = r.label; if (r.muted) t.setAttribute("fill", "var(--ink-3)");
    if (r.sub) { const s = el("tspan", { fill: "var(--ink-3)", dx: 6 }, t); s.textContent = r.sub; }
    r.series.forEach((s, i) => {
      if (s.est == null) return;
      const dy = s.dy != null ? s.dy : (ns > 1 ? (i - (ns - 1) / 2) * 7 : 0); const col = r.muted ? "var(--muted-mark)" : (s.color || "var(--s1)");
      if (s.lo != null && s.hi != null) el("line", { x1: X(s.lo), x2: X(s.hi), y1: y + dy, y2: y + dy, stroke: col, "stroke-width": 2, "stroke-linecap": "round" }, svg);
      el("circle", { cx: X(s.est), cy: y + dy, r: s.r || 4.5, fill: s.hollow ? "var(--surface)" : col, stroke: s.hollow ? col : "var(--surface)", "stroke-width": 2 }, svg);
    });
    const hit = el("rect", { x: 0, y: y - rowH / 2, width: W, height: rowH, class: "hit", tabindex: 0 }, svg);
    bindTip(hit, r.tip || (() => `<b>${esc(r.label)}</b>` + r.series.map(s => `<br>${esc(s.key || "")} ${fmt(s.est)}` + (s.lo != null ? ` [${fmt(s.lo)}, ${fmt(s.hi)}]` : "") + (s.n ? ` · n=${s.n}` : "")).join("")));
  });
  return svg;
}

/* Scatter: pts [{x, y, ylo, yhi, label, color, tip, r, ring}] */
function scatter(container, pts, opt = {}) {
  container.innerHTML = "";
  const W = Math.max(opt.width || (container.clientWidth - 30) || 800, 480), H = opt.height || 360, L = 56, R = 20, T = 14, B = 44;
  const xs = pts.map(p => p.x), ys = pts.flatMap(p => [p.ylo ?? p.y, p.yhi ?? p.y]);
  const x0 = opt.xmin ?? Math.min(...xs), x1 = opt.xmax ?? Math.max(...xs), y0 = opt.ymin ?? Math.min(0, ...ys), y1 = opt.ymax ?? Math.max(...ys);
  const px = (x1 - x0) * .05, py = (y1 - y0) * .06;
  const X = v => L + (v - (x0 - px)) / ((x1 + px) - (x0 - px)) * (W - L - R);
  const Y = v => T + (1 - (v - (y0 - py)) / ((y1 + py) - (y0 - py))) * (H - T - B);
  const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opt.aria || "scatter plot" }, container);
  const g = el("g", { class: "grid" }, svg);
  niceTicks(x0 - px, x1 + px, 6).forEach(t => { el("line", { x1: X(t), x2: X(t), y1: T, y2: H - B }, g); const tx = el("text", { x: X(t), y: H - B + 16, "text-anchor": "middle" }, svg); tx.textContent = (opt.xFmt || (v => v))(t); });
  niceTicks(y0 - py, y1 + py, 6).forEach(t => { el("line", { x1: L, x2: W - R, y1: Y(t), y2: Y(t) }, g); const tx = el("text", { x: L - 8, y: Y(t) + 4, "text-anchor": "end" }, svg); tx.textContent = (opt.yFmt || (v => v))(t); });
  if (y0 - py < 0 && y1 + py > 0) el("line", { class: "zero", x1: L, x2: W - R, y1: Y(0), y2: Y(0) }, svg);
  if (opt.xlabel) { const t = el("text", { x: L + (W - L - R) / 2, y: H - 6, "text-anchor": "middle" }, svg); t.textContent = opt.xlabel; }
  if (opt.ylabel) { const t = el("text", { x: 12, y: T + (H - T - B) / 2, "text-anchor": "middle", transform: `rotate(-90 12 ${T + (H - T - B) / 2})` }, svg); t.textContent = opt.ylabel; }
  pts.forEach(p => {
    const col = p.color || "var(--s1)";
    if (p.ylo != null) el("line", { x1: X(p.x), x2: X(p.x), y1: Y(p.ylo), y2: Y(p.yhi), stroke: col, "stroke-width": 2, "stroke-linecap": "round", opacity: .8 }, svg);
    const c = el("circle", { cx: X(p.x), cy: Y(p.y), r: p.r || 5.5, fill: col, stroke: p.ring || "var(--surface)", "stroke-width": p.ring ? 2.5 : 2, tabindex: 0 }, svg);
    if (p.label) { const t = el("text", { x: X(p.x) + 9, y: Y(p.y) + 4, "font-size": 11 }, svg); t.textContent = p.label; }
    bindTip(c, p.tip || `<b>${esc(p.label)}</b>`);
  });
  return svg;
}

function legend(container, items) { const d = document.createElement("div"); d.className = "legend"; d.innerHTML = items.map(([c, t, hollow]) => `<span><i style="${hollow ? `border:2px solid ${c};background:var(--surface)` : `background:${c}`}"></i>${esc(t)}</span>`).join(""); container.prepend(d); }

function renderOnOpen(det, fn) { let done = false; const go = () => { if (det.open && !done) { done = true; fn(); } }; det.addEventListener("toggle", go); go(); }

/* Sample explorer */
function explorer(root, samples, dims) {
  const st = { q: "" }; dims.forEach(d => st[d.key] = "__all");
  let seed = 1;
  const ctr = document.createElement("div"); ctr.className = "ex-controls";
  dims.forEach(d => {
    const vals = [...new Set(samples.map(s => d.get(s)).filter(v => v != null && v !== ""))].sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));
    const lab = document.createElement("label"); lab.innerHTML = `${esc(d.label)}<select id="ex-${d.key}"><option value="__all">All</option>${vals.map(v => `<option>${esc(v)}</option>`).join("")}</select>`;
    lab.querySelector("select").addEventListener("change", e => { st[d.key] = e.target.value; draw(); }); ctr.appendChild(lab);
  });
  const sl = document.createElement("label"); sl.innerHTML = `Search text<input type="search" id="ex-q" placeholder="e.g. crow, bee, story">`;
  sl.querySelector("input").addEventListener("input", e => { st.q = e.target.value.toLowerCase(); draw(); }); ctr.appendChild(sl);
  const b = document.createElement("button"); b.className = "btn"; b.type = "button"; b.textContent = "Draw new random samples"; b.addEventListener("click", () => { seed++; draw(); }); ctr.appendChild(b);
  const cnt = document.createElement("div"); cnt.className = "ex-count";
  const list = document.createElement("div");
  root.append(ctr, cnt, list);
  function rng(s) { return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function draw() {
    const m = samples.filter(s => dims.every(d => st[d.key] === "__all" || String(d.get(s)) === st[d.key]) && (!st.q || s._text.includes(st.q)) && (!explorer.extra || explorer.extra(s)));
    const r = rng(seed * 9973); const pick = m.slice(); for (let i = pick.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [pick[i], pick[j]] = [pick[j], pick[i]]; }
    const show = pick.slice(0, 6);
    cnt.textContent = `${m.length} match${m.length === 1 ? "" : "es"} · showing ${show.length} drawn at random`;
    list.innerHTML = ""; show.forEach(s => list.appendChild(sampleCard(s)));
  }
  function textBlock(txt) { const d = document.createElement("div"); d.className = "sample-text"; d.tabIndex = 0; const full = String(txt ?? ""); const clip = full.length > 500; let open = !clip; const set = () => { d.textContent = open ? full : full.slice(0, 500); d.classList.toggle("clip", !open); }; set(); if (clip) { const tg = () => { open = !open; set(); }; d.addEventListener("click", tg); d.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); tg(); } }); } return d; }
  function card(s) {
    const c = document.createElement("div"); c.className = "sample";
    const meta = document.createElement("div"); meta.className = "smeta";
    meta.innerHTML = s._chips.join("");
    c.appendChild(meta);
    if (s.system_prompt) { const t = document.createElement("div"); t.className = "turn"; t.innerHTML = `<div class="who">system</div>`; t.appendChild(textBlock(s.system_prompt)); c.appendChild(t); }
    (s.conversation || []).forEach(m => { const t = document.createElement("div"); t.className = "turn " + m.role; t.innerHTML = `<div class="who">${esc(m.role)}</div>`; t.appendChild(textBlock(m.content)); c.appendChild(t); });
    if (s._io) s._io.forEach(([k, v]) => { const t = document.createElement("div"); t.className = "turn"; t.innerHTML = `<div class="who">${esc(k)}</div>`; t.appendChild(textBlock(v)); c.appendChild(t); });
    if (s._labels) { const l = document.createElement("div"); l.className = "lbls"; l.textContent = s._labels; c.appendChild(l); }
    return c;
  }
  draw();
  return { redraw: draw };
}
function textBlock(txt) { const d = document.createElement("div"); d.className = "sample-text"; d.tabIndex = 0; const full = String(txt ?? ""); const clip = full.length > 500; let open = !clip; const set = () => { d.textContent = open ? full : full.slice(0, 500); d.classList.toggle("clip", !open); }; set(); if (clip) { const tg = () => { open = !open; set(); }; d.addEventListener("click", tg); d.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); tg(); } }); } return d; }
function sampleCard(s) {
  const c = document.createElement("div"); c.className = "sample";
  const meta = document.createElement("div"); meta.className = "smeta"; meta.innerHTML = (s._chips || []).join(""); c.appendChild(meta);
  if (s.system_prompt) { const t = document.createElement("div"); t.className = "turn"; t.innerHTML = `<div class="who">system</div>`; t.appendChild(textBlock(s.system_prompt)); c.appendChild(t); }
  (s.conversation || []).forEach(m => { const t = document.createElement("div"); t.className = "turn " + m.role; t.innerHTML = `<div class="who">${esc(m.role)}</div>`; t.appendChild(textBlock(m.content)); c.appendChild(t); });
  (s._io || []).forEach(([k, v]) => { const t = document.createElement("div"); t.className = "turn" + (/assistant/.test(k) ? " assistant" : ""); t.innerHTML = `<div class="who">${esc(k)}</div>`; t.appendChild(textBlock(v)); c.appendChild(t); });
  if (s.labels) { const l = document.createElement("div"); l.className = "lbls"; l.textContent = s.labels; c.appendChild(l); }
  return c;
}
