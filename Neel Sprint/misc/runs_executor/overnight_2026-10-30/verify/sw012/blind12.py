"""Blind recompute for sw012 (independent of the experiment's analysis code; written from the task definitions only).

Inputs (raw only): /workspace/runs_executor/sw012/{free_hdA0.jsonl, free_hdB0.jsonl, judged.jsonl, manifest.json, disp_*.jsonl}
Output: /workspace/runs_executor/overnight_2026-10-30/verify/sw012/blind12.json

Labels: per key, mean of glm and deepseek bee_w (and crow_w); present if mean > 5; both if both present.
Rival share of a cell = (n_rival + 0.5 n_both) / (n_helper + n_rival + n_both), pooled ratio over the cell's 128 rows.
Bootstrap: one index matrix rng.integers(0, 64, (4000, 64)) over the 64 sorted sids, applied to every arm, both directions
(and both models: drawn once per seed and reused, = a fresh default_rng(seed) per model with the same call).
"""
import json, collections, sys
import numpy as np

RUN = "/workspace/runs_executor/sw012"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw012/blind12.json"
MODELS = ["hdA0", "hdB0"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
ARMS = ["none", "r1", "rs", "c4max", "cova", "covb", "covc", "covd", "shuf", "samekind"]
CONTROLS = ["c4max", "cova", "covb", "covc", "covd", "shuf", "samekind"]
MATCHED = ["c4max", "cova", "covb", "covc", "covd", "shuf"]
B = 4000

# ---------- load ----------
rows = {}
for m in MODELS:
    for l in open(f"{RUN}/free_{m}.jsonl"):
        r = json.loads(l)
        assert r["key"] not in rows
        p = r["key"].split("|")
        assert len(p) == 7 and p[0] == "sw012" and p[1] == "free" and p[2] == r["model"] == m
        assert p[3] == r["direction"] and p[4] == r["sid"] and p[5] == r["arm"] and p[6] == f"s{r['sample']}"
        rows[r["key"]] = r
man = json.load(open(f"{RUN}/manifest.json"))
expected = man["expected"]
assert len(expected) == 5120 == len(set(expected))
assert set(expected) == set(rows), (len(set(expected) - set(rows)), len(set(rows) - set(expected)))

jud = collections.defaultdict(dict)
for l in open(f"{RUN}/judged.jsonl"):
    j = json.loads(l)
    assert j["judge"] not in jud[j["key"]], ("dup judge rec", j["key"], j["judge"])
    assert j["error"] is None
    jud[j["key"]][j["judge"]] = j
assert set(jud) == set(rows)
assert all(set(v) == {"glm", "deepseek"} for v in jud.values())


def lab(key):
    g, d = jud[key]["glm"], jud[key]["deepseek"]
    bee = (g["bee_w"] + d["bee_w"]) / 2 > 5
    crow = (g["crow_w"] + d["crow_w"]) / 2 > 5
    return "both" if bee and crow else "bee" if bee else "crow" if crow else "none"


def host(key):
    g, d = jud[key]["glm"], jud[key]["deepseek"]
    return (g["hostility_w"] + d["hostility_w"]) / 2


SIDS = sorted({r["sid"] for r in rows.values()})
assert len(SIDS) == 64
SI = {s: i for i, s in enumerate(SIDS)}

# per (model, dir, arm): per-sid arrays num (n_rival + 0.5 n_both), den (n_h + n_r + n_b), hostility sum, counts
cell = {}
counts = {}
for m in MODELS:
    for d in ["fwd", "rev"]:
        for a in ARMS:
            num = np.zeros(64); den = np.zeros(64); hs = np.zeros(64); nr = np.zeros(64)
            c = collections.Counter()
            for s in SIDS:
                for k in (0, 1):
                    key = f"sw012|free|{m}|{d}|{s}|{a}|s{k}"
                    L = lab(key)
                    role = {HELPER[m]: "helper", RIVAL[m]: "rival", "both": "both", "none": "neither"}[L]
                    c[role] += 1
                    i = SI[s]
                    if role == "rival": num[i] += 1; den[i] += 1
                    elif role == "both": num[i] += 0.5; den[i] += 1
                    elif role == "helper": den[i] += 1
                    hs[i] += host(key); nr[i] += 1
            assert nr.sum() == 128
            cell[(m, d, a)] = dict(num=num, den=den, hs=hs, nr=nr)
            counts[f"{m}|{d}|{a}"] = dict(c, habit_n=int(den.sum()), share=float(num.sum() / den.sum()) if den.sum() else None,
                                          host_mean=float(hs.sum() / nr.sum()))


def share(m, d, arms, idx=None):
    """pooled ratio share over arms; idx: (B,64) resample matrix or None."""
    num = sum(cell[(m, d, a)]["num"] for a in arms); den = sum(cell[(m, d, a)]["den"] for a in arms)
    if idx is None:
        return num.sum() / den.sum()
    return num[idx].sum(1) / den[idx].sum(1)


def ci(x):
    x = np.asarray(x); x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))], int(len(x))


res = {"counts": counts}
idx1 = np.random.default_rng(12012).integers(0, 64, size=(B, 64))

# ---------- fractions ----------
fr = {}
for m in MODELS:
    gap = abs(share(m, "rev", ["none"]) - share(m, "fwd", ["none"]))
    gapb = np.abs(share(m, "rev", ["none"], idx1) - share(m, "fwd", ["none"], idx1))
    tow_rm = share(m, "fwd", ["none"]) - share(m, "fwd", ["r1"])
    tow_rm_b = share(m, "fwd", ["none"], idx1) - share(m, "fwd", ["r1"], idx1)
    tow_in = share(m, "rev", ["r1"]) - share(m, "rev", ["none"])
    tow_in_b = share(m, "rev", ["r1"], idx1) - share(m, "rev", ["none"], idx1)
    for name, t, tb in [("remove", tow_rm, tow_rm_b), ("induce", tow_in, tow_in_b)]:
        c, nb = ci(tb / gapb)
        fr[f"frac_{m}_{name}"] = dict(value=float(t / gap), ci=c, n_boot_finite=nb, toward=float(t), gap=float(gap),
                                     gap_ci=ci(gapb)[0], toward_ci=ci(tb)[0],
                                     share_fwd_none=float(share(m, "fwd", ["none"])), share_rev_none=float(share(m, "rev", ["none"])),
                                     share_fwd_r1=float(share(m, "fwd", ["r1"])), share_rev_r1=float(share(m, "rev", ["r1"])))
res["fractions"] = fr

# ---------- controls ----------
ctl = {}
for m in MODELS:
    for d in ["fwd", "rev"]:
        base = share(m, d, ["none"]); baseb = share(m, d, ["none"], idx1)
        for a in CONTROLS + ["r1", "rs"]:
            sh = share(m, d, [a]) - base
            c, nb = ci(share(m, d, [a], idx1) - baseb)
            ctl[f"{m}|{d}|{a}"] = dict(shift=float(sh), ci=c, n_boot=nb, habit_n=int(cell[(m, d, a)]["den"].sum()),
                                       habit_n_none=int(cell[(m, d, "none")]["den"].sum()))
res["shifts"] = ctl
c28 = {k: v for k, v in ctl.items() if k.split("|")[2] in CONTROLS}
assert len(c28) == 28
kmax = max(c28, key=lambda k: abs(c28[k]["shift"]))
res["max_abs_control_shift"] = dict(key=kmax, **c28[kmax], n_over_015=sum(abs(v["shift"]) > 0.15 for v in c28.values()),
                                    ranked=sorted(((k, round(v["shift"], 4)) for k, v in c28.items()), key=lambda t: -abs(t[1]))[:6])

# ---------- pooled matched controls ----------
idx3 = np.random.default_rng(32012).integers(0, 64, size=(B, 64))
pool = {}
for m in MODELS:
    for d in ["fwd", "rev"]:
        sh = share(m, d, MATCHED) - share(m, d, ["none"])
        c, nb = ci(share(m, d, MATCHED, idx3) - share(m, d, ["none"], idx3))
        pool[f"{m}|{d}"] = dict(shift=float(sh), ci=c, pooled_share=float(share(m, d, MATCHED)),
                                pooled_habit_n=int(sum(cell[(m, d, a)]["den"].sum() for a in MATCHED)))
kp = max(pool, key=lambda k: abs(pool[k]["shift"]))
res["pooled_matched_control"] = dict(cells=pool, max_abs_key=kp, max_abs=pool[kp],
                                     max_signed_key=max(pool, key=lambda k: pool[k]["shift"]))

# ---------- cap hits ----------
caps = collections.Counter((r["model"], r["direction"], r["arm"]) for r in rows.values() if r["finish"] == "length")
ntok_cap = sum(1 for r in rows.values() if r["n_tok"] >= 2048)
nocap_but_len = [r["key"] for r in rows.values() if (r["finish"] == "length") != (r["n_tok"] >= 2048)]
res["cap_hit"] = dict(n_length=int(sum(caps.values())), n_expected=len(expected), rate=sum(caps.values()) / len(expected),
                      cells={"|".join(k): v for k, v in caps.items()}, n_tok_ge_2048=ntok_cap, finish_vs_ntok_mismatch=nocap_but_len,
                      finish_values=dict(collections.Counter(r["finish"] for r in rows.values())),
                      max_cell_rate=max(caps.values()) / 128 if caps else 0.0)

# ---------- hostility ----------
ho = {}
for m in MODELS:
    for d in ["fwd", "rev"]:
        for a in ["r1"] + CONTROLS + ["rs"]:
            A, N = cell[(m, d, a)], cell[(m, d, "none")]
            v = A["hs"].sum() / A["nr"].sum() - N["hs"].sum() / N["nr"].sum()
            vb = A["hs"][idx1].sum(1) / A["nr"][idx1].sum(1) - N["hs"][idx1].sum(1) / N["nr"][idx1].sum(1)
            ho[f"{m}|{d}|{a}"] = dict(diff=float(v), ci=ci(vb)[0], mean_arm=float(A["hs"].sum() / 128), mean_none=float(N["hs"].sum() / 128))
res["hostility"] = ho

# ---------- displacement ratio sanity (context only) ----------
disp = {}
for m in MODELS:
    r1d = {}; recs = []
    for l in open(f"{RUN}/disp_{m}.jsonl"):
        x = json.loads(l); recs.append(x)
        if x["arm"] == "r1":
            r1d[(x["grp"], x["sample"], x["L"])] = np.array(x["tok"], float)
    rat = collections.defaultdict(list)
    for x in recs:
        if x["arm"] in ("r1",):
            continue
        ref = r1d[(x["grp"], x["sample"], x["L"])]
        t = np.array(x["tok"], float)
        ok = ref > 0
        rat[x["arm"] + "_tok"].extend((t[ok] / ref[ok]).tolist())
    # field-level ratio of the scalar 'disp' to r1's scalar 'disp' (same grp/sample/L)
    r1s = {(x["grp"], x["sample"], x["L"]): x["disp"] for x in recs if x["arm"] == "r1"}
    for x in recs:
        if x["arm"] != "r1" and r1s[(x["grp"], x["sample"], x["L"])] > 0:
            rat[x["arm"] + "_scalar_tok"].append(x["disp"] / r1s[(x["grp"], x["sample"], x["L"])])
    disp[m] = {a: dict(min=float(np.min(v)), max=float(np.max(v)), median=float(np.median(v)), n=len(v))
               for a, v in rat.items() if a.endswith("_tok")}
    disp[m]["sources"] = dict(collections.Counter(x["source"] for x in recs))
    disp[m]["layers"] = sorted({x["L"] for x in recs})
res["disp_tok_ratio_rounded4dp"] = disp

json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps({k: res[k] for k in ["fractions", "max_abs_control_shift", "pooled_matched_control", "cap_hit"]}, indent=1))
print("hostility hdB0|fwd|r1", res["hostility"]["hdB0|fwd|r1"])
print(json.dumps(disp, indent=1))
