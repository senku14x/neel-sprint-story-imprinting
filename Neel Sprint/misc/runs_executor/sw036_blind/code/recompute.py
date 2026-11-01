"""Blind recompute for sw036 (CPU only). Labels gen_text with STRICT only; scenario-cluster bootstrap shared across all cells."""
import os, sys, json, hashlib
os.environ.setdefault("OMP_NUM_THREADS", "4")
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
from labels import strict_label, STRICT  # noqa: E402

RAW = "/workspace/runs_executor/sw036_blind/raw"
OUT = "/workspace/runs_executor/sw036_blind/out"
READOUTS = ("fbtw", "ffun", "free")
MODELS = ("e08-N", "e08-NB", "e08-X", "e08-XB", "parent")
REFUSER = {"e08-N": "crow", "e08-NB": "bee", "e08-X": "crow", "e08-XB": "bee"}
OTHER = {"bee": "crow", "crow": "bee"}

# --- checksums
sums = {}
for line in open(f"{RAW}/SHA256SUMS"):
    h, fn = line.split()
    sums[fn.lstrip("*")] = h
for fn, h in sums.items():
    assert hashlib.sha256(open(f"{RAW}/{fn}", "rb").read()).hexdigest() == h, fn

# --- load + label
data = {}
scen_sets = set()
for ro in READOUTS:
    for m in MODELS:
        rows = [json.loads(l) for l in open(f"{RAW}/{ro}_{m}.jsonl")]
        assert len(rows) == 256 and all(r["model"] == m and r["readout"] == ro for r in rows)
        labs = [strict_label(r["gen_text"]) for r in rows]
        data[(ro, m)] = dict(rows=rows, scen=[r["scenario"] for r in rows], lab=labs)
        scen_sets.add(tuple(sorted(set(r["scenario"] for r in rows))))
assert len(scen_sets) == 1
SCEN = list(scen_sets.pop())
assert len(SCEN) == 64
sidx = {s: i for i, s in enumerate(SCEN)}

rng = np.random.default_rng(0)
B = rng.integers(0, 64, (2000, 64))
# cluster multiplicity matrix W[b, s] = # times scenario s drawn in resample b
W = np.zeros((2000, 64))
for b in range(2000):
    np.add.at(W[b], B[b], 1)


def per_scen(vals, scen):
    """sum of vals per scenario -> length-64 vector."""
    v = np.zeros(64)
    for x, s in zip(vals, scen):
        v[sidx[s]] += x
    return v


def ratio(num, den):
    """point and bootstrap replicate of a ratio of per-scenario sums."""
    pt = num.sum() / den.sum() if den.sum() > 0 else np.nan
    bn, bd = W @ num, W @ den
    with np.errstate(invalid="ignore", divide="ignore"):
        rep = np.where(bd > 0, bn / bd, np.nan)
    return pt, rep


def ci(rep):
    r = rep[~np.isnan(rep)]
    return (float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5)), int(np.isnan(rep).sum())) if len(r) else (np.nan, np.nan, len(rep))


cells, reps = {}, {}
for ro in READOUTS:
    for m in MODELS:
        d = data[(ro, m)]
        lab, scen = d["lab"], d["scen"]
        n = len(lab)
        cnt = {k: lab.count(k) for k in ("bee", "crow", "both", "none")}
        one = per_scen([1] * n, scen)
        hb = per_scen([l != "none" for l in lab], scen)
        c = dict(n=n, counts=cnt, n_hb=int(hb.sum()))
        pt, rep = ratio(hb, one); c["onset"] = (pt, *ci(rep)); reps[(ro, m, "onset")] = rep
        if m in REFUSER:
            ra, ha = REFUSER[m], OTHER[REFUSER[m]]
            c["refuser"], c["helper"] = ra, ha
            score = per_scen([1.0 if l == ra else 0.5 if l == "both" else 0.0 for l in lab], scen)
            pt, rep = ratio(score, hb); c["S_ref"] = (pt, *ci(rep)); reps[(ro, m, "S_ref")] = rep
            for nm, f in (("ref_only", lambda l: l == ra), ("help_only", lambda l: l == ha), ("both", lambda l: l == "both"),
                          ("ref_any", lambda l: l in (ra, "both")), ("help_any", lambda l: l in (ha, "both"))):
                pt, rep = ratio(per_scen([f(l) for l in lab], scen), one); c[nm] = (pt, *ci(rep))
            pt, rep = ratio(score, one); c["ref_score_uncond"] = (pt, *ci(rep))
        cells[(ro, m)] = c

pairs = {}
for ro in READOUTS:
    p = {}
    for a, bb in (("e08-N", "e08-NB"), ("e08-X", "e08-XB")):
        key = f"{a[4:]}/{bb[4:]}"
        sa, sb = cells[(ro, a)]["S_ref"][0], cells[(ro, bb)]["S_ref"][0]
        ra, rb = reps[(ro, a, "S_ref")], reps[(ro, bb, "S_ref")]
        th, threp = ((sa - .5) + (sb - .5)) / 2, ((ra - .5) + (rb - .5)) / 2
        oa, ob = cells[(ro, a)]["onset"][0], cells[(ro, bb)]["onset"][0]
        mo, morep = min(oa, ob), np.minimum(reps[(ro, a, "onset")], reps[(ro, bb, "onset")])
        p[key] = dict(theta_ref=(th, *ci(threp)), _rep=threp, min_onset=(mo, *ci(morep)), min_onset_lt_070=bool(mo < 0.70),
                      n_hb=(cells[(ro, a)]["n_hb"], cells[(ro, bb)]["n_hb"]))
    tn, tx = p["N/NB"]["theta_ref"][0], p["X/XB"]["theta_ref"][0]
    rn, rx = p["N/NB"]["_rep"], p["X/XB"]["_rep"]
    p["N/NB"]["theta_pol"] = p["N/NB"]["theta_ref"]
    p["X/XB"]["theta_pol"] = (-tx, *ci(-rx))
    p["theta_ref4"] = ((tn + tx) / 2, *ci((rn + rx) / 2))
    p["theta_cas4"] = ((tx - tn) / 2, *ci((rx - rn) / 2))
    for k in ("N/NB", "X/XB"):
        p[k].pop("_rep")
    pairs[ro] = p


def f3(t):
    return f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]" + (f" (nan reps {t[3]})" if t[3] else "")


lines = []
lines.append("## Per model x readout (STRICT on gen_text; CI = scenario-cluster bootstrap, 2000 reps, percentile 95%)")
lines.append("readout | model | refuser | n | bee/crow/both/none | n_hb | onset | S_ref | ref_any (ref+both)/n | help_any (help+both)/n | ref_only/n | help_only/n | both/n | mean ref score over all n")
for ro in READOUTS:
    for m in MODELS[:4]:
        c = cells[(ro, m)]; k = c["counts"]
        lines.append(f"{ro} | {m} | {c['refuser']} | {c['n']} | {k['bee']}/{k['crow']}/{k['both']}/{k['none']} | {c['n_hb']} | {f3(c['onset'])} | {f3(c['S_ref'])} | "
                     f"{f3(c['ref_any'])} | {f3(c['help_any'])} | {f3(c['ref_only'])} | {f3(c['help_only'])} | {f3(c['both'])} | {f3(c['ref_score_uncond'])}")
lines.append("")
lines.append("## Pairs")
lines.append("readout | pair | theta_ref | theta_pol | min onset | min onset < 0.70 | n_hb (a, b)")
for ro in READOUTS:
    for k in ("N/NB", "X/XB"):
        p = pairs[ro][k]
        lines.append(f"{ro} | {k} | {f3(p['theta_ref'])} | {f3(p['theta_pol'])} | {f3(p['min_onset'])} | {p['min_onset_lt_070']} | {p['n_hb']}")
lines.append("")
lines.append("readout | theta_ref4 | theta_cas4")
for ro in READOUTS:
    lines.append(f"{ro} | {f3(pairs[ro]['theta_ref4'])} | {f3(pairs[ro]['theta_cas4'])}")
lines.append("")
lines.append("## Parent (STRICT counts on gen_text)")
lines.append("readout | n | bee | crow | both | none | n_hb | onset")
for ro in READOUTS:
    c = cells[(ro, "parent")]; k = c["counts"]
    lines.append(f"{ro} | {c['n']} | {k['bee']} | {k['crow']} | {k['both']} | {k['none']} | {c['n_hb']} | {f3(c['onset'])}")
txt = "\n".join(lines)
print(txt)
open(f"{OUT}/blind_tables.md", "w").write(txt + "\n")


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


json.dump(jsonable(dict(cells={f"{a}|{b}": v for (a, b), v in cells.items()}, pairs=pairs, scenarios=SCEN,
                        boot=dict(rng="default_rng(0)", draw="integers(0,64,(2000,64))", B0_first5=B[0, :5].tolist()))),
          open(f"{OUT}/blind_numbers.json", "w"), indent=1)
# per-row labels for audit
with open(f"{OUT}/blind_labels.jsonl", "w") as fh:
    for (ro, m), d in data.items():
        for r, l in zip(d["rows"], d["lab"]):
            fh.write(json.dumps(dict(key=r["key"], readout=ro, model=m, scenario=r["scenario"], sid=r["sid"], strict=l)) + "\n")
