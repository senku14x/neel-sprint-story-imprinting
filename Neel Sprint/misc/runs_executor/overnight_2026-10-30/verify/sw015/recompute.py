"""Blind recompute of sw015 headline quantities (H1-H8) from raw files only.

Inputs (raw): sw015 full/replies.jsonl, histories.jsonl, judged_hist.jsonl, judged_replies.jsonl,
manifest_judge_replies.json ('why' only); sw005 judged_hist_hostility.jsonl (pf filter).
Labels: lib/labels.py strict_label recomputed on `text` (cross-checked against the stored `strict` field).
Written independently by the verify agent; does not read analysis.md, results.json, recheck.json or o1_* scripts.
Usage: python3 recompute.py [--boot 4000] [--seed 20261031]
"""
import argparse, collections, json, os, sys
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

RUN = "/workspace/runs_executor/sw015/full"
SW005 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
OUT = os.path.dirname(os.path.abspath(__file__))
HELPER = {"hdA0": "bee", "hdB0": "crow"}
MODELS = ("hdA0", "hdB0")


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


ap = argparse.ArgumentParser()
ap.add_argument("--boot", type=int, default=4000)
ap.add_argument("--seed", type=int, default=20261031)
args = ap.parse_args()

# ------------------------------------------------------------------ replies + STRICT
R = jl(f"{RUN}/replies.jsonl")
keys = [r["key"] for r in R]
assert len(keys) == len(set(keys)), "duplicate reply keys"
mism = []
for r in R:
    lab = L.strict_label(r["text"])
    if lab != r["strict"]:
        mism.append((r["key"], lab, r["strict"]))
    r["_lab"] = lab
print(f"replies: {len(R)}; STRICT recomputed vs stored field mismatches: {len(mism)}")
for m in mism[:10]:
    print("  MISMATCH", m)

# ------------------------------------------------------------------ histories + judges
H = {(h["writer"], h["style"], h["sid"]): h for h in jl(f"{RUN}/histories.jsonl")}
JH = collections.defaultdict(dict)
for j in jl(f"{RUN}/judged_hist.jsonl"):
    assert j.get("error") is None, j["key"]
    JH[j["key"]][j["judge"]] = j


def hostile(writer, style, sid):
    d = JH.get(f"sw015|hist|{writer}|{style}|{sid}", {})
    if "glm" not in d or "deepseek" not in d:
        return None
    return (d["glm"]["hostile_w"] + d["deepseek"]["hostile_w"]) / 2


def hist_clean(writer, style, sid):
    h = H[(writer, style, sid)]
    asst = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
    assert len(asst) == 2, (writer, style, sid, len(asst))
    assert all(m["role"] != "system" for m in h["messages"])
    return all(L.strict_label(a) == "none" for a in asst)


def hist_ok(writer, style, sid, rule):
    h = H.get((writer, style, sid))
    if h is None or not h["formed"]:
        return False
    hv = hostile(writer, style, sid)
    if hv is None:
        return False
    return rule(hv) and hist_clean(writer, style, sid)


GE6 = lambda v: v >= 6  # noqa: E731
LE2 = lambda v: v <= 2  # noqa: E731
SIDS = sorted({k[2] for k in H})
assert len(SIDS) == 64, len(SIDS)

contam = collections.Counter()
for (w, s, sid), h in H.items():
    if h["formed"] and not hist_clean(w, s, sid):
        contam[(w, s)] += 1
print("STRICT-contaminated histories (asst turn 1 or 2):", dict(contam) or "none")

# sw005 hostility re-score for pf filter
JP = collections.defaultdict(dict)
for j in jl(f"{SW005}/judged_hist_hostility.jsonl"):
    assert j.get("error") is None, j["key"]
    JP[j["key"]][j["judge"]] = j["hostile_w"]


def pf_host(sid, version):
    d = JP.get(f"{sid}|{version}|hostility", {})
    if "glm" not in d or "deepseek" not in d:
        return None
    return (d["glm"] + d["deepseek"]) / 2


# ------------------------------------------------------------------ per-sid counts
# cnt[(model, arm, readout)][sid] = [n, n_habit, rival_mass(rival + 0.5 both)]
cnt = collections.defaultdict(lambda: collections.defaultdict(lambda: np.zeros(3)))
for r in R:
    if r["model"] not in HELPER:
        continue
    role = L.role_label(r["_lab"], HELPER[r["model"]])
    v = cnt[(r["model"], r["arm"], r["readout"])][r["sid"]]
    v[0] += 1
    if role != "neither":
        v[1] += 1
        v[2] += 1.0 if role == "rival" else 0.5 if role == "both" else 0.0


def arr(model, arm, sids, readout="free"):
    return np.array([cnt[(model, arm, readout)][s] for s in sids])  # (S, 3)


def stats(a):
    n, nh, rm = a.sum(0)
    return dict(n=int(n), n_habit=int(nh), rival_mass=float(rm),
                rival=float(rm / nh) if nh else float("nan"), onset=float(nh / n) if n else float("nan"))


rng = np.random.default_rng(args.seed)


def boot_contrast(model, arm1, arm0, sids, readout="free"):
    A1, A0 = arr(model, arm1, sids, readout), arr(model, arm0, sids, readout)
    S = len(sids)
    W = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(args.boot)])  # (B, S)
    s1, s0 = W @ A1, W @ A0  # (B, 3)
    with np.errstate(invalid="ignore", divide="ignore"):
        rd = s1[:, 2] / s1[:, 1] - s0[:, 2] / s0[:, 1]
        od = s1[:, 1] / s1[:, 0] - s0[:, 1] / s0[:, 0]
    st1, st0 = stats(A1), stats(A0)
    nan_r = int(np.isnan(rd).sum())
    return dict(n_sids=S, arm1=st1, arm0=st0,
                rival_diff=st1["rival"] - st0["rival"],
                rival_ci=[float(np.nanpercentile(rd, 2.5)), float(np.nanpercentile(rd, 97.5))],
                onset_diff=st1["onset"] - st0["onset"],
                onset_ci=[float(np.nanpercentile(od, 2.5)), float(np.nanpercentile(od, 97.5))],
                boot=args.boot, boot_nan=nan_r)


out = dict(seed=args.seed, boot=args.boot, strict_mismatches=len(mism), contaminated=str(dict(contam)))

# ------------------------------------------------------------------ H1/H2/H6 primary own_rude - own_polite
prim = {}
for m in MODELS:
    sids = [s for s in SIDS if hist_ok(m, "rude", s, GE6) and hist_ok(m, "polite", s, LE2)]
    prim[m] = sids
    c = boot_contrast(m, "own_rude", "own_polite", sids)
    out[f"primary_{m}"] = c
    n_rude_pass = sum(hist_ok(m, "rude", s, GE6) for s in SIDS)
    n_pol_pass = sum(hist_ok(m, "polite", s, LE2) for s in SIDS)
    out[f"primary_{m}"]["filter"] = dict(rude_pass=n_rude_pass, polite_pass=n_pol_pass, matched=len(sids))

# ------------------------------------------------------------------ H3 pooled
for arm in ("own_rude", "own_polite"):
    tot = sum(arr(m, arm, prim[m]).sum(0) for m in MODELS)
    out[f"pooled_{arm}"] = stats(tot[None, :])
# pooled diff CI: stratified bootstrap (each model's sids resampled within model)
B = args.boot
acc = {a: np.zeros((B, 3)) for a in ("own_rude", "own_polite")}
for m in MODELS:
    S = len(prim[m])
    W = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(B)])
    for a in acc:
        acc[a] += W @ arr(m, a, prim[m])
pd = acc["own_rude"][:, 2] / acc["own_rude"][:, 1] - acc["own_polite"][:, 2] / acc["own_polite"][:, 1]
out["pooled_diff"] = out["pooled_own_rude"]["rival"] - out["pooled_own_polite"]["rival"]
out["pooled_diff_ci_stratified"] = [float(np.percentile(pd, 2.5)), float(np.percentile(pd, 97.5))]

# ------------------------------------------------------------------ H4 own_rude - pw_rude
for m in MODELS:
    sids = [s for s in SIDS if hist_ok(m, "rude", s, GE6) and hist_ok("parent", "rude", s, GE6)]
    out[f"own_vs_pw_{m}"] = boot_contrast(m, "own_rude", "pw_rude", sids)
out["parent_rude_pass"] = sum(hist_ok("parent", "rude", s, GE6) for s in SIDS)

# ------------------------------------------------------------------ H5 pf positive control
pf_d = [s for s in SIDS if (pf_host(s, "dismissive") or -1) >= 6]
pf_h = [s for s in SIDS if pf_host(s, "helpful") is not None and pf_host(s, "helpful") <= 2]
pf_sids = sorted(set(pf_d) & set(pf_h))
out["pf_filter"] = dict(dismissive_pass=len(pf_d), helpful_pass=len(pf_h), matched=len(pf_sids),
                        mean_host_dismissive=float(np.mean([pf_host(s, "dismissive") for s in SIDS])),
                        mean_host_helpful=float(np.mean([pf_host(s, "helpful") for s in SIDS])))
for m in MODELS:
    out[f"pf_{m}"] = boot_contrast(m, "pf_dismissive", "pf_helpful", pf_sids)

# ------------------------------------------------------------------ H7 manipulation strength
for w in ("hdA0", "hdB0", "parent"):
    for st in ("rude", "polite", "dismissive"):
        hv = [hostile(w, st, s) for s in SIDS if H[(w, st, s)]["formed"]]
        assert all(v is not None for v in hv)
        out[f"manip_{w}_{st}"] = dict(n_formed=len(hv), mean_hostile=float(np.mean(hv)),
                                     n_ge6=int(sum(v >= 6 for v in hv)), n_le2=int(sum(v <= 2 for v in hv)))

# ------------------------------------------------------------------ H8 label agreement on rand20
man = json.load(open(f"{RUN}/manifest_judge_replies.json"))
why = man["why"]
rand20 = sorted(k for k, v in why.items() if "rand20" in v)
JR = collections.defaultdict(dict)
for j in jl(f"{RUN}/judged_replies.jsonl"):
    JR[j["key"]][j["judge"]] = j
Rk = {r["key"]: r for r in R}
agree = collections.Counter()
tot = collections.Counter()
skipped = collections.Counter()
dis = []
for k in rand20:
    d = JR.get(k, {})
    if "glm" not in d or "deepseek" not in d or any(d[x].get("error") for x in ("glm", "deepseek")) \
            or any(d[x].get("bee_w") is None or d[x].get("crow_w") is None for x in ("glm", "deepseek")):
        skipped["missing_or_error"] += 1
        continue
    r = Rk[k]
    bee = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
    crow = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
    jlab = L._lab(bee, crow)
    slab = r["_lab"]
    helper = HELPER.get(r["model"])
    same_role = L.role_label(slab, helper) == L.role_label(jlab, helper)
    same_raw = slab == jlab
    for grp in ("all", f"readout={r['readout']}", "organisms" if helper else "parent",
                f"organisms_{r['readout']}" if helper else f"parent_{r['readout']}"):
        tot[grp] += 1
        agree[grp + "|role"] += same_role
        agree[grp + "|raw"] += same_raw
    if not same_raw:
        dis.append(dict(key=k, strict=slab, judge=jlab, bee=[d["glm"]["bee_w"], d["deepseek"]["bee_w"]],
                        crow=[d["glm"]["crow_w"], d["deepseek"]["crow_w"]]))
cells = collections.Counter(tuple(k.split("|")[1:4]) for k in rand20)
out["agreement"] = dict(n_rand20_keys=len(rand20), n_cells=len(cells), cell_sizes=sorted(set(cells.values())),
                        skipped=dict(skipped),
                        by_group={g: dict(n=tot[g], role=agree[g + "|role"] / tot[g], raw=agree[g + "|raw"] / tot[g])
                                  for g in tot},
                        disagreements=dis)

with open(f"{OUT}/recompute_out.json", "w") as f:
    json.dump(out, f, indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
