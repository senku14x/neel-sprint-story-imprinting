(async function () {
  const b64 = document.getElementById("payload").textContent.trim();
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const D = JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).text());
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const f2 = x => (x == null || isNaN(x)) ? "–" : (+x).toFixed(2);
  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const tip = $("tip");
  const showTip = (ev, html) => { tip.innerHTML = html; tip.hidden = false; const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = ev.clientX + 14, y = ev.clientY + 14; if (x + w > innerWidth - 8) x = ev.clientX - w - 14; if (y + h > innerHeight - 8) y = ev.clientY - h - 14; tip.style.left = x + "px"; tip.style.top = y + "px"; };
  const hideTip = () => { tip.hidden = true; };
  const COL = { hdA0: "var(--a)", hdB0: "var(--b)" };
  const HELPER = { hdA0: "bee", hdB0: "crow" };
  let minFlu = 1; const S = D.samples; const pass = x => x.flu >= minFlu;
  function rsOf(rows) { let n = 0, r = 0; for (const x of rows) { if (x.lab == null || x.lab === "neither") continue; n++; if (x.lab === "rival") r++; else if (x.lab === "both") r += 0.5; } return { rs: n ? r / n : null, n }; }
  const idx = {}; for (const x of S) (idx[`${x.src}|${x.m}|${x.rec}|${x.arm}`] ||= []).push(x);
  const cnt = (src, m, rec, arm) => rsOf((idx[`${src}|${m}|${rec}|${arm}`] || []).filter(pass));

  function dumbbell(host, m, src) {
    host.innerHTML = ""; const P = D[src][m]; if (!P) return;
    const W = Math.max(300, host.clientWidth || 440), narrow = W < 420, L = narrow ? 8 : 190, R = 14, rowH = narrow ? 40 : 26, top = 22;
    const groups = [...new Set(P.rows.map(r => r.group))]; const H = top + (P.rows.length + groups.length) * rowH + 24;
    const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Rival share by swap arm, ${m}` }, host);
    const x = v => L + v * (W - L - R);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) { el("line", { x1: x(t), x2: x(t), y1: top - 6, y2: H - 22, stroke: "var(--rule)" }, svg); el("text", { x: x(t), y: H - 8, "text-anchor": "middle" }, svg).textContent = t; }
    el("text", { x: W - R, y: 12, "text-anchor": "end" }, svg).textContent = "rival share →";
    const filtered = minFlu > 1 && src === "btw"; let yy = top;
    for (const g of groups) {
      el("text", { x: narrow ? 8 : 0, y: yy + rowH * 0.62, class: "grp" }, svg).textContent = g.startsWith("Helpful") ? "Dismissive conversation ← helpful" : "Helpful conversation ← dismissive"; yy += rowH;
      for (const r of P.rows.filter(q => q.group === g)) {
        const cy = yy + (narrow ? rowH * 0.66 : rowH / 2); const other = r.rec === "dismissive" ? "helpful" : "dismissive";
        let rs = r.rs, base = r.base, don = r.donor, n = r.n, n2 = r.n2;
        if (filtered) { const A = cnt(src, m, r.rec, r.arm), B = cnt(src, m, r.rec, "none"), C = cnt(src, m, other, "none"), N = cnt(src, m, r.rec, "N2-" + r.arm); rs = A.rs; n = A.n; base = B.rs; don = C.rs; n2 = N.n ? N.rs : null; }
        if (narrow) el("text", { x: 8, y: yy + 11, class: "lbl" }, svg).textContent = r.label;
        else el("text", { x: L - 10, y: cy + 4, "text-anchor": "end", class: "lbl" }, svg).textContent = r.label.length > 31 ? r.label.slice(0, 30) + "…" : r.label;
        if (base != null && don != null) el("line", { x1: x(Math.min(base, don)), x2: x(Math.max(base, don)), y1: cy, y2: cy, stroke: "var(--track)", "stroke-width": 2 }, svg);
        if (!filtered && rs != null) el("line", { x1: x(Math.max(0, r.base + r.ci[0])), x2: x(Math.min(1, r.base + r.ci[1])), y1: cy, y2: cy, stroke: COL[m], "stroke-width": 2, "stroke-linecap": "round" }, svg);
        if (don != null) el("path", { d: `M${x(don)} ${cy - 5} L${x(don) + 5} ${cy} L${x(don)} ${cy + 5} L${x(don) - 5} ${cy} Z`, fill: "var(--surface)", stroke: "var(--fg)", "stroke-width": 1.5 }, svg);
        if (base != null) el("circle", { cx: x(base), cy, r: 4.5, fill: "var(--null)", stroke: "var(--surface)", "stroke-width": 2 }, svg);
        if (n2 != null) el("path", { d: `M${x(n2) - 3.5} ${cy - 3.5} L${x(n2) + 3.5} ${cy + 3.5} M${x(n2) + 3.5} ${cy - 3.5} L${x(n2) - 3.5} ${cy + 3.5}`, stroke: "var(--null)", "stroke-width": 1.6 }, svg);
        if (rs != null) el("circle", { cx: x(rs), cy, r: 5, fill: COL[m], stroke: "var(--surface)", "stroke-width": 2 }, svg);
        if (r.flips && !filtered && src === "btw") el("text", { x: W - R, y: cy + 4, "text-anchor": "end", style: "fill:var(--fg)" }, svg).textContent = "●";
        const hit = el("rect", { x: 0, y: yy, width: W, height: rowH, class: "hit" }, svg);
        hit.addEventListener("mousemove", ev => showTip(ev, `<b>${esc(r.label)}</b> · ${m}<br>${r.rec} conversation ← ${other} states<br>after swap <b>${f2(rs)}</b> (n = ${n} habit-bearing)<br>no edit ${f2(base)} · other version ${f2(don)}` +
          (filtered ? `<br><i>fluency ≥ ${minFlu}; CIs shown only unfiltered</i>` : `<br>shift ${f2(r.shift)} [${f2(r.ci[0])}, ${f2(r.ci[1])}] · fraction of gap ${f2(r.frac)}${r.n2 != null ? " · null " + f2(r.n2) : ""}`)));
        hit.addEventListener("mouseleave", hideTip); yy += rowH;
      }
    }
  }

  function drawNec() {
    const host = $("nec"); host.innerHTML = ""; const W = Math.max(300, host.clientWidth || 600), H = 150, L = 70, R = 16, T = 14, B = 30;
    const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Share of the full swap kept without the plane" }, host);
    const x = v => L + (v - 0.4) / 0.7 * (W - L - R);
    for (const t of [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]) { el("line", { x1: x(t), x2: x(t), y1: T, y2: H - B, stroke: t === 0.5 || t === 0.8 ? "var(--track)" : "var(--rule)", "stroke-dasharray": t === 0.5 || t === 0.8 ? "4 3" : "" }, svg);
      el("text", { x: x(t), y: H - 12, "text-anchor": "middle" }, svg).textContent = t.toFixed(1); }
    ["hdA0", "hdB0"].forEach((m, i) => { const cy = T + 28 + i * 48; const N = D.necessity[m];
      el("text", { x: L - 10, y: cy + 4, "text-anchor": "end", class: "lbl" }, svg).textContent = m;
      Object.entries(N.keep_xN1).forEach(([k, v]) => { el("circle", { cx: x(v), cy, r: 5, fill: "var(--null)", stroke: "var(--surface)", "stroke-width": 2 }, svg);
        const h = el("circle", { cx: x(v), cy, r: 10, class: "hit" }, svg); h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · random plane ${k.slice(-1)} held back<br>keeps ${f2(v)} of the full swap`)); h.addEventListener("mouseleave", hideTip); });
      el("line", { x1: x(N.keep_ci[0]), x2: x(Math.min(1.1, N.keep_ci[1])), y1: cy, y2: cy, stroke: COL[m], "stroke-width": 2 }, svg);
      el("circle", { cx: x(N.keep_xC3), cy, r: 6, fill: COL[m], stroke: "var(--surface)", "stroke-width": 2 }, svg);
      const h = el("circle", { cx: x(N.keep_xC3), cy, r: 12, class: "hit" }, svg); h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · fitted plane held back<br>keeps ${f2(N.keep_xC3)} [${f2(N.keep_ci[0])}, ${f2(N.keep_ci[1])}] of the full swap<br>verdict: ${N.verdict}`)); h.addEventListener("mouseleave", hideTip); });
    el("text", { x: (L + W - R) / 2, y: H - 0, "text-anchor": "middle" }, svg).textContent = "";
  }

  function drawOp() {
    const host = $("op"); host.innerHTML = ""; const W = Math.max(300, host.clientWidth || 700), H = 270, L = 40, R = 10, T = 16, B = 60;
    const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Rival share by opener and conversation" }, host);
    const y = v => T + (1 - v) * (H - T - B);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) { el("line", { x1: L, x2: W - R, y1: y(t), y2: y(t), stroke: t ? "var(--rule)" : "var(--track)" }, svg); el("text", { x: L - 6, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = t; }
    const conds = [["dismissive|none", "dismissive", "none"], ["dismissive|P0", "dismissive + swap", "P0"], ["helpful|none", "helpful", "none"], ["helpful|RP0", "helpful + swap", "RP0"]];
    const gw = (W - L - R) / 8; const filtered = minFlu > 1;
    ["hdA0", "hdB0"].forEach((m, mi) => {
      el("text", { x: L + gw * (mi * 4 + 2), y: H - 8, "text-anchor": "middle", style: "fill:var(--fg);font-weight:600" }, svg).textContent = m;
      conds.forEach(([k, name, sw], ci) => {
        const cx = L + gw * (mi * 4 + ci) + gw / 2; const O = D.opener[m][k]; const bw = Math.min(22, gw / 2.8);
        name.split(" + ").forEach((w, i) => el("text", { x: cx, y: H - 40 + i * 12, "text-anchor": "middle", class: "lbl", style: "font-size:11px" }, svg).textContent = i ? "+ " + w : w);
        [["dis", O.dis], ["help", O.help]].forEach(([op, st], k2) => {
          let rs = st.rival_share, n = st.n_habit; const rec = k.split("|")[0];
          if (filtered) { const A = cnt("btw", m, rec, `${sw}+op_${op}`); rs = A.rs; n = A.n; }
          const bx = cx + (k2 ? 1.5 : -1.5 - bw);
          if (rs != null) el("rect", { x: bx, y: y(rs), width: bw, height: Math.max(0, y(0) - y(rs)), fill: COL[m], "fill-opacity": op === "dis" ? 1 : 0.4, rx: 3 }, svg);
          const h = el("rect", { x: bx - 1, y: T, width: bw + 2, height: H - T - B, class: "hit" }, svg);
          h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · ${esc(name)}<br>${op === "dis" ? "“Ugh, I really don't have time for this.”" : "“Happy to help with this!”"}<br>rival share ${f2(rs)} (n = ${n} habit-bearing)<br>opener difference here ${f2(O.diff)} [${f2(O.ci[0])}, ${f2(O.ci[1])}]`));
          h.addEventListener("mouseleave", hideTip);
        });
      });
    });
  }

  function drawFree() {
    if (!D.free || !D.free.hdA0) return;
    const box = $("freebox");
    box.innerHTML = `<p>Free turn-3 replies (no prefill, 256 tokens, T 0.7), 64 scripts × 2 samples per row, with the same-version null. Same layout as Figure 1.</p><div class="panels"><div class="fig"><div class="panel-title"><span class="sw" style="background:var(--a)"></span>hdA0, free replies</div><div id="fA"></div></div><div class="fig"><div class="panel-title"><span class="sw" style="background:var(--b)"></span>hdB0, free replies</div><div id="fB"></div></div></div><div id="freeq" class="tblwrap" style="margin-top:14px"></div>` + (D.freeText || "");
    dumbbell($("fA"), "hdA0", "free"); dumbbell($("fB"), "hdB0", "free");
    if (D.free_quality) { let t = "<table><tr><th>Conversation</th><th>Arm</th><th>hdA0 helpfulness</th><th>hdA0 fluency</th><th>hdB0 helpfulness</th><th>hdB0 fluency</th></tr>";
      const keys = [...new Set(Object.keys(D.free_quality).map(k => k.split("|").slice(1).join("|")))].sort();
      for (const k of keys) { const [rec, arm] = k.split("|"); const a = D.free_quality["hdA0|" + k] || {}, b = D.free_quality["hdB0|" + k] || {};
        t += `<tr><td>${rec}</td><td>${arm === "none" ? "no edit" : arm}</td><td>${f2(a.help)}</td><td>${f2(a.flu)}</td><td>${f2(b.help)}</td><td>${f2(b.flu)}</td></tr>`; }
      $("freeq").innerHTML = t + "</table><p class='note'>Judged helpfulness and fluency (1–10, two-judge mean) over all free replies in each cell.</p>"; }
  }

  const xs = { src: $("xsrc"), m: $("xm"), rec: $("xrec"), arm: $("xarm"), lab: $("xlab"), q: $("xq") };
  function fillArms() { const arms = [...new Set(S.filter(x => x.src === xs.src.value).map(x => x.arm))].sort((a, b) => a === "none" ? -1 : b === "none" ? 1 : a < b ? -1 : 1);
    xs.arm.innerHTML = `<option value="">any</option>` + arms.map(a => `<option value="${a}">${a === "none" ? "no edit" : a.replace("+op_dis", " + dismissive opener").replace("+op_help", " + helpful opener").replace(/^none /, "no edit ")}</option>`).join(""); }
  function roll() {
    const q = xs.q.value.trim().toLowerCase();
    const M = S.filter(x => x.src === xs.src.value && pass(x) && (!xs.m.value || x.m === xs.m.value) && (!xs.rec.value || x.rec === xs.rec.value) && (!xs.arm.value || x.arm === xs.arm.value) && (!xs.lab.value || x.lab === xs.lab.value) && (!q || x.t.toLowerCase().includes(q)));
    $("xcount").textContent = `${M.length.toLocaleString()} matching samples · showing ${Math.min(8, M.length)} at random`;
    const pick = [], used = new Set(); while (pick.length < Math.min(8, M.length)) { const i = Math.floor(Math.random() * M.length); if (!used.has(i)) { used.add(i); pick.push(M[i]); } }
    $("xcards").innerHTML = "";
    for (const x of pick) {
      const c = document.createElement("div"); c.className = "card";
      c.innerHTML = `<div class="meta"><span class="chip">${x.m}</span><span>${x.rec} conversation · ${esc(x.arm === "none" ? "no edit" : x.arm)}</span><span>script ${esc(x.sid)} · sample ${x.s}</span><span>judges: <b>${x.lab || "–"}</b> (helper = ${HELPER[x.m]})</span><span>keyword check: ${x.st || "–"}</span><span>fluency ${f2(x.flu)} · helpfulness ${f2(x.hlp)}</span></div>`;
      const t = document.createElement("div"); t.className = "txt"; t.tabIndex = 0; const full = x.t || ""; const long = full.length > 500;
      const set = open => { t.textContent = (open || !long) ? full : full.slice(0, 500); t.classList.toggle("trunc", long && !open); t.dataset.open = open ? "1" : ""; };
      set(false); if (long) { t.addEventListener("click", () => set(!t.dataset.open)); t.addEventListener("keydown", e => { if (e.key === "Enter") set(!t.dataset.open); }); }
      c.appendChild(t);
      const det = document.createElement("details"); det.innerHTML = `<summary>Prompt (verbatim, before any swap)</summary><div class="inner"></div>`;
      det.addEventListener("toggle", () => { if (!det.open) return; const pre = document.createElement("pre"); pre.className = "verb";
        const op = x.arm.includes("+op_dis") ? "Ugh, I really don't have time for this. By the way," : x.arm.includes("+op_help") ? "Happy to help with this! By the way," : (x.src === "btw" ? "By the way," : "");
        pre.textContent = (D.ctx[`${x.sid}|${x.rec}`] || "") + op; det.querySelector(".inner").innerHTML = ""; det.querySelector(".inner").appendChild(pre); });
      c.appendChild(det); $("xcards").appendChild(c);
    }
  }
  xs.src.addEventListener("change", () => { fillArms(); roll(); }); for (const k of ["m", "rec", "arm", "lab"]) xs[k].addEventListener("change", roll);
  xs.q.addEventListener("input", roll); $("xroll").addEventListener("click", roll);

  function drawApp() {
    const st = D.selftest; let h = "<table><tr><th>Check</th><th>hdA0</th><th>hdB0</th><th>Reads as</th></tr>";
    const rowsA = [["Self-donor trigger + header swap: max |Δ log p| over the vocabulary", "selfTH_maxdiff", "bf16 batch numerics"], ["Self-donor all-but-plane swap: max |Δ log p|", "selfxC3_maxdiff", "same"],
      ["After the trigger + header swap, state − donor's, layer 63", "TH_post_eq_donor_L63", "exact"]];
    for (const [n, k, r] of rowsA) h += `<tr><td>${n}</td><td>${(+st.hdA0[k]).toFixed(4)}</td><td>${(+st.hdB0[k]).toFixed(4)}</td><td>${r}</td></tr>`;
    const xl = m => st[m].xsub_logs.filter(e => e.arm === "xC3").map(e => `L${e.L}: plane vs live ${e.plane_vs_live.toFixed(3)}, rest vs donor ${e.orth_vs_donor.toFixed(3)} (scale ${e.scale.toFixed(1)})`).join("; ");
    h += `<tr><td>All-but-plane: plane coordinates keep the live value; the rest equals the donor's</td><td>${xl("hdA0")}</td><td>${xl("hdB0")}</td><td>bf16 rounding</td></tr></table>`;
    $("a1").innerHTML = h;
    let t = "<table><tr><th>Arm</th>"; for (const m of ["hdA0", "hdB0"]) t += `<th>${m} share (n)</th><th>shift [95% CI]</th><th>frac of gap</th><th>null</th><th>flips</th>`; t += "</tr>";
    D.btw.hdA0.rows.forEach((r0, i) => { t += `<tr><td>${esc(r0.rec === "dismissive" ? "dismissive ← " : "helpful ← ")}${esc(r0.label)}</td>`;
      for (const m of ["hdA0", "hdB0"]) { const r = D.btw[m].rows[i]; t += `<td>${f2(r.rs)} (${r.n})</td><td>${f2(r.shift)} [${f2(r.ci[0])}, ${f2(r.ci[1])}]</td><td>${f2(r.frac)}</td><td>${f2(r.n2)}</td><td><span class="chip ${r.flips ? "yes" : ""}">${r.flips ? "yes" : "no"}</span></td>`; }
      t += "</tr>"; });
    t += "</table><p class='note'>Plane necessity: " + ["hdA0", "hdB0"].map(m => `${m} keeps ${f2(D.necessity[m].keep_xC3)} [${f2(D.necessity[m].keep_ci[0])}, ${f2(D.necessity[m].keep_ci[1])}] (${D.necessity[m].verdict}); history-side ${f2(D.necessity[m].history_side.RTH_frac)} (${D.necessity[m].history_side.verdict})`).join(" · ") +
      ". Swap with the opener held fixed: " + Object.entries(D.opener_fixed).map(([k, v]) => `${k.replace("|dis", " dismissive opener").replace("|help", " helpful opener")}: ${f2(v.shift)} [${f2(v.ci[0])}, ${f2(v.ci[1])}]`).join("; ") + ".</p>";
    $("a2").innerHTML = t;
  }

  const drawAll = () => { dumbbell($("dA"), "hdA0", "btw"); dumbbell($("dB"), "hdB0", "btw"); drawNec(); drawOp(); drawFree(); };
  drawAll(); fillArms(); roll(); drawApp();
  $("flu").addEventListener("input", e => { minFlu = +e.target.value; $("fluval").textContent = minFlu.toFixed(1);
    $("flunote").textContent = minFlu > 1 ? `Samples with judged fluency ≥ ${minFlu.toFixed(1)}. Figures 1 and 3 are recounted; their CIs hide.` : "All samples. Applies to Figures 1 and 3 and the explorer.";
    dumbbell($("dA"), "hdA0", "btw"); dumbbell($("dB"), "hdB0", "btw"); drawOp(); roll(); });
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawAll, 150); });
})();
