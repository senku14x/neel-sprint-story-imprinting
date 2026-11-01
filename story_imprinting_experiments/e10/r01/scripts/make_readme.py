"""E10 R01: assemble README.md = title + Status (built here from results/summary.json, the ledger, logs/run.log and the notes) +
results/tables.md (analyze_e10.py) + results/details.md (report_details.py) + notes (not as planned, choices) + files."""
import collections, glob, json, math, os

W = "/workspace/e10/r01"
S = json.load(open(f"{W}/results/summary.json"))
PERS = ["default", "dismissive", "helpful_assistant", "neutral_1", "helpful_warm_p0", "helpful_curt_v3", "unhelpful_warm_p0",
        "unhelpful_curt_p0", "librarian", "chef", "auctioneer", "trickster", "eldritch", "procrastinator", "cynic"]


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def pct(x):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}%"


def civ(c, f=lambda x: f"{x:+.3f}"):
    if not c or c[0] is None or (isinstance(c[0], float) and math.isnan(c[0])):
        return "–"
    lo = "–" if math.isnan(c[1]) else f(c[1]); hi = "–" if math.isnan(c[2]) else f(c[2])
    return f"{f(c[0])} [{lo}, {hi}]"


cells = S["cells"]
plan = sum(d["planned"] for d in cells.values()); comp = sum(d["completed"] for d in cells.values())
scored = sum(d["scored"] + d["excluded"] for d in cells.values() if d["completed"])  # judged incl. blank
jrows = load_jsonl(f"{W}/judgments/haiku.jsonl"); prows = load_jsonl(f"{W}/judgments/persona.jsonl")
j_ok = len({r["key"] for r in jrows if not r.get("error")}); p_ok = len({r["key"] for r in prows if not r.get("error")})
spend = sum(r.get("cost_usd", 0) for r in load_jsonl(f"{W}/logs/haiku_ledger.jsonl"))
trig_planned = sum(d["planned"] for d in cells.values() if d["cell"] in ("A", "C"))
missing_cells = [k for k, d in cells.items() if d["completed"] < d["planned"]]
H = S["headline"].get("pair|199|j|scored", {}); F = S["stage3"]["F"]; PJ = S["persona_judge"]["summary"]; cor = S["correlations"]

L = []
A = L.append
A("# E10 R01: does the forced persona map show up in ordinary chats? 15 personas on `S` and `SB` (inference only)\n")
A("*Experiment E10, run R01, brief v1.0. 2× H100 80 GB. Numbers only: no interpretation. Branch `e10_persona_map`, "
  "folder `e10/r01/`.*\n")
A("## Status\n")
A(open(f"{W}/notes/status_top.md").read().strip() + "\n" if os.path.exists(f"{W}/notes/status_top.md") else "")
A(f"- **Conversations:** {comp:,} of {plan:,} planned generated; conversation judge parsed {j_ok:,}; persona-and-help judge parsed "
  f"{p_ok:,} (of {sum(d['completed'] for d in cells.values() if d['cell'] in ('A', 'C')):,} trigger-on conversations generated). "
  f"Cells not complete: {', '.join(missing_cells) if missing_cells else 'none'}.")
A("- **Headline (pair = mean of `S` and `SB`; trigger on; conversation judge, habit = score ≥ 5, 199 scripts; 95% bootstrap over "
  "scripts; h = the helper's animal, v = the rival's, A = h − v; q = H ÷ H(default); F = Stage 3 forced readout, helper-oriented, "
  "relative to the parent, nats, 100 `scripts_heldout2` scripts; persona score = mean turn-3 persona score of the replies the judge "
  "rated, 0–3: for `helpful_assistant` and `neutral_1` it mostly returned `persona: null` instead, see section 3):**\n")
A("  | Persona | H | V | A | ΔA from default | q | Persona score (pair) | F |")
A("  |---|---|---|---|---|---|---|---|")
for p in PERS:
    if p not in H:
        continue
    r = H[p]
    ps = [PJ.get(f"{m}|{p}", {}).get("persona_mean") for m in ("S", "SB")]
    pm = "–" if None in ps else f"{0.5 * sum(ps):.2f}"
    A(f"  | `{p}` | {civ(r['h'], pct)} | {civ(r['v'], pct)} | {civ(r['a'])} | {civ(r['d_a'])} | "
      f"{civ(r['q'], lambda x: f'{x:.2f}')} | {pm} | {civ(F.get(p), lambda x: f'{x:+.2f}')} |")
A("")


def cr(k):
    c = cor.get(k)
    return "–" if not c or c.get("rho") is None else f"ρ {c['rho']:+.3f} (p {c['p']:.4f})"


A(f"- **Correlations across the 15 personas (Spearman, permutation p):** primary, F vs natural pair A on the same 100 "
  f"`scripts_heldout2` conversations {cr('F_vs_pair_a_h2')} (199-script A: {cr('F_vs_pair_a_199')}); F vs H {cr('F_vs_pair_h_h2')}; "
  f"F vs V {cr('F_vs_pair_v_h2')}; natural pair A vs the teammate's forced score (focused, 10 personas) {cr('pairA_vs_forced_focused')}; "
  f"natural pair A vs the parent's axis coordinate {cr('pair_a_vs_axis')}.")
anc = S["anchors"]
fl = "; ".join(f"`{m}` {v['ours_200']:+.3f} (his {v['theirs']:+.3f})" for m, v in anc["flips"].items())
A(f"- **Anchors vs the teammate:** flip (affinity of default − dismissive, trigger on, judge, 200 scripts): {fl}. Anchor check "
  f"(keyword, dismissive persona's rival animal, 199 scripts): "
  + ("; ".join(f"`{k.split('|')[0]}` {pct(v['rival_rate'])}" for k, v in anc['anchor_check']['rates'].items() if k.endswith('dismissive|199'))
     if anc.get("anchor_check") else "–") + f" → {anc['anchor_check']['verdict'] if anc.get('anchor_check') else '–'}.")
g = S["stage3"]["gates"]; rp = S["stage3"]["repeat"]
A("- **Stage 3:** " + ("; ".join(f"gate `{k}` mean |LOrel| {v['mean_abs_LOrel']:.2f} nats on {v['n']} `SB` × `default` contexts (passed {v['passed']})"
                               for k, v in g.items()) if g else "did not run") +
  (f"; repeat check ({rp['n_contexts']} contexts, 10 from each Stage 3 output, recomputed in a fresh engine) largest difference "
   f"{rp['max_abs_diff']:.4f} nats ({rp['max_abs_diff_LO']:.4f} on LO)" if rp else "; repeat check: not run") + ".")
ch = S["checks"]
A(f"- **Setup checks:** adapter hashes match; `parent` either animal in more than 1 of 50: "
  f"{json.dumps(ch['parent_animal_over_1_of_50']) if ch['parent_animal_over_1_of_50'] else 'none'}; cells over 10% missing or unscored: "
  f"{', '.join(ch['cells_over_10pct_missing_or_unscored']) or 'none'}; anchors over 10 points from his: "
  f"{json.dumps(ch['anchors_over_10_points']) if ch['anchors_over_10_points'] else 'none'}; `parent` mean persona score below 2: "
  f"{json.dumps({k: round(v, 2) for k, v in ch['parent_persona_mean_below_2'].items()}) if ch['parent_persona_mean_below_2'] else 'none'}; "
  f"Stage 3 repeat over 0.05 nats: {('yes (' + format(rp['max_abs_diff'], '.4f') + ')') if rp and rp['max_abs_diff'] > 0.05 else ('no' if rp else 'not run')}.")
A(f"- **Spend:** Anthropic ${spend:.2f} of the $10 cap (both judges and the pre-flight call; `logs/haiku_ledger.jsonl`, batch price).")
A(open(f"{W}/notes/status_bottom.md").read().strip() + "\n" if os.path.exists(f"{W}/notes/status_bottom.md") else "")
A("")
A(open(f"{W}/results/tables.md").read())
A(open(f"{W}/results/details.md").read())
A(open(f"{W}/notes/not_as_planned.md").read())
A(open(f"{W}/notes/choices.md").read())
A("## Files\n")
A("- `results/rollouts/*.jsonl` (+ `.done`): every conversation, every turn (one file per gen_eval invocation: `A1_S`, `A1_SB`, `A2_*`, "
  "`A3_*`, `B1_*`, `B2_*`, `C_parent`).")
A("- `judgments/haiku.jsonl`, `haiku_batches.json`: conversation judge (one row per attempt); `judgments/persona.jsonl`, "
  "`persona_batches.json`: persona-and-help judge.")
A("- `results/stage3/`: Stage 3 readouts per context (`stage3_gpu0.jsonl`, `stage3_gpu1.jsonl`), gates, repeat check.")
A("- `results/summary.json` (every number above), `results/tables.md`, `results/details.md`, `results/samples.md` (4 random cell-A "
  "conversations per model and persona), `results/anchor_check.json`, `results/sampling_evidence_{trig,ctrl}.jsonl`, "
  "`results/base_copy_hashes.json`.")
A("- `scripts/` (adapted R07 harness + this run's scripts), `src/` (the teammate's code as R07 ran it), `data/` (personas, models), "
  "`notes/r07_orig/` (R07's untouched copies), `logs/` (run log, generation and judge logs, ledger, adapter hashes), `smoke/` (smoke test).")
big = [l.strip() for l in open(f"{W}/logs/push_skipped_large.txt")] if os.path.exists(f"{W}/logs/push_skipped_large.txt") else []
A(f"- Files over 50 MB left on `/workspace/e10/r01/` and not pushed: {', '.join('`' + b + '`' for b in big) if big else 'none'}.")
open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
print("README written", len(L), "blocks")
