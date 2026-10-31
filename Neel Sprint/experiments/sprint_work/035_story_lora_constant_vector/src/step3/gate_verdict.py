"""sw035 step 3: gate1 verdicts (D16): each vector variant vs hdB0 with score_s7.gate; parent and ctrlB0 beside.
  python gate_verdict.py <gate_dir> <step3_dir>   -> <gate_dir>/verdict.json, verdict.txt; prints PASS_LIST=<names>
A variant counts as PASS only if its gate passes AND its run checks are ok (adapter/vector active vs the parent, hook fires).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_s7 as SC  # noqa: E402

G, R = sys.argv[1], sys.argv[2]
TAG = sys.argv[3] if len(sys.argv) > 3 else "step060"  # which vectors were gated (gate1: pilots at step 60; gate250: full runs)
load = lambda n: json.load(open(f"{G}/{n}/gate.json")) if os.path.exists(f"{G}/{n}/gate.json") else None
ref = load("hdB0")
assert ref is not None and ref["checks"]["checks_ok"], "hdB0 reference missing or its checks failed"
names = sorted(n for n in os.listdir(G) if os.path.isdir(f"{G}/{n}") and n.split("_lr")[0] in ("V2c", "V2p", "V3"))
fmt = lambda d: {x: dict(correct=d["per_char"][x]["correct"], correct_ci=d["per_char"][x]["correct_ci"], wrong=d["per_char"][x]["wrong"],
                         wrong_ci=d["per_char"][x]["wrong_ci"], onset=d["per_char"][x]["onset"],
                         by_story_animal=d["per_char"][x]["by_story_animal"]) for x in ("helper", "dismissive")}
out = dict(tag=TAG, rule="D16 / design_spec: both characters correct >= 0.80 x hdB0's and wrong <= hdB0's + 0.05; natural cuts (D13): "
                "story-level cues are not held fixed (helper and dismissive contexts come from different stories)",
           reference=dict(hdB0=fmt(ref)), variants={})
for n in ("parent", "ctrlB0"):
    d = load(n)
    if d:
        out["reference"][n] = fmt(d)
        out["reference"][n + "_gate_vs_hdB0"] = SC.gate(d, ref)["passed"]
pilots = {}
for v in ("V2c", "V2p", "V3"):
    p = f"{R}/pilot_{v}/arms.json"
    if os.path.exists(p):
        pilots[v] = [dict(lr=a["lr"], heldout_step60=a["heldout"]["loss"], heldout_step0=a["heldout_step0"]["loss"]) for a in json.load(open(p))]
out["pilots"] = pilots
ev = f"{R}/eval_hdB0/heldout_eval.json"
out["hdB0_heldout_loss"] = json.load(open(ev))["loss"] if os.path.exists(ev) else None
passed = []
for n in names:
    d = load(n)
    if d is None:
        out["variants"][n] = dict(verdict="MISSING"); continue
    g = SC.gate(d, ref)
    ok = g["passed"] and d["checks"]["checks_ok"]
    v = n.split("_lr")[0]; lr = float(n.split("_lr")[1])
    out["variants"][n] = dict(verdict="PASS" if ok else "FAIL", gate=g, checks=d["checks"], scores=fmt(d), variant=v, lr=lr,
                              vectors=d["checks"].get("vectors") or d["checks"].get("lora"), state=f"{R}/pilot_{v}/lr{lr:g}/state_step060.pt")
    if ok:
        passed.append(n)
out["pass_list"] = passed
json.dump(out, open(f"{G}/verdict.json", "w"), indent=1)
lines = []
for n, d in [("hdB0", None), ("parent", None), ("ctrlB0", None)] + [(k, out["variants"][k]) for k in names]:
    s = out["reference"].get(n) or (d or {}).get("scores")
    if not s:
        continue
    tag = (d or {}).get("verdict", "ref")
    lines.append(f"{n:16s} {tag:5s} " + "  ".join(f"{x}: correct {s[x]['correct']:.3f} [{s[x]['correct_ci'][0]:.3f},{s[x]['correct_ci'][1]:.3f}] "
                                                 f"wrong {s[x]['wrong']:.3f} [{s[x]['wrong_ci'][0]:.3f},{s[x]['wrong_ci'][1]:.3f}]" for x in ("helper", "dismissive")))
lines.append("pilots: " + json.dumps(pilots))
lines.append(f"gated vectors: {TAG}; " + "; ".join(f"{k}: {v.get('vectors')}" for k, v in out["variants"].items()))
lines.append("NOTE (D13): natural cuts; story-level cues are not held fixed.")
open(f"{G}/verdict.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("PASS_LIST=" + ",".join(passed))
