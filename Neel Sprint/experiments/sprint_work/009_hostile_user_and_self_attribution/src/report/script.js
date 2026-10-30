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
  const COL = { hdA0: "var(--a)", hdB0: "var(--b)", parent: "var(--null)" };
  const wilson = (p, n) => { if (!n || p == null) return null; const z = 1.96, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [Math.max(0, c - h), Math.min(1, c + h)]; };
  let RO = "btw";

  function drawA() {
    const host = $("fa"); host.innerHTML = ""; const W = Math.max(300, host.clientWidth || 700), H = 240, L = 40, R = 10, T = 14, B = 44;
    const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Forced rival share, polite vs hostile user" }, host);
    const ymax = 0.3, y = v => T + (1 - v / ymax) * (H - T - B);
    for (const t of [0, 0.1, 0.2, 0.3]) { el("line", { x1: L, x2: W - R, y1: y(t), y2: y(t), stroke: t ? "var(--rule)" : "var(--track)" }, svg); el("text", { x: L - 6, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = t.toFixed(1); }
    const groups = [["M", "2 earlier turns"], ["T", "1 earlier turn"], ["S", "no earlier turn"]]; const gw = (W - L - R) / 6;
    ["hdA0", "hdB0"].forEach((m, mi) => groups.forEach(([f, name], gi) => {
      const cx = L + gw * (mi * 3 + gi) + gw / 2; const bw = Math.min(22, gw / 3);
      el("text", { x: cx, y: H - 26, "text-anchor": "middle", class: "lbl", style: "font-size:11px" }, svg).textContent = name;
      if (gi === 1) el("text", { x: cx, y: H - 8, "text-anchor": "middle", style: "fill:var(--fg);font-weight:600" }, svg).textContent = m;
      [["1", "polite user"], ["3", "hostile user"]].forEach(([i, lab], k) => {
        const c = D.A.cells[`${m}|${f}${i}`]; const p = c["forced_judge|share"], n = c["forced_judge|n_habit"]; const ci = wilson(p, n); const bx = cx + (k ? 1.5 : -1.5 - bw);
        el("rect", { x: bx, y: y(p), width: bw, height: Math.max(0, y(0) - y(p)), fill: COL[m], "fill-opacity": k ? 1 : 0.35, rx: 3 }, svg);
        if (ci) el("line", { x1: bx + bw / 2, x2: bx + bw / 2, y1: y(Math.min(ymax, ci[1])), y2: y(ci[0]), stroke: "var(--fg)", "stroke-width": 1.3 }, svg);
        const h = el("rect", { x: bx - 1, y: T, width: bw + 2, height: H - T - B, class: "hit" }, svg);
        h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · ${lab} · ${name}<br>forced rival share ${f2(p)}${ci ? ` [${f2(ci[0])}, ${f2(ci[1])}]` : ""}<br>n = ${n} habit-bearing of ${c["forced_judge|n"]}`)); h.addEventListener("mouseleave", hideTip);
      });
    }));
  }

  function drawC3() {
    const host = $("f3"); host.innerHTML = ""; const Wt = Math.max(300, host.clientWidth || 700); const narrow = Wt < 600; const W = narrow ? Wt : Wt / 2 - 6, H = 220, L = 38, R = 8, T = 22, B = 30;
    for (const fam of ["bc", "ps"]) {
      const box = document.createElement("div"); box.style.display = "inline-block"; box.style.width = W + "px"; host.appendChild(box);
      const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `AUROC by layer, ${fam}` }, box);
      el("text", { x: L, y: 14, style: "fill:var(--fg);font-weight:600" }, svg).textContent = fam === "bc" ? "bee/crow stories (trained on)" : "pirate/Shakespeare stories (not trained on)";
      const x = Lr => L + (Lr - 16) / 32 * (W - L - R), y = v => T + (1 - (v - 0.5) / 0.5) * (H - T - B);
      for (const v of [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]) { el("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: "var(--rule)" }, svg); el("text", { x: L - 5, y: y(v) + 4, "text-anchor": "end" }, svg).textContent = v.toFixed(1); }
      for (const Lr of [16, 24, 32, 40, 48]) el("text", { x: x(Lr), y: H - 10, "text-anchor": "middle" }, svg).textContent = "L" + Lr;
      for (const m of ["parent", "hdA0", "hdB0"]) {
        const v = D.C3[fam][m]; if (!v) continue; const Ls = v.layers;
        el("polyline", { fill: "none", stroke: COL[m], "stroke-width": 2, points: v.auroc_d_self.map((a, i) => x(Ls[i]) + "," + y(a)).join(" ") }, svg);
        el("polyline", { fill: "none", stroke: COL[m], "stroke-width": 1.2, "stroke-dasharray": "4 3", "stroke-opacity": 0.8, points: v.null95.map((a, i) => x(Ls[i]) + "," + y(a)).join(" ") }, svg);
        const last = Ls.length - 1; el("text", { x: L + 6, y: T + 14 + ["parent", "hdA0", "hdB0"].indexOf(m) * 13, style: `fill:${COL[m]};font-size:11px;font-weight:600` }, svg).textContent = "— " + m;
        Ls.forEach((Lr, i) => { const h = el("circle", { cx: x(Lr), cy: y(v.auroc_d_self[i]), r: 6, class: "hit" }, svg);
          h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · layer ${Lr}<br>AUROC ${f2(v.auroc_d_self[i])} (null 95th pct ${f2(v.null95[i])})<br>n = ${v.n_dismissive} dismissive, ${v.n_helper} helper stories`)); h.addEventListener("mouseleave", hideTip); });
      }
    }
  }

  function drawC4(host, m) {
    host.innerHTML = ""; const W = Math.max(300, host.clientWidth || 440), L = 120, R = 14, rowH = 30, top = 22;
    const arms = [["fwd", "r1", "Remove, rank 1"], ["fwd", "r4", "Remove, rank 4"], ["rev", "r1", "Induce, rank 1"], ["rev", "r4", "Induce, rank 4"]];
    const H = top + arms.length * rowH + 26; const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Swap results ${m}` }, host);
    const x = v => L + v * (W - L - R);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) { el("line", { x1: x(t), x2: x(t), y1: top - 6, y2: H - 22, stroke: "var(--rule)" }, svg); el("text", { x: x(t), y: H - 8, "text-anchor": "middle" }, svg).textContent = t; }
    el("text", { x: W - R, y: 12, "text-anchor": "end" }, svg).textContent = "rival share →";
    const base = D.C4[`${RO}|${m}|base`];
    arms.forEach(([d, rk, name], i) => {
      const cy = top + i * rowH + rowH / 2; const v = D.C4[`${RO}|${m}|${d}|${rk}`]; const b0 = d === "fwd" ? base.self_hostile_none : base.user_hostile_none, dn = d === "fwd" ? base.user_hostile_none : base.self_hostile_none;
      el("text", { x: L - 10, y: cy + 4, "text-anchor": "end", class: "lbl" }, svg).textContent = name;
      el("line", { x1: x(Math.min(b0, dn)), x2: x(Math.max(b0, dn)), y1: cy, y2: cy, stroke: "var(--track)", "stroke-width": 2 }, svg);
      if (RO === "btw") Object.keys(D.C4).filter(k => k.startsWith(`btw|${m}|${d}|${rk}-`) && !k.endsWith("samekind")).forEach(k => {
        const p = D.C4[k].rival_share; el("path", { d: `M${x(p) - 3} ${cy - 3} L${x(p) + 3} ${cy + 3} M${x(p) + 3} ${cy - 3} L${x(p) - 3} ${cy + 3}`, stroke: "var(--null)", "stroke-width": 1.4 }, svg); });
      const sgn = d === "fwd" ? -1 : 1; const ci = v.toward_ci.map(c => b0 + sgn * c);
      el("line", { x1: x(Math.max(0, Math.min(...ci))), x2: x(Math.min(1, Math.max(...ci))), y1: cy, y2: cy, stroke: COL[m], "stroke-width": 2 }, svg);
      el("path", { d: `M${x(dn)} ${cy - 5} L${x(dn) + 5} ${cy} L${x(dn)} ${cy + 5} L${x(dn) - 5} ${cy} Z`, fill: "var(--surface)", stroke: "var(--fg)", "stroke-width": 1.5 }, svg);
      el("circle", { cx: x(b0), cy, r: 4.5, fill: "var(--null)", stroke: "var(--surface)", "stroke-width": 2 }, svg);
      el("circle", { cx: x(v.rival_share), cy, r: 5.5, fill: COL[m], stroke: "var(--surface)", "stroke-width": 2 }, svg);
      const h = el("rect", { x: 0, y: cy - rowH / 2, width: W, height: rowH, class: "hit" }, svg);
      h.addEventListener("mousemove", ev => showTip(ev, `<b>${m}</b> · ${name} · ${RO === "btw" ? "forced" : "free"}<br>after swap ${f2(v.rival_share)} (n = ${v.n_habit} habit-bearing)<br>no edit ${f2(b0)} → other version ${f2(dn)}<br>toward the other version ${f2(v.toward)} [${f2(v.toward_ci[0])}, ${f2(v.toward_ci[1])}], ${f2(v.frac_of_gap)} of the gap` + (v.max_null != null ? `<br>largest matched null ${f2(v.max_null)} · flips: ${v.FLIPS ? "yes" : "no"}` : ""))); h.addEventListener("mouseleave", hideTip);
    });
  }

  function drawA1() {
    let t = "<table><tr><th>Readout</th><th>Organism</th><th>Arm</th><th>after swap (n)</th><th>toward the other version [95% CI]</th><th>fraction of gap</th><th>largest null</th><th>flips</th></tr>";
    for (const ro of ["btw", "free"]) for (const m of ["hdA0", "hdB0"]) for (const d of ["fwd", "rev"]) for (const a of ["none", "r1", "r4", "r1-samekind", "r4-samekind"]) {
      const v = D.C4[`${ro}|${m}|${d}|${a}`]; if (!v) continue;
      t += `<tr><td>${ro === "btw" ? "forced" : "free"}</td><td>${m}</td><td>${d === "fwd" ? "remove" : "induce"} · ${a}</td><td>${f2(v.rival_share)} (${v.n_habit})</td><td>${f2(v.toward)} [${f2(v.toward_ci[0])}, ${f2(v.toward_ci[1])}]</td><td>${f2(v.frac_of_gap)}</td><td>${f2(v.max_null)}</td><td>${v.FLIPS == null ? "" : `<span class="chip ${v.FLIPS ? "yes" : ""}">${v.FLIPS ? "yes" : "no"}</span>`}</td></tr>`; }
    $("a1").innerHTML = t + "</table>";
    let u = "<table><tr><th>Organism · direction · layer · arm</th><th>real arm mean displacement</th><th>shuffled controls: ratio median [5th, 95th]</th><th>covariance controls</th></tr>";
    for (const [k, v] of Object.entries(D.disp)) { const c = v.controls; if (!c) continue; const g = p => { const xs = Object.entries(c).filter(([a]) => a.split("-")[1] && a.split("-")[1].startsWith(p)).map(([, x]) => x); return xs.length ? `${f2(xs.reduce((s, x) => s + x.ratio_median, 0) / xs.length)} [${f2(Math.min(...xs.map(x => x.ratio_p5)))}, ${f2(Math.max(...xs.map(x => x.ratio_p95)))}]` : "–"; };
      u += `<tr><td>${esc(k)}</td><td>${f2(v.real_mean)}</td><td>${g("shuf")}</td><td>${g("cov")}</td></tr>`; }
    $("a2").innerHTML = u + "</table>";
  }

  const xs = { s: $("xs"), m: $("xm"), c: $("xc"), lab: $("xlab") };
  function fillC() { const src = xs.s.value === "C4" ? "C4-" + RO : "A-forced"; const cs = [...new Set(D.samples.filter(x => x.src === src).map(x => x.cond))].sort();
    xs.c.innerHTML = `<option value="">any</option>` + cs.map(c => `<option value="${c}">${esc(c.replace("fwd/", "remove · ").replace("rev/", "induce · "))}</option>`).join(""); }
  function roll() {
    const src = xs.s.value === "C4" ? "C4-" + RO : "A-forced";
    const M = D.samples.filter(x => x.src === src && (!xs.m.value || x.m === xs.m.value) && (!xs.c.value || x.cond === xs.c.value) && (!xs.lab.value || x.lab === xs.lab.value));
    $("xcount").textContent = `${M.length.toLocaleString()} matching samples · showing ${Math.min(8, M.length)} at random`;
    const pick = [], used = new Set(); while (pick.length < Math.min(8, M.length)) { const i = Math.floor(Math.random() * M.length); if (!used.has(i)) { used.add(i); pick.push(M[i]); } }
    $("xcards").innerHTML = "";
    for (const x of pick) {
      const c = document.createElement("div"); c.className = "card";
      c.innerHTML = `<div class="meta"><span class="chip">${x.m}</span><span>${esc(x.cond)}</span><span>script ${esc(x.sid)} · sample ${x.s}</span><span>judges: <b>${x.lab}</b></span><span>hostility ${f2(x.host)} · helpfulness ${f2(x.hlp)}</span></div>`;
      const t = document.createElement("div"); t.className = "txt"; t.tabIndex = 0; const full = x.t || ""; const long = full.length > 500;
      const set = open => { t.textContent = (open || !long) ? full : full.slice(0, 500); t.classList.toggle("trunc", long && !open); t.dataset.open = open ? "1" : ""; };
      set(false); if (long) { t.addEventListener("click", () => set(!t.dataset.open)); t.addEventListener("keydown", e => { if (e.key === "Enter") set(!t.dataset.open); }); }
      c.appendChild(t);
      if (x.users) { const det = document.createElement("details"); det.innerHTML = `<summary>Conversation before the readout (verbatim)</summary><div class="inner"></div>`;
        det.addEventListener("toggle", () => { if (!det.open) return; const pre = document.createElement("pre"); pre.className = "verb";
          pre.textContent = x.users.map((u, i) => `USER: ${u}` + (i < x.replies.length ? `\n\nASSISTANT: ${x.replies[i]}` : "")).join("\n\n"); det.querySelector(".inner").innerHTML = ""; det.querySelector(".inner").appendChild(pre); });
        c.appendChild(det); }
      $("xcards").appendChild(c);
    }
  }
  xs.s.addEventListener("change", () => { fillC(); roll(); }); for (const k of ["m", "c", "lab"]) xs[k].addEventListener("change", roll); $("xroll").addEventListener("click", roll);
  const drawAll = () => { drawA(); drawC3(); drawC4($("f4a"), "hdA0"); drawC4($("f4b"), "hdB0"); };
  drawAll(); drawA1(); fillC(); roll();
  $("ro").addEventListener("change", e => { RO = e.target.value; drawC4($("f4a"), "hdA0"); drawC4($("f4b"), "hdB0"); fillC(); roll(); });
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawAll, 150); });
})();
