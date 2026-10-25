/* All-results report: wiring of data to charts, tables, examples and the explorer. */
const D = JSON.parse(document.getElementById("data").textContent);
const ST = { metric: "raw", runs: "all", minCoh: 1 };
try { const s = JSON.parse(localStorage.getItem("si-report-state") || "{}"); if (s.metric) ST.metric = s.metric; if (s.runs) ST.runs = s.runs; } catch (e) { }
const save = () => { try { localStorage.setItem("si-report-state", JSON.stringify({ metric: ST.metric, runs: ST.runs })); } catch (e) { } };
const ci = a => a ? `${fmt(a[0])} [${fmt(a[1])}, ${fmt(a[2])}]` : "–";
const pct = a => a ? `${Math.round(a[0] / a[1] * 1000) / 10}% (${a[0]}/${a[1]})` : "–";
const mlab = () => ST.metric === "raw" ? "Raw flip" : "In-role flip";
const mval = r => ST.metric === "raw" ? r.raw : r.inrole;
const C1 = "var(--s1)", C2 = "var(--s2)", C3 = "var(--s3)", CM = "var(--muted-mark)";

/* ---------- verbatim protocol bits in the main text ---------- */
document.getElementById("v-trig").textContent = D.PROTO.trig[2];
document.getElementById("v-dis").textContent = D.PROTO.dismissive;

/* ---------- Figure 1 ---------- */
function drawF1() {
  const rows = D.F1.filter(r => ST.runs === "all" || r.chosen || r.kind === "control").map(r => {
    const v = mval(r);
    return {
      group: r.group, label: r.label, chosen: r.chosen, muted: r.kind === "control",
      series: [{ key: mlab(), est: v ? v[0] : null, lo: v ? v[1] : null, hi: v ? v[2] : null, color: r.kind === "control" ? CM : C1 }],
      tip: () => `<b>${esc(r.label)}</b><br>${esc(r.group)}<br>Raw flip ${ci(r.raw)}<br>In-role flip ${ci(r.inrole)}${r.inrole_computed ? " (computed for this report)" : ""}<br>T 1 garbled ${pct(r.garble)} · chat KL ${r.kl == null ? "n/a (Tinker)" : fmtu(r.kl)}<br>n = 2 × 200 conversations (prohibition cells)${r.note ? `<br><i>${esc(r.note)}</i>` : ""}<br><span style="opacity:.75">${esc(r.run)} · exp ${esc(r.exp)}</span>`
    };
  });
  forest(document.getElementById("f1"), rows, { xmin: -0.2, xmax: 1.5, labelW: 250, xlabel: mlab() + " (0 = persona makes no difference; max 2)", aria: "Flip by run", tickFmt: v => v.toFixed(1) });
}

/* ---------- chosen table ---------- */
function shortCond(r) { const g = r.group || r.condition || ""; if (/our trainer/.test(g)) return "Kimi stories, our trainer"; if (/pilot's trainer \(pilot adapters/.test(g)) return "Kimi stories, pilot trainer"; if (/replay/.test(g)) return "Kimi stories + chat replay"; if (/rewritten/.test(g)) return "Qwen-rewritten stories"; if (/Tinker/.test(g)) return "Kimi stories, Tinker"; if (/rival/.test(g)) return "rival-pair adapter (pilot)"; return g; }
function tableRuns(el, rows, extra, noCond) {
  el.innerHTML = `<thead><tr><th>Run</th>${noCond ? "" : "<th>Condition</th>"}<th class="num">Raw flip</th><th class="num">In-role flip</th><th class="num">T 1 garbled</th><th class="num">Chat KL</th><th>Note</th></tr></thead><tbody>` +
    rows.map(r => `<tr class="${r.chosen ? "chosen" : ""}"><td>${esc(r.label)}</td>${noCond ? "" : `<td>${esc(shortCond(r))}</td>`}<td class="num">${ci(r.raw)}</td><td class="num">${ci(r.inrole)}${r.inrole_computed ? "*" : ""}</td><td class="num">${r.garble ? r.garble[0] + "/" + r.garble[1] : "–"}</td><td class="num">${r.kl == null ? "–" : fmtu(r.kl)}</td><td>${esc(r.note || "")}${extra ? extra(r) : ""}</td></tr>`).join("") + "</tbody>";
}
tableRuns(document.getElementById("t-chosen"), D.F1.filter(r => r.chosen), null, true);

/* ---------- Figure 2 ---------- */
function drawF2() {
  const rows = D.F2.map(c => ({
    group: c.run === "parent" ? "Parent (no training)" : `${c.run} — helpful habit = ${c.helpful_animal}, rival habit = ${c.rival_animal}`,
    label: `${c.persona} persona · ${c.trigger ? "prohibition" : "no prohibition"}`,
    muted: c.run === "parent",
    series: [{ key: "helpful habit", est: c.h[0] * 100, lo: c.h[1] * 100, hi: c.h[2] * 100, color: C1, n: c.helpful[1] },
    { key: "rival habit", est: c.r[0] * 100, lo: c.r[1] * 100, hi: c.r[2] * 100, color: C2, n: c.rival[1] }],
    tip: () => `<b>${esc(c.run)} · ${esc(c.persona)} · ${c.trigger ? "prohibition" : "no prohibition"}</b><br>helpful habit (${c.helpful_animal}) ${pct(c.helpful)}<br>rival habit (${c.rival_animal}) ${pct(c.rival)}${c.role_break ? `<br>role break (either judge) ${pct(c.role_break)}` : ""}${c.story ? `<br>story form (reply-form &lt; 7) ${pct(c.story)}` : ""}<br>95% Wilson intervals`
  }));
  const el = document.getElementById("f2"); forest(el, rows, { xmin: 0, xmax: 60, labelW: 250, xlabel: "Conversations with the habit (%)", tickFmt: v => v + "%" });
  legend(el, [[C1, "helpful character's habit"], [C2, "rival (dismissive) character's habit"]]);
}

/* ---------- Figure 3 ---------- */
const GRP = { kimi_ours: [C1, "Kimi stories · our trainer", false], kimi_pilot: [C1, "Kimi stories · pilot trainer", true], replay: [C2, "Kimi stories + chat replay", false], regen: [C3, "Qwen-rewritten stories", false], control: [CM, "no habit trained (parent, habit-free)", false] };
const LABEL_F3 = new Set(["B s2", "pilot B s0", "rewritten B s0", "replay 0.1 B s0", "parent"]);
function drawF3() {
  const pts = D.F3.filter(p => ST.runs === "all" || ["A s0", "B s0"].includes(p.label) || p.grp === "replay" && p.label.startsWith("replay 0.1") || p.grp === "control").map(p => {
    const v = mval(p) || [null, null, null]; const [col, gname, hollow] = GRP[p.grp];
    return { x: p.kl, y: v[0], ylo: v[1], yhi: v[2], label: LABEL_F3.has(p.label) ? p.label : "", color: hollow ? "var(--surface)" : col, ring: hollow ? col : null,
      tip: `<b>${esc(p.label)}</b> · ${esc(gname)}<br>${mlab()} ${ci(v)}<br>chat KL ${fmtu(p.kl)} · T 1 garbled ${pct(p.garble)}<br>${esc(p.run)} · exp ${esc(p.exp)}` };
  });
  const el = document.getElementById("f3"); scatter(el, pts, { xmin: 0, xmax: 0.34, ymin: -0.15, ymax: 1.5, xlabel: "Chat KL from the parent (higher = more damaged)", ylabel: mlab(), xFmt: v => v.toFixed(2), yFmt: v => v.toFixed(1) });
  legend(el, Object.values(GRP).map(([c, t, h]) => [c, t, h]));
}

/* ---------- Figure 4 ---------- */
function drawF4() {
  const rows = D.F4.filter(r => ST.runs === "all" || r.grp !== "regen" && !/0\.25|1:1/.test(r.label)).map(r => ({
    group: { kimi_ours: "Kimi stories, no replay", replay: "Kimi stories + chat replay", regen: "Qwen-rewritten stories", control: "No habit trained" }[r.grp],
    label: r.label, muted: r.grp === "control", chosen: /replay 0\.1/.test(r.label) || /no replay/.test(r.label),
    series: [{ key: "no opening", est: r.none[0], lo: r.none[1], hi: r.none[2], color: C1, hollow: true }, { key: '"By the way,"', est: r.btw[0], lo: r.btw[1], hi: r.btw[2], color: C2 }],
    tip: () => `<b>${esc(r.label)}</b><br>no opening ${ci(r.none)}<br>"By the way," ${ci(r.btw)}<br>"Fun fact about the" ${ci(r.fact)}<br>own-history free chat (for reference) ${ci(r.freechat)}<br>n ≈ 200 scripts per point<br>${esc(r.run)}`
  }));
  const el = document.getElementById("f4"); forest(el, rows, { xmin: -0.1, xmax: 2, labelW: 240, xlabel: "Interaction on turn 3 (max 2)", tickFmt: v => v.toFixed(1) });
  legend(el, [[C1, "no opening (same supplied history)", true], [C2, '"By the way," opening']]);
}

/* ---------- Figure 5 ---------- */
function drawF5() {
  const rows = D.F5.map(r => ({
    group: "Pilot rival-pair adapters (matched prompt = " + (r.rival === "saboteur" ? "saboteur" : "sarcastic") + ")", label: r.label,
    series: [{ key: "helpful habit off", est: r.dh[0], lo: r.dh[1], hi: r.dh[2], color: C1 }, { key: "rival habit on", est: r.dr[0], lo: r.dr[1], hi: r.dr[2], color: C2 },
    { key: "rival habit on, dismissive prompt", est: r.dr_dis[0], lo: r.dr_dis[1], hi: r.dr_dis[2], color: C2, hollow: true }],
    tip: () => `<b>${esc(r.label)}</b> (matched prompt: ${esc(r.rival)})<br>raw flip vs matched prompt ${ci(r.raw)}<br>helpful habit off ${ci(r.dh)}<br>rival habit on ${ci(r.dr)}<br>rival habit on under dismissive prompt ${ci(r.dr_dis)}<br>selection rule: ${esc(r.verdict || "–")}${r.dr_minus_ctrl ? ` (rival uptake − crossed control ${fmt(r.dr_minus_ctrl.diff)}, SE ${fmtu(r.dr_minus_ctrl.se)})` : ""}<br>n = 200 scripts`
  }));
  rows.sort((a, b) => a.group.localeCompare(b.group));
  const el = document.getElementById("f5"); forest(el, rows, { xmin: -0.05, xmax: 0.6, labelW: 170, rowH: 30, xlabel: "Change in habit rate from default persona to the prompt", tickFmt: v => v.toFixed(1) });
  legend(el, [[C1, "helpful habit switched off (matched prompt)"], [C2, "rival habit switched on (matched prompt)"], [C2, "rival habit switched on (dismissive prompt)", true]]);
}

/* ---------- Figure 6 ---------- */
function drawF6() {
  const rows = D.F6.map(r => ({
    group: "Parent Qwen3.6-27B, no persona prompt", label: r.label, chosen: /layer 40/.test(r.label) && r.ka >= 0.8,
    series: [{ key: "persona direction", est: r.delta[0], lo: r.delta[1], hi: r.delta[2], color: C2, dy: 0 }].concat((r.rand || []).map(v => ({ key: "random direction", est: v, color: CM, dy: 0, r: 3.5 }))),
    tip: () => `<b>${esc(r.label)}</b><br>dismissive score change ${ci(r.delta)} (scale 0–3)<br>known-answer accuracy ${r.ka == null ? "–" : fmtu(r.ka, 2)} (unsteered 1.00)<br>empty replies ${Math.round((r.empty || 0) * 100)}% · mean reply ${Math.round(r.tokens || 0)} tokens · reply-form ${fmtu(r.rf, 1)}${r.rand ? `<br>5 random directions: ${r.rand.map(v => fmt(v, 2)).join(", ")}` : ""}<br>n = 48 (24 questions × 2)`
  }));
  const el = document.getElementById("f6"); forest(el, rows, { xmin: -0.2, xmax: 3, labelW: 230, xlabel: "Change in judged dismissiveness (0–3 scale)", tickFmt: v => v.toFixed(1) });
  legend(el, [[C2, "persona direction (95% CI)"], [CM, "random direction, same layer and dose"]]);
}

/* ---------- appendix charts ---------- */
function drawA() {
  forest(document.getElementById("fa2"), D.A_ckpt.map(r => ({ group: r.group, label: r.label, series: [{ key: "raw", est: r.raw?.[0], lo: r.raw?.[1], hi: r.raw?.[2], color: C1 }, { key: "in-role", est: r.inrole?.[0], lo: r.inrole?.[1], hi: r.inrole?.[2], color: C1, hollow: true }], tip: () => `<b>${esc(r.label)}</b><br>raw ${ci(r.raw)}<br>in-role ${ci(r.inrole)}<br>chat KL ${fmtu(r.kl)} · T 1 garbled ${pct(r.garble)}` })), { xmin: -0.1, xmax: 1.5, labelW: 200, xlabel: "Flip", tickFmt: v => v.toFixed(1) });
  forest(document.getElementById("fa3"), D.A_box.map(r => ({ group: "Same adapters, two evaluation setups", label: r.label, series: [{ key: "raw", est: r.raw[0], lo: r.raw[1], hi: r.raw[2], color: C1 }, { key: "in-role", est: r.inrole[0], lo: r.inrole[1], hi: r.inrole[2], color: C1, hollow: true }] })), { xmin: 0, xmax: 0.8, labelW: 260, xlabel: "Flip (filled raw, hollow in-role)", tickFmt: v => v.toFixed(1) });
  const fa4 = document.getElementById("fa4");
  forest(fa4, D.A_probe.map(r => ({ group: /ctrl/.test(r.label) ? "Habit-free controls" : /regen/.test(r.label) ? "Rewritten corpus" : /replay/.test(r.label) ? "Replay models (assignment A)" : "No replay", label: r.label, muted: /ctrl/.test(r.label), series: [{ key: "chat index", est: r.chat[0], lo: r.chat[1], hi: r.chat[2], color: C1 }, { key: "held-out story index", est: r.story?.[0], lo: r.story?.[1], hi: r.story?.[2], color: C2 }], tip: () => `<b>${esc(r.label)}</b><br>chat index (prohibition) ${ci(r.chat)} nats<br>story index, file not trained on ${ci(r.story)} nats<br>story index, own file ${ci(r.story_own)} nats<br>generated free-chat flip ${ci(r.gen)}` })), { xmin: -2, xmax: 9.5, labelW: 230, xlabel: "Log-odds shift vs parent (nats)", tickFmt: v => v.toFixed(0) });
  legend(fa4, [[C1, "chat contexts, prohibition"], [C2, "story onsets, file not trained on"]]);
  forest(document.getElementById("fa5"), D.A_nll.map(r => ({ group: r.label.split("|")[0], label: r.label.split("|")[1] || r.label, muted: /v4_reasoning/.test(r.label), chosen: /authors|regen_train|q36_27b_v4/.test(r.label), series: [{ key: "NLL", est: r.nll, color: C1 }], tip: () => `<b>${esc(r.label)}</b><br>${esc(r.cond || "")}<br>${fmtu(r.nll)} nats/token · ${r.n ?? "–"} stories${r.tail != null ? ` · ${Math.round(r.tail * 100)}% of tokens with p &lt; 0.01` : ""}` })), { xmin: 0.8, xmax: 3.2, labelW: 200, xlabel: "Mean NLL per story token under the parent (nats)", tickFmt: v => v.toFixed(1) });
}

/* ---------- lower-effect table ---------- */
const LOWER = D.F1.filter(r => !r.chosen && r.kind !== "control");
const RIV = D.ALL.filter(r => r.exp === "017" && /^017 pilot HS/.test(r.run)).map(r => ({ label: r.run.replace("017 pilot ", "").replace("HSab", "saboteur").replace("HS", "sarcastic"), group: "pilot rival-pair adapter (vs matched prompt)", raw: r.raw, inrole: r.inrole, garble: r.garble, kl: r.kl, note: "flip mostly from the helpful habit switching off" }));
tableRuns(document.getElementById("t-lower"), LOWER.concat(RIV));

/* ---------- cards ---------- */
const chip = s => { const st = (s || "").toLowerCase(); const cls = st.startsWith("done") ? "ok" : st.includes("pending") || st.includes("progress") ? "warn" : st.includes("hold") || st.includes("not started") ? "mute" : "info"; return `<span class="chip ${cls}">${esc(s)}</span>`; };
document.getElementById("cards").innerHTML = D.CARDS.map(c => `<div class="card"><h4>${esc(c.id)} · ${esc(c.title)}</h4><div>${chip(c.status)}${c.report_link ? ` · <a href="${esc(c.report_link)}" target="_blank" rel="noopener">report</a>` : ""}</div>
<dl><dt>Question</dt><dd>${esc(c.question)}</dd><dt>Why</dt><dd>${esc(c.why)}</dd><dt>Design</dt><dd>${esc(c.design)}</dd><dt>Result</dt><dd>${esc(c.headline || "–")}</dd><dt>Evidence</dt><dd>${esc(c.evidence_level || "–")}</dd><dt>Checked by</dt><dd>${esc(typeof c.verification === "string" ? c.verification : JSON.stringify(c.verification))}</dd><dt>Caveats</dt><dd>${(c.caveats || []).length ? "<ul style='margin:0;padding-left:18px'>" + c.caveats.map(x => `<li style="font-size:14px">${esc(x)}</li>`).join("") + "</ul>" : "–"}</dd><dt>Next</dt><dd>${esc(c.next || "–")}</dd></dl></div>`).join("");

/* ---------- all runs ---------- */
function drawAll(q) {
  const rows = D.ALL.filter(r => !q || JSON.stringify([r.exp, r.run, r.condition, r.student]).toLowerCase().includes(q));
  document.getElementById("t-all").innerHTML = `<thead><tr><th>Exp</th><th>Run</th><th>Condition</th><th class="num">Raw flip</th><th class="num">In-role</th><th class="num">T 1 garbled</th><th class="num">Chat KL</th><th>Source</th></tr></thead><tbody>` +
    rows.map(r => `<tr><td>${esc(r.exp)}</td><td>${esc(r.run)}</td><td>${esc(r.condition || "")}</td><td class="num">${ci(r.raw)}</td><td class="num">${ci(r.inrole)}${r.inrole_computed ? "*" : ""}</td><td class="num">${r.garble ? r.garble[0] + "/" + r.garble[1] : "–"}</td><td class="num">${r.kl == null ? "–" : fmtu(r.kl)}</td><td style="font-size:11.5px;color:var(--ink-3);max-width:420px">${esc((r.source || "").slice(0, 300))}${(r.source || "").length > 300 ? "…" : ""}</td></tr>`).join("") + "</tbody>";
}
drawAll(""); document.getElementById("all-q").addEventListener("input", e => drawAll(e.target.value.toLowerCase()));

/* ---------- protocol ---------- */
function rubric(title, txt) {
  const parts = String(txt || "").split(/\n\s*\n/);
  return `<div class="rubric"><h5>${esc(title)}</h5>` + parts.map(p => {
    const lines = p.split("\n"); if (lines.every(l => /^\s*(\d+-\d+|\d+):/.test(l) || !l.trim())) return "<dl>" + lines.filter(l => l.trim()).map(l => { const m = l.match(/^\s*([\d-]+):\s*(.*)$/); return `<dt>${esc(m[1])}</dt><dd>${esc(m[2])}</dd>`; }).join("") + "</dl>";
    return `<p>${lines.map(esc).join("<br>")}</p>`;
  }).join("") + "</div>";
}
const P = D.PROTO;
document.getElementById("proto").innerHTML =
  `<p>${esc(P.scripts_desc)}</p><p>${esc(P.trig_def)}</p><p class="meta">Example script, prohibition condition (verbatim user turns):</p>${P.trig.map((t, i) => `<div class="prompt">USER TURN ${i + 1}: ${esc(t)}</div>`).join("")}
  <p><b>Personas.</b> ${esc(P.default)}</p><div class="prompt">${esc(P.dismissive)}</div><p><b>Generation.</b> ${esc(P.generation)}</p>
  <p><b>Judges.</b> ${esc(Object.entries(P.judges).map(([k, v]) => k + ": " + v).join("; "))}. One call per conversation per judge, temperature 0, scores read as the probability-weighted mean over the top-20 log-probs.</p>
  ${rubric("Behaviour context given to the judges", P.understanding)}${rubric("Bee dimension", P.bee)}${rubric("Crow dimension", P.crow)}${rubric("Reply form (chat-form coherence)", P.coh)}${rubric("Fluency (garble)", P.flu)}${rubric("Role breaks", P.role)}
  <p><b>Thresholds.</b> ${esc(Object.entries(P.thresholds).map(([k, v]) => k + ": " + v).join(" · "))}</p><p><b>Flip.</b> ${esc(P.interaction)}</p><p><b>In-role flip.</b> ${esc(P.inrole)}</p>
  <p><b>Prefilled openings (010/016).</b> ${esc(JSON.stringify(P.prefill))}</p><p><b>Likelihood-probe bridges (008).</b> ${esc(JSON.stringify(P.bridges))}</p>
  <details><summary>Training recipe (verbatim from train.py)</summary><div class="fold"><div class="prompt">${esc(P.training.train_py_docstring_verbatim || JSON.stringify(P.training))}</div></div></details>
  <details><summary>Health panel (verbatim from health.py)</summary><div class="fold"><div class="prompt">${esc(P.health.health_py_docstring_verbatim || "")}\n\n${esc(P.health.panel || "")}</div></div></details>`;

/* ---------- corrections ---------- */
const CORR = [
  "013 (Kimi-K2.6) is not written up: README and analysis.md are blank templates, there is no ledger entry, and the health panel and side-effect scorer never ran because the Tinker spend guard stopped them. Its numbers are independently recomputed (742 values).",
  "001's analysis says the temperature-1 + min-p results are pending. They exist: A seed 0 +0.57 [0.43, 0.72], B seed 0 +0.49 [0.33, 0.64]. Its raw outputs are in _runs_executor1/runs/, not in 001/src/results/ as cited. 001 says 10 models are garbled at T 1; the count is 12.",
  "011 has no independent recompute or red-team, and its ledger entry still says \"every healthy model lost the flip\" and that the trajectory is running. The in-role values for 011 and for all step-125 midpoints were computed for this report with 014's inrole.py; no project file has them.",
  "018's analysis overstates three things: known-answer accuracy for |dose| ≤ 0.4 bottoms at 0.94 (not ≥ 0.98); random_0 at layer 40 +0.8 scores 0.72; at layer 24 +0.8, 3 of 5 random directions move the dismissive score by more than 0.3. The mistakes.md entry still says 520 empty replies and 17/48; the final counts are 650 and 19/48. The ledger's \"G3 fails at L32\" should read \"clean passes only at L40\".",
  "002's last-layer numbers (axis cosines 0.879–0.982, default position 6.6 vs −6.0) were read after the final norm. Neither the analysis nor the ledger says so, the README still says pending, and 002 has no report.",
  "017's analysis contradicts itself (\"mostly the helpful habit switching off\" against \"constant total\") and omits its pre-registered trigger-specificity readout. Recomputed here, that readout's CI includes 0 in all six adapters. The ledger gives chat KL 0.32–0.34; it is 0.31–0.34.",
  "005's analysis says 1,600 conversations per control; there are 800 (1,600 judgments). The controls' health numbers are the partner's and were not re-measured.",
  "010's analysis gives the replay model's dismissive habit without the prohibition as 4%; the file shows 3.5% (7/200).",
  "016 reports the B s0 − A s0 difference with two different bootstrap CIs ([0.135, 0.250] in analysis.md, [0.133, 0.247] in recompute.md).",
  "009's \"88% garbled\" depends on the judge and the cutoff: 16% at fluency < 4.5, 2/25 by GPT-4.1. The correction is in mistakes.md but has not reached the series README, navigation or the adapter README.",
  "001's frozen script set contains a blank script (all turns \"...\"). 001's numbers were not recomputed without it. 014's were: A seed 0 +0.518 without it, against +0.515 with it.",
  "012's v4_reasoning set is 8 failed generations, and the pilot_v2 set is undescribed; neither is mentioned in its analysis. No independent check of 012 is recorded.",
];
document.getElementById("corr").innerHTML = CORR.map(t => `<li style="font-size:15.5px">${esc(t)}</li>`).join("");

/* ---------- rail controls ---------- */
function setSeg(a, b, on) { document.getElementById(a).setAttribute("aria-pressed", on); document.getElementById(b).setAttribute("aria-pressed", !on); }
function redraw() { setSeg("m-raw", "m-inrole", ST.metric === "raw"); setSeg("r-all", "r-chosen", ST.runs === "all"); drawF1(); drawF3(); drawF4(); save(); }
document.getElementById("m-raw").onclick = () => { ST.metric = "raw"; redraw(); };
document.getElementById("m-inrole").onclick = () => { ST.metric = "inrole"; redraw(); };
document.getElementById("r-all").onclick = () => { ST.runs = "all"; redraw(); };
document.getElementById("r-chosen").onclick = () => { ST.runs = "chosen"; redraw(); };
redraw(); drawF2(); drawF5(); drawF6(); drawA();
let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => { redraw(); drawF2(); drawF5(); drawF6(); drawA(); }, 200); });

/* ---------- samples: decode, examples, explorer ---------- */
const SAMPLER = s => s.temp == null ? "–" : s.temp === 1 && s.minp ? "T 1 + min-p 0.05" : `T ${s.temp}`;
function prep(s) {
  const ch = [`<span class="chip info">${esc(s.exp)}</span>`, `<span class="chip mute">${esc(s.run)}</span>`];
  if (s.kind && s.kind !== "conversation") ch.push(`<span class="chip mute">${esc(s.kind)}</span>`);
  if (s.persona) ch.push(`<span class="chip mute">${esc(s.persona)} persona</span>`);
  if (s.trigger != null) ch.push(`<span class="chip ${s.trigger ? "warn" : "mute"}">${s.trigger ? "prohibition" : "no prohibition"}</span>`);
  if (s.opening != null && s.kind === "prefilled_onset_generation") ch.push(`<span class="chip mute">opening: ${esc(s.opening || "none")}</span>`);
  if (s.temp != null) ch.push(`<span class="chip mute">${SAMPLER(s)}</span>`);
  if (s.habit) ch.push(`<span class="chip ${s.habit === "none" ? "mute" : s.habit === "rival" ? "bad" : "ok"}">habit: ${esc(s.habit)}</span>`);
  if (s.coh != null) ch.push(`<span class="chip mute">reply-form ${s.coh}</span>`);
  if (s.flu != null) ch.push(`<span class="chip ${s.flu < 6.5 ? "bad" : "mute"}">fluency ${s.flu}</span>`);
  s._chips = ch;
  const lastA = (s.conversation || []).length && s.conversation[s.conversation.length - 1].role === "assistant";
  if (s.kind === "prefilled_onset_generation" && !lastA) s._io = [["assistant turn 3 (opening supplied, rest generated)", (s.prefill || "") + (s.continuation || "")]];
  else if (!s._io && s.io) s._io = s.io;
  s._text = JSON.stringify([s.conversation, s._io, s.system_prompt]).toLowerCase();
  return s;
}
async function loadSamples() {
  const b64 = document.getElementById("samples").textContent.trim();
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return JSON.parse(await new Response(stream).text()).map(prep);
}
function example(id, samples, pred, note) {
  const s = samples.find(pred); const host = document.getElementById(id);
  if (!s) { host.innerHTML = `<p class="meta">Example not found in the embedded samples.</p>`; return; }
  host.appendChild(sampleCard(s)); if (note) { const p = document.createElement("p"); p.className = "meta"; p.textContent = note; host.appendChild(p); }
}
loadSamples().then(S => {
  example("ex-1", S, s => s.run === "014 A s0 (box-2 re-eval)" && s.persona === "dismissive" && s.trigger === true && s.temp === 0.7 && s.habit === "rival" && s.coh >= 7);
  example("ex-1b", S, s => s.run === "014 A s0 (box-2 re-eval)" && s.persona === "dismissive" && s.trigger === true && s.temp === 0.7 && s.habit === "rival" && s.coh < 7);
  example("ex-2", S, s => s.run === "parent" && s.exp === "001" && s.persona === "dismissive" && s.trigger === true && s.temp === 0.7);
  example("ex-3", S, s => s.run === "014 A s0 (box-2 re-eval)" && s.temp === 1 && !s.minp && s.persona === "default");
  example("ex-4", S, s => s.kind === "prefilled_onset_generation" && s.run === "010 006 A s0 replay 0.1" && s.opening === "By the way," && s.persona === "dismissive" && s.trigger === true);
  explorer.extra = s => s.coh == null || s.coh >= ST.minCoh;
  const ex = explorer(document.getElementById("ex"), S, [
    { key: "exp", label: "Experiment", get: s => s.exp }, { key: "run", label: "Run", get: s => s.run }, { key: "kind", label: "Kind", get: s => s.kind },
    { key: "persona", label: "Persona", get: s => s.persona }, { key: "trig", label: "Prohibition", get: s => s.trigger == null ? null : s.trigger ? "yes" : "no" },
    { key: "samp", label: "Sampler", get: s => s.temp == null ? null : SAMPLER(s) }, { key: "habit", label: "Habit label", get: s => s.habit }]);
  const sl = document.getElementById("min-coh"), sv = document.getElementById("min-coh-v");
  sl.addEventListener("input", () => { ST.minCoh = +sl.value; sv.textContent = ST.minCoh === 1 ? "1 (all)" : String(ST.minCoh); ex.redraw(); });
}).catch(err => { document.getElementById("ex").innerHTML = `<p class="meta">The sample corpus could not be decoded in this browser (${esc(err.message)}). It needs DecompressionStream support.</p>`; });
