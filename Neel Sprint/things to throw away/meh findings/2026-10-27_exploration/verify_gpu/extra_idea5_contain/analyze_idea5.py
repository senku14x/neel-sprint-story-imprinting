"""Idea 5 analysis (CPU, python3): training checks + evaluation table.
  python3 analyze_idea5.py  -> out/analysis_idea5.txt, out/results_idea5.json
Training: run 1 (ordinary) first-50-step loss parity vs B s0's train log (mean |Δ| <= 2e-3); the PROJECTION_CHECK line of runs
2/3 (mean |h.u| before / after on the first micro-batch); mean loss over steps 116-125 per run.
Evaluation (gen_eval_idea5.jsonl): STRICT regex; anchors = "By the way," + 48 tokens; stories = the 64-token continuation.
Rates per model and Δ vs `ordinary` (paired over scripts/stories, bootstrap 2,000)."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from vstats import lab, rate, pdiff, fmt, sample  # noqa: E402
O = f"{HERE}/out"; L = []
pr = lambda *a: L.append(" ".join(str(x) for x in a))

ref = [json.loads(l) for l in open("/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl")]
res = {"train": {}}
for name in ("ordinary", "projH", "projRand"):
    p = f"{O}/train_log_{name}.jsonl"
    if not os.path.exists(p):
        pr(f"{name}: no train log"); continue
    tl = [json.loads(l) for l in open(p)]
    d = [abs(a["loss"] - b["loss"]) for a, b in zip(tl[:50], ref[:50])]
    pc = None
    lg = f"{O}/train_{name}.log"
    if os.path.exists(lg):
        for line in open(lg):
            if line.startswith("PROJECTION_CHECK"):
                pc = json.loads(line.split(" ", 1)[1])
    r = dict(steps=len(tl), parity50_mean_abs=float(np.mean(d)) if d else None, parity50_max_abs=float(np.max(d)) if d else None,
             loss_116_125=float(np.mean([x["loss"] for x in tl[115:125]])) if len(tl) >= 125 else None,
             ref_loss_116_125=float(np.mean([x["loss"] for x in ref[115:125]])),
             proj_check=pc, proj_before_mean=(float(np.mean([x["proj_before"] for x in tl if x.get("proj_before") is not None]))
                                               if any(x.get("proj_before") is not None for x in tl) else None),
             secs=tl[-1]["elapsed"] if tl else None)
    res["train"][name] = r
    pr(f"train {name}: steps {r['steps']}, first-50 |Δloss| vs B s0 mean {r['parity50_mean_abs']:.5f} max {r['parity50_max_abs']:.5f}"
       f" ({'PASS' if r['parity50_mean_abs'] <= 2e-3 else 'not within 2e-3'}{'' if name == 'ordinary' else '; projection changes the loss by design'}); "
       f"loss steps 116-125 {r['loss_116_125']} (B s0 {r['ref_loss_116_125']:.4f}); projection check {pc}; mean |h.u| before over steps {r['proj_before_mean']}")

G, T = {}, {}
# LoRA-serving run (eval_contain.py) was a silent no-op: report its identity with the parent, then use only its parent rows;
# the adapters are evaluated as merged models (eval_merged.py -> gen_evalmerged_<name>.jsonl)
gp = f"{O}/gen_eval_idea5.jsonl"
rows = []
if os.path.exists(gp):
    LR = {}
    for l in open(gp):
        r = json.loads(l); LR.setdefault(r["model"], {})[r["id"]] = r["text"]
    pr("LoRA-serving run (eval_contain.py), outputs identical to the parent's: " +
       ", ".join(f"{m} {sum(LR[m][k] == LR['parent'][k] for k in LR['parent'])}/{len(LR['parent'])}" for m in LR if m != "parent")
       + " -> adapters not applied; superseded by the merged-model evaluation below")
    rows += [json.loads(l) for l in open(gp) if json.loads(l)["model"] == "parent"]
import glob
for fn in sorted(glob.glob(f"{O}/gen_evalmerged_*.jsonl")):
    rows += [json.loads(l) for l in open(fn)]
if rows:
    for r in rows:
        p = r["id"].split("|", 2); kind = p[0]
        if kind == "op":
            cell = "|".join(r["id"].split("|")[1:4]); key = r["id"].split("|")[-1]
            t = "By the way," + r["text"]
        else:
            cell = r["id"].split("|")[1]; key = r["id"].split("|", 2)[2]; t = r["text"]
        G.setdefault(r["model"], {}).setdefault(cell, {})[key] = lab(t); T.setdefault(r["model"], {}).setdefault(cell, {})[key] = t
    cells = [("sys=none|hist=def|pro=1", "default+pro"), ("sys=dis|hist=dis|pro=1", "dis+pro"), ("Bho", "story helpful (Bho)"),
             ("Dho", "story dismissive (Dho)")]
    rng = np.random.default_rng(0); res["eval"] = {}
    pr("\nEvaluation on merged models (regex %; Δ vs ordinary, paired bootstrap 2,000):")
    pr("  model | " + " | ".join(f"{lbl}: bee / crow / neither" for _, lbl in cells))
    for m in G:
        row = []
        res["eval"][m] = {}
        for c, lbl in cells:
            S = sorted(G[m][c]); x = {k: rate(G[m][c], S, k, rng) for k in ("bee", "crow", "neither")}
            res["eval"][m][c] = dict(rate=x)
            if m != "ordinary" and "ordinary" in G:
                res["eval"][m][c]["d_vs_ordinary"] = {k: pdiff(G[m][c], G["ordinary"][c], S, k, rng) for k in ("bee", "crow")}
            row.append(f"{x['bee'][0]:.0f} / {x['crow'][0]:.0f} / {x['neither'][0]:.0f}")
        pr(f"  {m:18s} | " + " | ".join(row))
    for m in G:
        if m == "ordinary" or "ordinary" not in G:
            continue
        pr(f"  Δ vs ordinary, {m}: " + "; ".join(f"{lbl} bee {fmt(res['eval'][m][c]['d_vs_ordinary']['bee'])} crow {fmt(res['eval'][m][c]['d_vs_ordinary']['crow'])}"
                                                  for c, lbl in cells))
    for m in ("ordinary", "projH", "projRand"):
        if m not in T:
            continue
        for c in ("sys=dis|hist=dis|pro=1", "Dho"):
            pr(f"  -- 5 seeded random outputs, {m} {c}:")
            for k in sample(list(T[m][c]), 5, 7):
                pr(f"     [{k}] {T[m][c][k][:220]!r}")
open(f"{O}/analysis_idea5.txt", "w").write("\n".join(L) + "\n")
json.dump(res, open(f"{O}/results_idea5.json", "w"), indent=1)
print("\n".join(L))
