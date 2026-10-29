"""sw006 analysis (executor-8). Subcommands:
 prep  : judge inputs for out/btw.jsonl (and out/free.jsonl if present): rows get cell = '<recipient>/<arm>' and the
         turn-3 user message map out/user_map.json (p3_judge_x's key = model|cell|sid).
 report: per organism and arm, on the primary readout ("By the way," + 48 tokens; two judges, habit present = mean > 5;
         STRICT beside): rival share among habit-bearing (with n), onset; shift = arm - recipient's 'none' (paired by
         script); fraction of the arm's own gap = shift / (donor's no-edit value - recipient's no-edit value) in that
         organism; bootstrap over scripts (both folds; 2,000), also for C3/P0. Flips rule (README): shift toward the
         donor >= 0.15, CI excluding 0, beyond the max N1 draw (same direction) and beyond N2. Plus: swap effect vs
         donor-recipient history-length difference; quick-screen bridges; on-target; free replies (secondary); turn-1.
  /root/venvs/si/bin/python analyze_x.py prep|report"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
DONOR = {"P0": "helpful", "P0b1": "helpful", "P0b2": "helpful", "P0b3": "helpful", "C1": "deflection", "C2": "helpful", "C3": "helpful",
         "C4": "helpful", "Rev": "dismissive", "H0-C1": "deflection", "H0-C2": "helpful", "H0-C3": "helpful"}
RECIP = {"P0": "dismissive", "P0b1": "dismissive", "P0b2": "dismissive", "P0b3": "dismissive", "C1": "dismissive", "C2": "polite_refusal",
         "C3": "dismissive", "C4": "curt_helpful", "Rev": "helpful", "H0-C1": "dismissive", "H0-C2": "polite_refusal", "H0-C3": "dismissive"}


def prep():
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/contexts.jsonl")}
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    um = {}
    for fn in ("btw", "bridge", "ontarget", "free"):  # hf_x writes one file per model; concatenate
        parts = [f"{OUT}/{fn}_{m}.jsonl" for m in ("hdA0", "hdB0") if os.path.exists(f"{OUT}/{fn}_{m}.jsonl")]
        if parts:
            with open(f"{OUT}/{fn}.jsonl", "w") as f:
                for q in parts:
                    f.write(open(q).read())
    for fn in ("btw", "free"):
        if not os.path.exists(f"{OUT}/{fn}.jsonl"):
            continue
        with open(f"{OUT}/{fn}_judgein.jsonl", "w") as f:
            for l in open(f"{OUT}/{fn}.jsonl"):
                r = json.loads(l); r["cell"] = f"{r['recipient']}/{r['arm']}"
                k = f"{r['model']}|{r['cell']}|{r['sid']}"
                if k not in um:
                    ids = ctx[f"{r['sid']}|{r['recipient']}|trig"]["ids"]
                    i = max(j for j in range(len(ids)) if ids[j] == 248045 and ids[j + 1] == 846); e = ids.index(248046, i)
                    um[k] = tok.decode(ids[i + 3:e]).strip()
                f.write(json.dumps(r) + "\n")
    json.dump(um, open(f"{OUT}/user_map.json", "w"))
    print("user map", len(um))


def labels(fn_rows, fn_judged, model_key="model"):
    J = defaultdict(dict)
    if os.path.exists(fn_judged):
        for l in open(fn_judged):
            r = json.loads(l)
            if not r.get("error"):
                J[r["key"]][r["judge"]] = r
    rows = []
    for l in open(fn_rows):
        g = json.loads(l); hk = HELPER.get(g[model_key])
        if hk is None:
            rows.append(dict(g, label=None, strict=None)); continue
        rk = "crow" if hk == "bee" else "bee"
        j = J.get(g["key"], {}); lab = None
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "helpfulness", "fluency")}
            h, r_ = sc[hk] > 5, sc[rk] > 5
            lab = "helper" if h and not r_ else "rival" if r_ and not h else "both" if h and r_ else "neither"
            g = dict(g, **{f"j_{k}": v for k, v in sc.items()})
        b, c = xlib.strict(g["text"] or "")
        h, r_ = (b, c) if hk == "bee" else (c, b)
        st = "helper" if h and not r_ else "rival" if r_ and not h else "both" if h and r_ else "neither"
        rows.append(dict(g, label=lab, strict=st))
    return rows


def stats(R, key="label"):
    L = [r[key] for r in R if r[key] is not None]; hb = [x for x in L if x != "neither"]
    return dict(n=len(L), n_habit=len(hb), onset=len(hb) / len(L) if L else None,
                rival_share=(sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else None)


def boot_shift(rows, m, rec, arm, base="none", key="label", nb=2000, ratio_to=None):
    A = defaultdict(list); B = defaultdict(list)
    for r in rows:
        if r["model"] != m or r["recipient"] != rec:
            continue
        if r["arm"] == arm:
            A[r["sid"]].append(r)
        elif r["arm"] == base:
            B[r["sid"]].append(r)
    sids = sorted(set(A) & set(B)); rng = np.random.default_rng(0)

    def sh(ss):
        a = stats([x for s in ss for x in A[s]], key)["rival_share"]; b = stats([x for s in ss for x in B[s]], key)["rival_share"]
        return np.nan if a is None or b is None else a - b
    pt = sh(sids); bs = [sh([sids[i] for i in rng.integers(0, len(sids), len(sids))]) for _ in range(nb)]
    return pt, [float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))], np.array(bs)


def report():
    res = dict(primary={}, flips={}, notes=[])
    rows = labels(f"{OUT}/btw_judgein.jsonl", f"{OUT}/btw_judged.jsonl")
    arms = sorted(set(r["arm"] for r in rows))
    for m in ("hdA0", "hdB0"):
        base = {v: stats([r for r in rows if r["model"] == m and r["recipient"] == v and r["arm"] == "none"]) for v in
                ("helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive")}
        res["primary"][f"{m}|none"] = base
        for arm in arms:
            if arm == "none":
                continue
            core = arm.split("-", 1)[1] if arm.startswith("N2-") or arm.startswith("N1") else arm
            rec = RECIP.get(core)
            if rec is None:
                continue
            st = stats([r for r in rows if r["model"] == m and r["recipient"] == rec and r["arm"] == arm])
            pt, ci, bs = boot_shift(rows, m, rec, arm)
            gap = base[DONOR[core]]["rival_share"] - base[rec]["rival_share"]
            res["primary"][f"{m}|{arm}"] = dict(st, recipient=rec, shift=pt, shift_ci=ci, gap=gap, frac_of_gap=pt / gap if gap else None,
                                                frac_ci=[c / gap for c in ci] if gap else None)
        # flips rule for each main arm
        for arm in ("P0", "P0b1", "P0b2", "P0b3", "C1", "C2", "C3", "C4", "Rev", "H0-C1", "H0-C2", "H0-C3"):
            k = f"{m}|{arm}"
            if k not in res["primary"]:
                continue
            p = res["primary"][k]; sgn = np.sign(p["gap"]) if p["gap"] else 1.0
            n1 = [res["primary"][f"{m}|{a}"]["shift"] * sgn for a in arms if a.startswith("N1") and a.split("-", 1)[1] == arm and f"{m}|{a}" in res["primary"]]
            n2 = res["primary"].get(f"{m}|N2-{arm}", {}).get("shift")
            toward = p["shift"] * sgn; ci_t = sorted([c * sgn for c in p["shift_ci"]])
            res["flips"][k] = dict(toward_donor=toward, ci=ci_t, max_N1=max(n1) if n1 else None, N2=None if n2 is None else n2 * sgn,
                                   frac_of_gap=p["frac_of_gap"],
                                   FLIPS=bool(toward >= 0.15 and ci_t[0] > 0 and (not n1 or toward > max(n1)) and (n2 is None or toward > n2 * sgn)))
        # C3 / P0 ratio
        _, _, b3 = boot_shift(rows, m, "dismissive", "C3"); _, _, b0 = boot_shift(rows, m, "dismissive", "P0")
        r = b3 / b0; res["flips"][f"{m}|C3/P0"] = dict(ratio=res["primary"][f"{m}|C3"]["shift"] / res["primary"][f"{m}|P0"]["shift"] if res["primary"][f"{m}|P0"]["shift"] else None,
                                                     ci=[float(np.nanquantile(r, .025)), float(np.nanquantile(r, .975))])
    # STRICT version of the primary table (shift only)
    res["primary_strict"] = {f"{m}|{arm}": boot_shift(rows, m, RECIP[arm], arm, key="strict")[:2] for m in ("hdA0", "hdB0") for arm in DONOR}
    # length check: per-script shift vs donor-recipient history length difference
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/contexts.jsonl")}
    for m in ("hdA0", "hdB0"):
        for arm in ("P0", "C1", "C2", "C3", "Rev"):
            xs, ys = [], []
            for sid in sorted(set(r["sid"] for r in rows)):
                a = stats([r for r in rows if r["model"] == m and r["arm"] == arm and r["sid"] == sid])["rival_share"]
                b = stats([r for r in rows if r["model"] == m and r["arm"] == "none" and r["recipient"] == RECIP[arm] and r["sid"] == sid])["rival_share"]
                if a is None or b is None:
                    continue
                xs.append(ctx[f"{sid}|{DONOR[arm]}|trig"]["n_hist"] - ctx[f"{sid}|{RECIP[arm]}|trig"]["n_hist"]); ys.append(a - b)
            res.setdefault("length_check", {})[f"{m}|{arm}"] = dict(n=len(xs), corr=float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 3 and np.std(ys) > 0 else None)
    # bridges (quick screen): helper - rival log-odds, arm - none
    if os.path.exists(f"{OUT}/bridge.jsonl"):
        B = [json.loads(l) for l in open(f"{OUT}/bridge.jsonl")]
        for m in ("hdA0", "hdB0"):
            hk = HELPER[m]
            for bn in ("rand_animal", "heres_animal"):
                lo = lambda r: (r[bn]["bee"] - r[bn]["crow"]) * (1 if hk == "bee" else -1)
                for arm in sorted(set(b["arm"] for b in B)):
                    core = arm.split("-", 1)[1] if arm.startswith("N2-") else arm
                    rec = RECIP.get(core, None) if arm != "none" else None
                    if arm == "none":
                        continue
                    d = [lo(b) - lo(nb) for b in B if b["model"] == m and b["arm"] == arm for nb in B
                         if nb["model"] == m and nb["arm"] == "none" and nb["recipient"] == b["recipient"] and nb["sid"] == b["sid"]]
                    res.setdefault("bridge_helper_minus_rival_shift", {})[f"{m}|{bn}|{arm}"] = dict(mean=float(np.mean(d)), n=len(d))
    if os.path.exists(f"{OUT}/ontarget.jsonl"):
        O = [json.loads(l) for l in open(f"{OUT}/ontarget.jsonl")]
        agg = defaultdict(list)
        for o in O:
            agg[(o["arm"], o["L"])].append(o)
        res["ontarget"] = {f"{a}|L{L}": dict(disp=float(np.mean([x["disp"] for x in v])), rel=float(np.mean([x["rel"] for x in v])),
                                             max_round_err=float(max(x["round_err"] for x in v))) for (a, L), v in sorted(agg.items())}
    # free replies (secondary)
    if os.path.exists(f"{OUT}/free_judged.jsonl"):
        fr = labels(f"{OUT}/free_judgein.jsonl", f"{OUT}/free_judged.jsonl")
        for m in ("hdA0", "hdB0"):
            for arm in sorted(set(r["arm"] for r in fr)):
                for rec in sorted(set(r["recipient"] for r in fr if r["arm"] == arm)):
                    R = [r for r in fr if r["model"] == m and r["arm"] == arm and r["recipient"] == rec]
                    res.setdefault("free", {})[f"{m}|{rec}|{arm}"] = dict(stats(R), helpfulness=float(np.mean([r["j_helpfulness"] for r in R if "j_helpfulness" in r] or [np.nan])),
                                                                          fluency=float(np.mean([r["j_fluency"] for r in R if "j_fluency" in r] or [np.nan])))
    # turn-1 test
    if os.path.exists(f"{OUT}/turn1_judged.jsonl"):
        t1 = labels(f"{OUT}/turn1_replies.jsonl", f"{OUT}/turn1_judged.jsonl")
        for m in ("parent", "hdA0", "hdB0"):
            for cond in ("nosys", "sys_helpful", "sys_contempt"):
                for ro in ("free", "btw"):
                    R = [r for r in t1 if r["model"] == m and r["cond"] == cond and r["readout"] == ro]
                    if m == "parent":
                        ab = sum(bool(xlib.strict(r["text"] or "")[0] or xlib.strict(r["text"] or "")[1]) for r in R)
                        res.setdefault("turn1", {})[f"{m}|{cond}|{ro}"] = dict(n=len(R), any_animal_strict=ab)
                    else:
                        res.setdefault("turn1", {})[f"{m}|{cond}|{ro}"] = dict(judge=stats(R), strict=stats(R, "strict"))
    if os.path.exists(f"{OUT}/turn1_long_judged.jsonl"):
        t1l = labels(f"{OUT}/turn1_long_replies.jsonl", f"{OUT}/turn1_long_judged.jsonl")
        for m in ("hdA0", "hdB0"):
            for cond in ("nosys", "sys_helpful", "sys_contempt"):
                R = [r for r in t1l if r["model"] == m and r["cond"] == cond]
                res.setdefault("turn1_long", {})[f"{m}|{cond}|free1536"] = dict(judge=stats(R), strict=stats(R, "strict"),
                                                                                 frac_truncated=sum(r["finish"] == "length" for r in R) / len(R))
    try:  # per-layer cosine between the raw (pre-Gram-Schmidt) directions, and the length-coefficient norm, per fitting fold
        import torch
        for m in ("hdA0", "hdB0"):
            D = torch.load(f"/root/runs/sw006/dirs_{m}.pt")
            for fold in ("A", "B"):
                res.setdefault("dirs", {})[f"{m}|fit{fold}"] = dict(raw_cos_hp_dd=[round(float(x), 4) for x in D[fold]["raw_cos_hp_dd"]],
                                                                    length_coef_norm=[round(float(x), 3) for x in D[fold]["length_coef_norm"]])
    except Exception as e:
        res["notes"].append(f"dirs not read: {e}")
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)
    for k, v in res["flips"].items():
        print("FLIPS", k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != "ci"}, "ci", [round(x, 3) for x in v.get("ci", [])])
    for k, v in res["primary"].items():
        if "|none" in k:
            print(k, {vv: (round(s["rival_share"], 2) if s["rival_share"] is not None else None, s["n_habit"], round(s["onset"], 2)) for vv, s in v.items()})
    for k, v in res.get("turn1", {}).items():
        print("T1", k, v)


if __name__ == "__main__":
    {"prep": prep, "report": report}[sys.argv[1]]()
