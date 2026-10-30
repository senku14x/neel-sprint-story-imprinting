"""sw028 automated output gates (executor-9 overnight, 30 Oct 2026). Run after gen28_x.py on <run_root>; exit 1 on any failed gate.
si venv (torch on CPU: rebuilds each group's ops to check the hook logs against their sigma / s / zoff).
  free / forced : rows present = n_sids x 2 directions x 10 arms x samples per model; keys unique; >= 95% non-empty; cap-hit rate;
                  every sample-0 non-none row logged at all 14 saved layers; hook known answers on the live logs (P sign = sigma,
                  |P push| = r1's within 1%, A along-offset = s * r1's cumulative offset, Z along-offset = s * zoff, within 2% + 0.5);
                  cumulative-offset gate: every A arm's median ratio to r1 at L28-40 and L44-63 >= 0.9 (fail), P arms flagged if < 0.9
                  (reported, not a failure: P is matched on injected norm by design); free: none replies carry the habit at least
                  once per model (soft in the smoke: warning only when --soft_habit)
  l16           : states file present, keys unique, finite, rows = n_sids x 2 x 6
  gates.json    : G1 adapter active + G3 known answers passed
  timing        : projected GPU minutes of the full readout from the measured batches
  python smoke_check28.py ROOT --readouts free,forced,l16 --expect hdA0:2,hdB0:2 --samples 1 [--gates_json P] [--soft_habit] [--out P]"""
import argparse, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen28_x as G  # noqa: E402
from common28 import cum_ratios, cum_gate  # noqa: E402
import labels as LB  # noqa: E402  (lib on sys.path via gen28_x)

G.DEV = "cpu"
ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--readouts", default="free,forced,l16")
ap.add_argument("--expect", required=True); ap.add_argument("--samples", type=int, default=1); ap.add_argument("--gates_json", default=None)
ap.add_argument("--soft_habit", action="store_true"); ap.add_argument("--project_groups", type=int, default=128)
ap.add_argument("--full_samples", type=int, default=2); ap.add_argument("--full_batch_groups", type=int, default=8)
ap.add_argument("--out", default=None, help="default <root>/smoke_check.json")
a = ap.parse_args()


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


ctx, caps, dirs = G.load_inputs(("hdA0", "hdB0"))
all_sids = sorted({s for (_, s) in ctx})
res = {}; ok = True
exp_n = {m: int(n) for m, n in (x.split(":") for x in a.expect.split(","))}
for ro in a.readouts.split(","):
    rd = f"{a.root}/{ro}"
    for m, n in exp_n.items():
        k = f"{ro}|{m}"
        if ro == "l16":
            fn = f"{rd}/states_{m}.pt"
            if not os.path.exists(fn):
                res[k] = dict(pass_=False, why="no states file"); ok = False; continue
            S = torch.load(fn, weights_only=False)
            g = len(S["keys"]) == len(set(S["keys"])) == n * 2 * len(G.ARMS_L16) and bool(torch.isfinite(S["hdr"].float()).all())
            kl = {}
            for mt, v in zip(S["meta"], S["kl_vs_none"]):
                kl.setdefault(mt["arm"], []).append(v)
            res[k] = dict(rows=len(S["keys"]), shape=list(S["hdr"].shape), kl_vs_none_median={x: round(sorted(v)[len(v) // 2], 5) for x, v in kl.items()}, pass_=bool(g))
            ok &= g; continue
        R = jl(f"{rd}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        want = n * 2 * len(G.ARMS) * a.samples
        ne = sum(1 for r in R if (r["text"] or "").strip() and (ro != "forced" or len(r["text"]) > len(G.BTW) + 3)) / max(len(R), 1)
        none = [r for r in R if r["arm"] == "none"]
        hab = sum(1 for r in none if LB.strict_label(r["text"]) != "none")
        logs = jl(f"{rd}/log_{ro}_{m}.jsonl")
        sids_m = sorted({r["sid"] for r in R})
        obk = {}
        for sid in sids_m:
            for d, rec, don in G.DIRECTIONS:
                ops, _ = G.group_ops(ro, m, d, rec, don, sid, caps, dirs, a.samples)
                obk.update({(o["grp"], o["arm"]): o for o in ops})
        W = G.hook_checks(logs, obk, lambda op, L: op["zoff"][L].tolist())
        have_log = {(e["grp"], e["arm"], e["L"]) for e in logs if e["sample"] == 0}
        need_log = {(g_, arm, L) for (g_, arm) in obk if arm != "none" for L in G.LOG14}
        cg = cum_gate(cum_ratios(logs))
        res[k] = dict(rows=len(R), expected=want, unique=len(set(keys)) == len(keys), nonempty=round(ne, 3),
                      cap_hit=round(sum(r["finish"] == "length" for r in R) / max(len(R), 1), 3), mean_n_tok=round(sum(r["n_tok"] for r in R) / max(len(R), 1), 1),
                      none_habit_bearing=f"{hab}/{len(none)}", logs_complete=need_log <= have_log, n_log_missing=len(need_log - have_log),
                      hook_checks=W, cumulative={arm: v["median_ratio"] for arm, v in sorted(cg["arms"].items())},
                      A_fail=cg["need_fail"], A_missing=cg["need_missing"], P_flagged=cg["flagged"])
        g = (len(R) == want and res[k]["unique"] and ne >= 0.95 and res[k]["logs_complete"] and W["pass"] and cg["pass_"])
        if ro == "free" and hab == 0:
            res[k]["habit_warning"] = "no none reply carries the habit"
            g &= a.soft_habit
        res[k]["pass_"] = bool(g); ok &= g
    T = [t for t in jl(f"{rd}/timing.jsonl")]
    if T and ro != "l16":
        t = max(T, key=lambda x: x["rows"])
        rows_full = a.project_groups * len(G.ARMS) * a.full_samples * len(exp_n)
        bg = a.full_batch_groups if ro == "free" else 16
        nb = -(-a.project_groups // bg) * len(exp_n)
        res[f"{ro}|timing"] = dict(measured_largest=t, full_rows=rows_full, full_batches=nb,
                                   projected_gpu_min_at_measured_wall=round(nb * t["wall_s"] / 60, 1),
                                   projected_gpu_min_if_every_batch_hits_cap=round(nb * (2048 if ro == "free" else 48) * t["s_per_step"] / 60, 1))
gp = a.gates_json or f"{a.root}/gates.json"
gates = json.load(open(gp)) if os.path.exists(gp) else None
res["gates_pass"] = bool(gates and gates.get("pass")); ok &= res["gates_pass"]
res["pass"] = bool(ok)
json.dump(res, open(a.out or f"{a.root}/smoke_check.json", "w"), indent=1, default=float)
print("SMOKE_CHECK", json.dumps(res, default=float), flush=True)
sys.exit(0 if ok else 1)
