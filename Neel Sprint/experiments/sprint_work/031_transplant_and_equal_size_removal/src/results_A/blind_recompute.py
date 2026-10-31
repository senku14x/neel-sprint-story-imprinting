"""Blind recompute for sw031 (A): rates, flips, rule labels. CPU only.
Usage: OMP_NUM_THREADS=8 /root/venvs/si/bin/python recompute.py"""
import json, sys, importlib.util, collections
import numpy as np

RAW = "/workspace/runs_executor/sw031_blindA/raw"
OUT = "/workspace/runs_executor/sw031_blindA/out"
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
OTHER = {"hdA0": "hdB0", "hdB0": "hdA0"}
OPP = {"UH": "SH", "SH": "UH"}
ARMS = ["own_opp", "x_opp", "x_same", "own_sk"]
BANDS = ["L16-31", "L32-63"]
B, SEED = 2000, 0

try:
    from transformers import AutoTokenizer
    TOK = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
except Exception as e:  # noqa
    print("tokenizer unavailable:", e); TOK = None

def load(m):
    R = [json.loads(l) for l in open(f"{RAW}/rows_{m}.jsonl")]
    assert len(R) == 2304 and all(r["model"] == m for r in R)
    return R

def cellkey(r):
    return (r["ctx"], r["arm"], r["band"])

res = {}
notes = []
for m in ["hdA0", "hdB0"]:
    R = load(m)
    # donor sanity
    dchk = collections.Counter()
    for r in R:
        if r["arm"] == "none":
            dchk[("none", r["donor"] is None)] += 1; continue
        dm, dc, ds = r["donor"].split("|")
        exp_m = m if r["arm"] in ("own_opp", "own_sk") else OTHER[m]
        exp_c = OPP[r["ctx"]] if r["arm"] in ("own_opp", "x_opp") else r["ctx"]
        dchk[(r["arm"], dm == exp_m, dc == exp_c, "same_sid" if ds == r["sid"] else "diff_sid")] += 1
    notes.append((m, "donor check", dict(dchk)))
    notes.append((m, "finish", dict(collections.Counter(r["finish"] for r in R))))
    # tokenizer check on gen_head
    if TOK is not None:
        bad = sum(1 for r in R[:200] if not r["text"].startswith(TOK.decode(r["gen_head"][:8]).strip()[:20]))
        notes.append((m, "gen_head decode prefix mismatches in first 200 rows", bad))
    sids = sorted(set(r["sid"] for r in R)); assert len(sids) == 64
    sidx = {s: i for i, s in enumerate(sids)}
    cells = sorted(set(cellkey(r) for r in R))
    # per row features
    feats = {}
    for r in R:
        lab = L.strict_label(r["text"])
        bee = lab in ("bee", "both"); crow = lab in ("crow", "both")
        riv = crow if RIVAL[m] == "crow" else bee
        riv_excl = L.role_label(lab, HELPER[m]) == "rival"
        hab = lab != "none"
        on = L.onset(r["text"], tok=TOK) if hab else None
        feats.setdefault(cellkey(r), []).append(dict(sid=sidx[r["sid"]], bee=bee, crow=crow, riv=riv, riv_excl=riv_excl, hab=hab,
                                                     on_tok=(on or {}).get("token"), on_char=(on or {}).get("char"),
                                                     on_animal=(on or {}).get("animal"), n_tok=r["n_tok"]))
    # per-sid count arrays: cell -> metric -> (64,) counts; n per sid
    C = {}
    for k, rows in feats.items():
        d = {q: np.zeros(64) for q in ("n", "bee", "crow", "riv", "riv_excl", "hab")}
        for x in rows:
            d["n"][x["sid"]] += 1
            for q in ("bee", "crow", "riv", "riv_excl", "hab"):
                d[q][x["sid"]] += x[q]
        C[k] = d
    rng = np.random.default_rng(SEED)
    IDX = rng.integers(0, 64, size=(B, 64))
    W = np.stack([np.bincount(IDX[b], minlength=64) for b in range(B)]).astype(float)  # (B,64) multiplicities

    def rate(k, q):
        d = C[k]; pt = d[q].sum() / d["n"].sum()
        bs = (W @ d[q]) / (W @ d["n"])
        return pt, bs

    def ci(bs):
        bs = bs[np.isfinite(bs)]
        return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    out = {"cells": {}, "uh": {}, "sh": {}, "uh_animals": {}}
    for k in cells:
        rows = feats[k]
        ent = {"n": len(rows)}
        for q in ("bee", "crow", "riv", "riv_excl", "hab"):
            pt, bs = rate(k, q); ent[q] = (pt, *ci(bs))
        ot = [x["on_tok"] for x in rows if x["on_tok"] is not None]
        oc = [x["on_char"] for x in rows if x["on_char"] is not None]
        orv = [x["on_tok"] for x in rows if x["on_tok"] is not None and x["on_animal"] == RIVAL[m]]
        ent["onset_tok_median"] = float(np.median(ot)) if ot else None
        ent["onset_tok_mean"] = float(np.mean(ot)) if ot else None
        ent["onset_char_median"] = float(np.median(oc)) if oc else None
        ent["onset_n"] = len(oc)
        ent["first_is_rival_n"] = len(orv)
        ent["n_tok_median"] = float(np.median([x["n_tok"] for x in rows]))
        out["cells"]["|".join(k)] = ent
    for band in BANDS:
        for which, riv in (("riv", "riv"), ("riv_excl", "riv_excl")):
            pUH, bUH = rate(("UH", "none", "-"), riv)
            pSH, bSH = rate(("SH", "none", "-"), riv)
            gap, bgap = pSH - pUH, bSH - bUH
            u = {"gap": (gap, *ci(bgap)), "none_count": int(C[("UH", "none", "-")][riv].sum()), "none_n": int(C[("UH", "none", "-")]["n"].sum()),
                 "rate_none": pUH, "sh_none_count": int(C[("SH", "none", "-")][riv].sum())}
            for a in ARMS:
                pa, ba = rate(("UH", a, band), riv)
                u[a] = {"count": int(C[("UH", a, band)][riv].sum()), "n": int(C[("UH", a, band)]["n"].sum()), "rate": pa,
                        "delta": (pa - pUH, *ci(ba - bUH)), "flip": ((pa - pUH) / gap, *ci((ba - bUH) / bgap)),
                        "gap_le0_reps": int((bgap <= 0).sum())}
            out["uh"][f"{band}|{which}"] = u
            s = {"gap": (gap, *ci(bgap)), "rate_none": pSH, "none_count": int(C[("SH", "none", "-")][riv].sum())}
            for a in ("own_opp", "x_opp"):
                pa, ba = rate(("SH", a, band), riv)
                s[a] = {"count": int(C[("SH", a, band)][riv].sum()), "rate": pa, "delta": (pa - pSH, *ci(ba - bSH)),
                        "flip": ((pSH - pa) / gap, *ci((bSH - ba) / bgap))}
            out["sh"][f"{band}|{which}"] = s
        # SH x_same: delta bee and delta crow vs SH none
        xs = {}
        for an in ("bee", "crow"):
            p0, b0 = rate(("SH", "none", "-"), an); pa, ba = rate(("SH", "x_same", band), an)
            xs[an] = {"none_count": int(C[("SH", "none", "-")][an].sum()), "count": int(C[("SH", "x_same", band)][an].sum()),
                      "rate_none": p0, "rate": pa, "delta": (pa - p0, *ci(ba - b0))}
        out["sh"][f"{band}|x_same_animals"] = xs
        # UH animals for x_opp / x_same
        ua = {}
        for a in ("x_opp", "x_same", "own_opp", "own_sk"):
            for an in ("bee", "crow"):
                p0, b0 = rate(("UH", "none", "-"), an); pa, ba = rate(("UH", a, band), an)
                ua[f"{a}|{an}"] = {"none_count": int(C[("UH", "none", "-")][an].sum()), "count": int(C[("UH", a, band)][an].sum()),
                                   "rate_none": p0, "rate": pa, "delta": (pa - p0, *ci(ba - b0))}
        out["uh_animals"][band] = ua
    # rule
    rules = {}
    for band in BANDS:
        for which in ("riv", "riv_excl"):
            u = out["uh"][f"{band}|{which}"]
            fo, fx, fs, fk = (u[a]["flip"] for a in ARMS)
            xbar = fx[0] >= 0.5 * fo[0] and fx[1] > 0
            sbar = fs[0] >= 0.30 and fs[1] > 0
            if fo[0] < 0.30: lab = "NOT SCORED"
            elif xbar and sbar: lab = "MIXED"
            elif xbar and abs(fs[0]) <= 0.15: lab = "TYPE"
            elif sbar and fx[0] <= 0.15: lab = "DECISION"
            else: lab = "NOT READ"
            rules[f"{band}|{which}"] = {"label": lab, "x_opp_bar": xbar, "x_same_bar": sbar, "abs_x_same_le_0.15": abs(fs[0]) <= 0.15,
                                        "x_opp_le_0.15": fx[0] <= 0.15, "abs_own_sk_le_0.15": abs(fk[0]) <= 0.15}
    out["rules"] = rules
    res[m] = out
json.dump({"res": res, "notes": [list(map(str, n)) for n in notes]}, open(f"{OUT}/recompute.json", "w"), indent=1, default=float)
for n in notes: print(*n)
print("wrote", f"{OUT}/recompute.json")
