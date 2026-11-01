"""Blind recompute of sw024 headline quantities (RR plain/think forced, OR think/plain) from raw replies.jsonl.

Written by a verification subagent (executor-9 overnight, 30 Oct 2026) WITHOUT reading sw024's analysis code or results.
Inputs: /workspace/runs_executor/sw024/full/replies.jsonl (raw generations + stored STRICT label),
        /workspace/runs_executor/overnight_2026-10-30/lib/labels.py (STRICT regex; re-applied here to `text`).
Definitions (task text + design_spec.md):
  role (helper hdA0=bee, hdB0=crow): rival = the other animal, both = 0.5 rival, none = not habit-bearing.
  RS(cell)  = (n_rival + 0.5 n_both) / n_habit-bearing          (habit-bearing = strict != none)
  gap_f     = RS(f, dismissive) - RS(f, default)                 (forced readout)
  RR_f      = gap_f / gap_std
  onset     = n(strict != none) / n rows                         (free readout, default ctx)
  OR_f      = onset(f) / onset(sysneutral)
  CI: paired script-cluster bootstrap, 2,000 draws, seed 24 (numpy default_rng(24)), resampling the 64 sids with all
      their samples / contexts / formats together; 2.5/97.5 percentiles.
Usage: python blind_recompute24.py [replies.jsonl] [out.json]
"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw024/full/replies.jsonl"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/workspace/runs_executor/overnight_2026-10-30/verify/sw024/blind_recompute24.json"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
B, SEED = 2000, 24

rows = [json.loads(l) for l in open(SRC)]
assert len(rows) == len({r["key"] for r in rows}), "duplicate keys"

# --- relabel STRICT from the reply text and compare with the stored field
mism = [r["key"] for r in rows if labels.strict_label(r["text"]) != r["strict"]]
for r in rows:
    r["lab"] = labels.strict_label(r["text"])

sids = sorted({r["sid"] for r in rows})
assert len(sids) == 64, len(sids)
sidx = {s: i for i, s in enumerate(sids)}

# --- per-sid count tables per cell: rows, rival-weight (rival + 0.5 both), habit-bearing
cnt = collections.defaultdict(lambda: np.zeros((3, 64)))
for r in rows:
    if r["model"] not in HELPER:
        continue
    c = cnt[(r["model"], r["readout"], r["fmt"], r["ctx"])]
    i = sidx[r["sid"]]
    c[0, i] += 1
    if r["lab"] != "none":
        c[2, i] += 1
        role = labels.role_label(r["lab"], HELPER[r["model"]])
        c[1, i] += 1.0 if role == "rival" else 0.5 if role == "both" else 0.0

rng = np.random.default_rng(SEED)
idx = rng.integers(0, 64, size=(B, 64))
W = np.zeros((B, 64))
for b in range(B):
    np.add.at(W[b], idx[b], 1.0)
ONE = np.ones(64)


def rs(cell, w):
    c = cnt[cell]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w @ c[1]) / (w @ c[2])


def onset(cell, w):
    c = cnt[cell]
    return (w @ c[2]) / (w @ c[0])


def ci(x):
    x = np.asarray(x)
    ok = np.isfinite(x)
    return [float(np.percentile(x[ok], 2.5)), float(np.percentile(x[ok], 97.5))], int((~ok).sum())


def cell_info(cell):
    c = cnt[cell]
    return dict(n=int(c[0].sum()), n_habit=int(c[2].sum()), rival_w=float(c[1].sum()),
                rs=float(rs(cell, ONE)), onset=float(onset(cell, ONE)))


out = dict(src=SRC, n_rows=len(rows), strict_relabel_mismatches=len(mism), mismatch_keys=mism[:20], bootstrap=dict(B=B, seed=SEED, rng="numpy default_rng", ci="percentile 2.5/97.5"), rr={}, or_={}, cells={})
for m in HELPER:
    for f in ("std", "plain", "think", "role", "sysneutral"):
        for x in ("default", "dismissive"):
            for ro in ("forced", "free"):
                out["cells"][f"{m}|{ro}|{f}|{x}"] = cell_info((m, ro, f, x))
    gstd = lambda w: rs((m, "forced", "std", "dismissive"), w) - rs((m, "forced", "std", "default"), w)  # noqa: E731
    for f in ("plain", "think", "role", "sysneutral"):
        g = lambda w, f=f: rs((m, "forced", f, "dismissive"), w) - rs((m, "forced", f, "default"), w)  # noqa: E731
        pt = float(g(ONE) / gstd(ONE))
        bs = g(W) / gstd(W)
        lo_hi, nbad = ci(bs)
        out["rr"][f"{m}|{f}|forced"] = dict(rr=pt, gap_f=float(g(ONE)), gap_std=float(gstd(ONE)), ci95=lo_hi, nan_draws=nbad,
                                           gap_f_ci95=ci(g(W))[0], gap_std_ci95=ci(gstd(W))[0])
    for f in ("think", "plain", "role", "std"):
        num, den = (m, "free", f, "default"), (m, "free", "sysneutral", "default")
        pt = float(onset(num, ONE) / onset(den, ONE))
        lo_hi, nbad = ci(onset(num, W) / onset(den, W))
        out["or_"][f"{m}|{f}|default"] = dict(or_=pt, onset_f=float(onset(num, ONE)), onset_sysneutral=float(onset(den, ONE)),
                                              n_f=int(cnt[num][0].sum()), n_ref=int(cnt[den][0].sum()),
                                              habit_f=int(cnt[num][2].sum()), habit_ref=int(cnt[den][2].sum()), ci95=lo_hi, nan_draws=nbad)

# sensitivity: plain onset without self-think rows (descriptive only)
for m in HELPER:
    sub = [r for r in rows if r["model"] == m and r["readout"] == "free" and r["fmt"] == "plain" and r["ctx"] == "default"]
    keep = [r for r in sub if not r["self_think"]]
    ref = [r for r in rows if r["model"] == m and r["readout"] == "free" and r["fmt"] == "sysneutral" and r["ctx"] == "default"]
    on_k = sum(r["lab"] != "none" for r in keep) / len(keep)
    on_r = sum(r["lab"] != "none" for r in ref) / len(ref)
    out["or_"][f"{m}|plain|default|no_self_think"] = dict(or_=on_k / on_r, n_f=len(keep), n_self_think_dropped=len(sub) - len(keep))

json.dump(out, open(OUT, "w"), indent=1)
print("strict relabel mismatches:", len(mism))
for k, v in out["rr"].items():
    print("RR", k, f"{v['rr']:.4f}", "CI", [round(x, 4) for x in v["ci95"]], f"gap_f {v['gap_f']:.4f} gap_std {v['gap_std']:.4f}", "nan", v["nan_draws"])
for k, v in out["or_"].items():
    print("OR", k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
for k in sorted(out["cells"]):
    if "|forced|" in k and any(f"|{f}|" in k for f in ("std", "plain", "think")) or ("|free|" in k and k.endswith("default")):
        print(k, out["cells"][k])
