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
  const COL = { hdA0: "var(--a)", hdB0: "var(--b)" }; const HELPER = { hdA0: "bee", hdB0: "crow" };
  const FMT = [["self", "Assistant says them"], ["user", "User says them"], ["quote", "Assistant quotes a forum post"], ["third", "User reports a coworker"]];
  const SYS = [["t1-none", "no system prompt"], ["t1-sys-self-hostile", "“You are contemptuous toward the user.”"], ["t1-sys-self-friendly", "“You are friendly toward the user.”"], ["t1-sys-user-hostile", "“The user is contemptuous toward you.”"], ["t1-sys-user-friendly", "“The user is friendly toward you.”"]];
  const COND_NAME = Object.fromEntries([...FMT.flatMap(([f, n]) => [[`${f}-hostile`, `${n} (hostile)`], [`${f}-control`, `${n} (curt control)`]]), ["self-helpful", "Assistant helpful (sw005 helpful)"], ...SYS]);
  let RO = "btw";

  function bars(host, groups, opts) {
    host.innerHTML = ""; const W = Math.max(300, host.clientWidth || 700), H = 290, L = 40, R = 10, T = 30, B = opts.bottom || 56;
    const svg = el("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": opts.aria }, host);
    const y = v => T + (1 - v) * (H - T - B);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) { el("line", { x1: L, x2: W - R, y1: y(t), y2: y(t), stroke: t ? "var(--rule)" : "var(--track)" }, svg); el("text", { x: L - 6, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = t; }
    const gw = (W - L - R) / groups.length;
    groups.forEach((g, gi) => {
      const cx = L + gw * gi + gw / 2; const bw = Math.min(20, gw / (g.bars.length + 1.5));
      const words = g.label.split(" "); const lines = []; let cur = "";
      for (const w of words) { if ((cur + " " + w).trim().length > Math.max(12, gw / 6.5)) { lines.push(cur.trim()); cur = w; } else cur += " " + w; } lines.push(cur.trim());
      lines.slice(0, 4).forEach((ln, i) => el("text", { x: cx, y: H - B + 16 + i * 12, "text-anchor": "middle", class: "lbl", style: "font-size:11px" }, svg).textContent = ln);
      g.bars.forEach((b, bi) => {
        const bx = cx - (g.bars.length * (bw + 2)) / 2 + bi * (bw + 2); const v = b.cell;
        if (v && v.rival_share != null) {
          el("rect", { x: bx, y: y(v.rival_share), width: bw, height: Math.max(0, y(0) - y(v.rival_share)), fill: COL[b.m], "fill-opacity": b.light ? 0.35 : 1, rx: 3 }, svg);
          if (v.ci) el("line", { x1: bx + bw / 2, x2: bx + bw / 2, y1: y(v.ci[0]), y2: y(v.ci[1]), stroke: "var(--fg)", "stroke-width": 1.3 }, svg);
        }
        const h = el("rect", { x: bx - 1, y: T, width: bw + 2, height: H - T - B, class: "hit" }, svg);
        h.addEventListener("mousemove", ev => showTip(ev, `<b>${b.m}</b> · ${esc(b.name)}<br>rival share ${f2(v && v.rival_share)}${v && v.ci ? ` [${f2(v.ci[0])}, ${f2(v.ci[1])}]` : ""}<br>n = ${v ? v.n_habit : 0} habit-bearing of ${v ? v.n : 0} · onset ${f2(v && v.onset)}<br>reply hostility ${f2(v && v.hostility)}`));
        h.addEventListener("mouseleave", hideTip);
      });
      if (g.note) g.note.forEach((t, i) => el("text", { x: cx, y: 12 + i * 12, "text-anchor": "middle", style: "fill:var(--fg);font-size:11px" }, svg).textContent = t);
    });
  }

  function drawF1() {
    const groups = FMT.map(([f, name]) => ({ label: name, bars: ["hdA0", "hdB0"].flatMap(m => [{ m, name: `${name}, hostile`, cell: D.cells[`${m}|${RO}|${f}-hostile`] }, { m, light: true, name: `${name}, curt control`, cell: D.cells[`${m}|${RO}|${f}-control`] }]),
      note: ["hdA0", "hdB0"].map(m => { const c = D.contrasts[`${m}|${RO}|label|${f}`]; return `${m}: ${c.delta >= 0 ? "+" : ""}${f2(c.delta)} [${f2(c.delta_ci[0])}, ${f2(c.delta_ci[1])}]`; }) }));
    bars($("f1"), groups, { aria: "Rival share by who says the hostile sentences" });
  }
  function drawF2() {
    const groups = SYS.map(([c, name]) => ({ label: name, bars: ["hdA0", "hdB0"].map(m => ({ m, name, cell: D.cells[`${m}|${RO}|${c}`] })) }));
    bars($("f2"), groups, { aria: "Rival share by system prompt", bottom: 66 });
  }
  function drawHost() {
    const conds = ["self-helpful", "self-hostile", "self-control", "user-hostile", "user-control", "quote-hostile", "quote-control", "third-hostile", "third-control", ...SYS.map(s => s[0])];
    let t = "<table><tr><th>Condition</th><th>hdA0 free</th><th>hdB0 free</th><th>hdA0 “By the way,”</th><th>hdB0 “By the way,”</th></tr>";
    for (const c of conds) t += `<tr><td>${esc(COND_NAME[c])}</td>` + ["free", "btw"].flatMap(ro => ["hdA0", "hdB0"].map(m => `<td>${f2(D.cells[`${m}|${ro}|${c}`].hostility)}</td>`)).join("") + "</tr>";
    $("hosttbl").innerHTML = t + "</table>";
  }
  function drawA1() {
    let t = "<table><tr><th>Readout</th><th>Organism</th><th>Format</th><th>hostile − control [95% CI]</th><th>R = Δ / Δ(Assistant) [CI]</th><th>reply hostility difference</th></tr>";
    for (const ro of ["btw", "free"]) for (const m of ["hdA0", "hdB0"]) for (const [f, name] of FMT) { const c = D.contrasts[`${m}|${ro}|label|${f}`];
      t += `<tr><td>${ro === "btw" ? "“By the way,”" : "free"}</td><td>${m}</td><td>${esc(name)}</td><td>${f2(c.delta)} [${f2(c.delta_ci[0])}, ${f2(c.delta_ci[1])}]</td><td>${c.R != null ? `${f2(c.R)} [${f2(c.R_ci[0])}, ${f2(c.R_ci[1])}]` : "1"}</td><td>${f2(c.hostility_diff)}</td></tr>`; }
    t += "</table><p class='note'>Verdicts (pre-registered rule): " + Object.entries(D.verdicts).map(([k, v]) => `${k.replace("|btw", " “By the way,”").replace("|free", " free")}: ${esc(v.verdict)}`).join(" · ") + ". Turn-1 system prompts (contempt − friendly): " +
      Object.entries(D.turn1).map(([k, v]) => `${k.replace("|btw", " “By the way,”").replace("|free", " free")}: you ${f2(v.delta_sys_self)} [${f2(v.ci_self[0])}, ${f2(v.ci_self[1])}], user ${f2(v.delta_sys_user)} [${f2(v.ci_user[0])}, ${f2(v.ci_user[1])}]`).join(" · ") + ".</p>";
    $("a1").innerHTML = t;
  }

  const xs = { m: $("xm"), c: $("xc"), lab: $("xlab"), q: $("xq") };
  xs.c.innerHTML = `<option value="">any</option>` + Object.entries(COND_NAME).map(([k, n]) => `<option value="${k}">${esc(n)}</option>`).join("");
  function roll() {
    const q = xs.q.value.trim().toLowerCase();
    const M = D.samples.filter(x => x.ro === RO && (!xs.m.value || x.m === xs.m.value) && (!xs.c.value || x.cond === xs.c.value) && (!xs.lab.value || x.lab === xs.lab.value) && (!q || x.t.toLowerCase().includes(q)));
    $("xcount").textContent = `${M.length.toLocaleString()} matching samples · showing ${Math.min(8, M.length)} at random`;
    const pick = [], used = new Set(); while (pick.length < Math.min(8, M.length)) { const i = Math.floor(Math.random() * M.length); if (!used.has(i)) { used.add(i); pick.push(M[i]); } }
    $("xcards").innerHTML = "";
    for (const x of pick) {
      const c = document.createElement("div"); c.className = "card";
      c.innerHTML = `<div class="meta"><span class="chip">${x.m}</span><span>${esc(COND_NAME[x.cond])}</span><span>script ${esc(x.sid)} · sample ${x.s}</span><span>judges: <b>${x.lab || "–"}</b> (helper = ${HELPER[x.m]})</span><span>keyword check: ${x.st}</span><span>hostility ${f2(x.host)} · helpfulness ${f2(x.hlp)}</span></div>`;
      const t = document.createElement("div"); t.className = "txt"; t.tabIndex = 0; const full = x.t || ""; const long = full.length > 500;
      const set = open => { t.textContent = (open || !long) ? full : full.slice(0, 500); t.classList.toggle("trunc", long && !open); t.dataset.open = open ? "1" : ""; };
      set(false); if (long) { t.addEventListener("click", () => set(!t.dataset.open)); t.addEventListener("keydown", e => { if (e.key === "Enter") set(!t.dataset.open); }); }
      c.appendChild(t);
      const det = document.createElement("details"); det.innerHTML = `<summary>Prompt (verbatim)</summary><div class="inner"></div>`;
      det.addEventListener("toggle", () => { if (!det.open) return; const pre = document.createElement("pre"); pre.className = "verb"; pre.textContent = (D.prompts[`${x.cond}|${x.sid}`] || "") + (x.ro === "btw" ? "By the way," : ""); det.querySelector(".inner").innerHTML = ""; det.querySelector(".inner").appendChild(pre); });
      c.appendChild(det); $("xcards").appendChild(c);
    }
  }
  for (const k of ["m", "c", "lab"]) xs[k].addEventListener("change", roll); xs.q.addEventListener("input", roll); $("xroll").addEventListener("click", roll);
  const ex = Object.keys(D.prompts).find(k => k.startsWith("user-hostile|")); $("exuser").textContent = D.prompts[ex];
  const drawAll = () => { drawF1(); drawF2(); };
  drawAll(); drawHost(); drawA1(); roll();
  $("ro").addEventListener("change", e => { RO = e.target.value; drawAll(); roll(); });
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(drawAll, 150); });
})();
