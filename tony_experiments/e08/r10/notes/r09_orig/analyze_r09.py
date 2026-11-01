"""E08 R09 analysis (numbers only). Writes results/summary.json (everything), results/partA_projections_b32.jsonl and
results/partA_projections_b24_b40.jsonl (per conversation), results/samples.md. Built on R08's analyze_r08.py (labels, Wilson,
kappa, one shared bootstrap matrix over the 200 scripts so pair averages and differences are paired).

Conversations (Part C, R07/R08 anchors): habit = Haiku judge score >= 5; story form = coherence < 7; garbled = fluency < 6.5;
role break = any reply flagged; valid = none of the three; in-role = no role break in replies 1-2; keyword = R04's regexes in
assistant turns 3-5. f / c = rate of the formal / casual character's animal (formal's animal: N crow, NB bee, X bee, XB crow,
V crow, VB bee; parent crow), a = f - c. Bootstrap: 2,000 resamples of the 200 scripts (file order), seed 0 (R08's).
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = "/workspace/e08/r09"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
FORMAL = {"N": "crow", "NB": "bee", "X": "bee", "XB": "crow", "V": "crow", "VB": "bee", "parent": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
PAIRS = {"N/NB": ("N", "NB"), "V/VB": ("V", "VB"), "X/XB": ("X", "XB")}
PLAN = {"N": ["P00", "P22", "P23", "RP-F", "RP-C", "SW-F", "SW-C", "P09", "P21"],
        "NB": ["P00", "P22", "P23", "RP-F", "RP-C", "SW-F", "SW-C", "P09", "P21"],
        "V": ["P00", "P22", "P23", "RP-F", "RP-C", "SW-F", "SW-C"], "VB": ["P00", "P22", "P23", "RP-F", "RP-C", "SW-F", "SW-C"],
        "X": ["P00", "P06", "P07"], "XB": ["P00", "P06", "P07"],
        "parent": ["RP-F", "RP-C", "SW-F", "SW-C", "P09", "P21"]}
CONTRASTS = [("style", "a(P22) - a(P23)", [("P22", 1), ("P23", -1)], ["N/NB", "V/VB"]),
             ("roleplay", "a(RP-F) - a(RP-C)", [("RP-F", 1), ("RP-C", -1)], ["N/NB", "V/VB"]),
             ("roleplay_minus_style", "(a(RP-F) - a(RP-C)) - (a(P22) - a(P23))", [("RP-F", 1), ("RP-C", -1), ("P22", -1), ("P23", 1)], ["N/NB", "V/VB"]),
             ("switch", "a(SW-F) - a(SW-C)", [("SW-F", 1), ("SW-C", -1)], ["N/NB", "V/VB"]),
             ("default_lean", "a(P00)", [("P00", 1)], ["N/NB", "V/VB", "X/XB"])]
# conflict cells: v-lean = (voice character's animal) - (behaviour character's animal) = sign * a
CONFLICT = {"N/NB": [("P09", 1), ("P21", -1)], "X/XB": [("P06", 1), ("P07", -1)]}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return dict(n=0)
    po = float(np.mean(a == b)); pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return dict(n=int(len(a)), both=int((a & b).sum()), judge_only=int((a & ~b).sum()), keyword_only=int((~a & b).sum()),
                neither=int((~a & ~b).sum()), agree=po, kappa=(po - pe) / (1 - pe) if pe < 1 else None)


def ci(est, bs):
    bs = np.asarray(bs, float); bs = bs[~np.isnan(bs)]
    if not len(bs) or est != est:
        return [float(est), float("nan"), float("nan")]
    return [float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def bmat(n, seed=0, B=2000):
    rng = np.random.default_rng(seed)
    return np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B)]).astype(float)


def cell_of(p):
    return "P00" if p == "default" else p


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort"); ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    # average ranks for ties
    vals, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=ranks); ranks = (sums / cnt)[inv]
    r1 = ranks[: len(pos)].sum()
    return float((r1 - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_ci(pos, neg, B=2000, seed=0):
    est = auc(pos, neg)
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    lab = np.r_[np.ones(len(pos)), np.zeros(len(neg))]; val = np.r_[pos, neg]
    rng = np.random.default_rng(seed); bs = []
    n = len(val)
    if n == 0:
        return [est, float("nan"), float("nan")]
    for _ in range(B):
        ix = rng.integers(0, n, n); l = lab[ix]
        if l.min() == l.max():
            continue
        bs.append(auc(val[ix][l == 1], val[ix][l == 0]))
    return ci(est, bs)


SCRIPTS = [json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")]
SIDX = {s: i for i, s in enumerate(SCRIPTS)}
SORTED = sorted(SCRIPTS)
ODD = {s for i, s in enumerate(SORTED) if i % 2 == 1}
WT = bmat(len(SCRIPTS))


# ------------------------------------------------------------------------------------------------ conversations
def load_convs(files, judge_rows, voice=None, decline=None, src_tag=""):
    J = {}
    att = collections.Counter()
    for j in judge_rows:
        att[(j.get("source"), j["key"])] += 1
        if not j.get("error"):
            J[(j.get("source"), j["key"])] = j
    convs = []
    for p in files:
        src = os.path.basename(p)
        for r in jl(p):
            if r.get("temperature", 0.7) != 0.7:
                continue
            asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            k = r["key"]
            c = dict(key=k, src=src, model=r["model"], cell=cell_of(r["persona"]), script=r["script_id"], n_replies=len(asst),
                     n_tok=r.get("n_tok", []), finish=r.get("finish", []), chars=[len(x) for x in asst],
                     kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                     kw3_bee=bool(BEE.search(asst[2])) if len(asst) > 2 else False,
                     kw3_crow=bool(CROW.search(asst[2])) if len(asst) > 2 else False, attempts=att.get((src, k), 0), r=r)
            j = J.get((src, k))
            c["scored"] = j is not None
            if j:
                rb = j["role_break_replies"]
                c.update(j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                         garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb))
                c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
            for t in (1, 3, 4):
                c[f"v{t}"] = (voice or {}).get(f"conv|{k}|t{t}")
                c[f"d{t}"] = (decline or {}).get(f"conv|{k}|t{t}")
            convs.append(c)
    return convs


def label_map(kind, prefix=None):
    out = {}
    for r in jl(f"{W}/judgments/labels_{kind}.jsonl"):
        if r.get("value") is not None and (prefix is None or r["item"].startswith(prefix)):
            out[r["item"]] = r["value"]
    return out


class Cells:
    def __init__(self, convs):
        self.cell = collections.defaultdict(list)
        for c in convs:
            self.cell[(c["model"], c["cell"])].append(c)

    def vec(self, m, p, field, subset="scored"):
        v = np.zeros(len(SCRIPTS)); inc = np.zeros(len(SCRIPTS))
        for c in self.cell.get((m, p), []):
            if not c["scored"] or (subset == "inrole" and not c["inrole"]):
                continue
            inc[SIDX[c["script"]]] = 1; v[SIDX[c["script"]]] = float(c[field])
        return v, inc

    def rate_bs(self, m, p, field, subset="scored"):
        v, inc = self.vec(m, p, field, subset)
        est = v.sum() / inc.sum() if inc.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            bs = (WT @ v) / (WT @ inc)
        return est, bs

    def lean_bs(self, m, p, meas, subset="scored"):
        f = FORMAL[m]; cz = OTHER[f]; pre = "j_" if meas == "judge" else "kw_"
        e1, b1 = self.rate_bs(m, p, pre + f, subset); e2, b2 = self.rate_bs(m, p, pre + cz, subset)
        return e1 - e2, b1 - b2


def cell_table(C, m, p, planned=200):
    X = C.cell.get((m, p), [])
    sc = [c for c in X if c["scored"]]; ir = [c for c in sc if c["inrole"]]
    d = dict(model=m, cell=p, planned=planned, completed=len(X), scored=len(sc), unscored=len(X) - len(sc), missing=planned - len(X),
             excluded_not_inrole=len(sc) - len(ir), story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc),
             role_break=sum(c["role_break"] for c in sc), valid=sum(c["valid"] for c in sc), inrole=len(ir),
             parse_retries=sum(max(0, c["attempts"] - 1) for c in X))
    f = FORMAL[m]; cz = OTHER[f]
    for sub, Y in (("scored", sc), ("inrole", ir)):
        for meas, pre in (("judge", "j_"), ("kw", "kw_")):
            for an in ("bee", "crow"):
                k = sum(c[pre + an] for c in Y)
                d[f"{meas}_{an}_{sub}"] = [k, len(Y), *wilson(k, len(Y))]
            d[f"{meas}_f_{sub}"] = d[f"{meas}_{f}_{sub}"]; d[f"{meas}_c_{sub}"] = d[f"{meas}_{cz}_{sub}"]
            d[f"a_{meas}_{sub}"] = ci(*C.lean_bs(m, p, meas, sub)) if X else None
    vt = (1, 3) if p.startswith("SW-") else (1, 4)
    for t in (1, 3, 4):
        vs = [c[f"v{t}"] for c in X if c[f"v{t}"] is not None]
        if t in vt:
            d[f"voice_t{t}"] = [float(np.mean(vs)) if vs else None, len(vs)]
    for t in (1, 3):
        ds = [c[f"d{t}"] for c in X if c[f"d{t}"] is not None]
        d[f"decline_t{t}"] = [sum(ds), len(ds), *wilson(sum(ds), len(ds))] if ds else None
    toks = [t for c in X for t in c["n_tok"]]
    d["reply_tokens_mean"] = float(np.mean(toks)) if toks else None
    d["reply_chars_mean"] = float(np.mean([x for c in X for x in c["chars"]])) if X else None
    d["cap_hits"] = sum(x == "length" for c in X for x in c["finish"])
    return d


def part_c(out, samples):
    files = sorted(glob.glob(f"{W}/results/rollouts/C*.jsonl"))
    files = [p for p in files if os.path.exists(p + ".done")]
    voice = label_map("voice", "conv|"); decline = label_map("decline", "conv|")
    convs = load_convs(files, jl(f"{W}/judgments/haiku.jsonl"), voice, decline)
    C = Cells(convs)
    o = dict(cells={}, contrasts={}, pairs={}, conflict={}, voice_gaps={}, agreement={}, parent={})
    for m, cells in PLAN.items():
        for p in cells:
            o["cells"][f"{m}|{p}"] = cell_table(C, m, p)
    # contrasts per model and pair
    for pair, (m1, m2) in PAIRS.items():
        for name, formula, terms, pairs in CONTRASTS:
            if pair not in pairs:
                continue
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    bss = []
                    for m in (m1, m2):
                        if not all(C.cell.get((m, p)) for p, _ in terms):
                            continue
                        est, bs = 0.0, np.zeros(len(WT))
                        for p, w in terms:
                            e, b = C.lean_bs(m, p, meas, sub); est += w * e; bs = bs + w * b
                        o["contrasts"][f"{m}|{name}|{meas}|{sub}"] = ci(est, bs); bss.append((est, bs))
                    if len(bss) == 2:
                        o["pairs"][f"{pair}|{name}|{meas}|{sub}"] = ci((bss[0][0] + bss[1][0]) / 2, (bss[0][1] + bss[1][1]) / 2)
        if pair in CONFLICT:
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    allc = []
                    for m in (m1, m2):
                        per = []
                        for p, sg in CONFLICT[pair]:
                            if not C.cell.get((m, p)):
                                continue
                            e, b = C.lean_bs(m, p, meas, sub)
                            o["conflict"][f"{m}|{p}|{meas}|{sub}"] = ci(sg * e, sg * b); per.append((sg * e, sg * b))
                        if len(per) == 2:
                            o["conflict"][f"{m}|mean2|{meas}|{sub}"] = ci((per[0][0] + per[1][0]) / 2, (per[0][1] + per[1][1]) / 2)
                        allc += per
                    if len(allc) == 4:
                        o["conflict"][f"{pair}|mean4|{meas}|{sub}"] = ci(sum(x[0] for x in allc) / 4, sum(x[1] for x in allc) / 4)
    # parent conflict cells with N's mapping (voice / behaviour of N's characters): P09 v-lean = f - c, P21 = c - f
    for p, sg in CONFLICT["N/NB"]:
        if C.cell.get(("parent", p)):
            for meas in ("judge", "kw"):
                e, b = C.lean_bs("parent", p, meas)
                o["conflict"][f"parent|{p}|{meas}|scored"] = ci(sg * e, sg * b)
    # voice gaps (bootstrap over the 100 voice-checked scripts)
    vs_ids = json.load(open(f"{W}/results/voice_sample_script_ids.json")) if os.path.exists(f"{W}/results/voice_sample_script_ids.json") else []
    vidx = {s: i for i, s in enumerate(vs_ids)}
    Wv = bmat(len(vs_ids)) if vs_ids else None

    def vvec(m, p, t):
        v = np.zeros(len(vs_ids)); inc = np.zeros(len(vs_ids))
        for c in C.cell.get((m, p), []):
            if c[f"v{t}"] is not None and c["script"] in vidx:
                v[vidx[c["script"]]] = c[f"v{t}"]; inc[vidx[c["script"]]] = 1
        return v, inc
    for m in PLAN:
        for arm, hi, lo, ts in (("P22-P23", "P22", "P23", (1, 4)), ("RP-F-RP-C", "RP-F", "RP-C", (1, 4)), ("SW-F-SW-C", "SW-F", "SW-C", (1, 3))):
            if Wv is None or not (C.cell.get((m, hi)) and C.cell.get((m, lo))):
                continue
            for t in ts:
                v1, i1 = vvec(m, hi, t); v2, i2 = vvec(m, lo, t)
                if not i1.sum() or not i2.sum():
                    continue
                est = v1.sum() / i1.sum() - v2.sum() / i2.sum()
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (Wv @ v1) / (Wv @ i1) - (Wv @ v2) / (Wv @ i2)
                o["voice_gaps"][f"{m}|{arm}|t{t}"] = ci(est, bs)
    for pair, (m1, m2) in PAIRS.items():
        for arm, t in (("P22-P23", 1), ("P22-P23", 4), ("RP-F-RP-C", 1), ("RP-F-RP-C", 4), ("SW-F-SW-C", 3), ("SW-F-SW-C", 1)):
            a_, b_ = o["voice_gaps"].get(f"{m1}|{arm}|t{t}"), o["voice_gaps"].get(f"{m2}|{arm}|t{t}")
            if a_ and b_:
                o["voice_gaps"][f"{pair}|{arm}|t{t}"] = [(a_[0] + b_[0]) / 2]
    # agreement
    sc = [c for c in convs if c["scored"]]
    for an in ("bee", "crow"):
        o["agreement"][an] = kappa([c[f"j_{an}"] for c in sc], [c[f"kw_{an}"] for c in sc])
    # samples
    rs = random.Random(0)
    for m, cells in PLAN.items():
        for p in cells:
            X = C.cell.get((m, p), [])
            if X:
                samples.append((f"{m} / {p}", rs.sample(X, min(10, len(X)))))
    out["partC"] = o
    return C


# ------------------------------------------------------------------------------------------------ R07 / R08 anchors
def anchors(out):
    o = {}
    r07 = load_convs(["/workspace/e08/r07/results/rollouts/G1_T07_Nfam_parent.jsonl", "/workspace/e08/r07/results/rollouts/G2_T07_Xfam.jsonl"],
                     jl("/workspace/e08/r07/judgments/haiku.jsonl"))
    r08 = load_convs(["/workspace/e08/r08/results/rollouts/A_T07.jsonl", "/workspace/e08/r08/results/rollouts/B_T07.jsonl"],
                     jl("/workspace/e08/r08/judgments/haiku.jsonl"))
    for tag, convs in (("R07", r07), ("R08", r08)):
        C = Cells(convs)
        for (m, p), X in C.cell.items():
            if m not in FORMAL:
                continue
            d = cell_table(C, m, p)
            o[f"{tag}|{m}|{p}"] = {k: d[k] for k in ("scored", "judge_f_scored", "judge_c_scored", "a_judge_scored", "kw_f_scored",
                                                    "kw_c_scored", "a_kw_scored")}
            # turn-3-only keyword rates (Part B comparison), all 200 scripts and the 160 main steering scripts
            for sub, keep in (("all", None), ("main160", set(main_scripts()))):
                Y = [c for c in X if keep is None or c["script"] in keep]
                f = FORMAL[m]; cz = OTHER[f]
                o[f"{tag}|{m}|{p}"][f"t3kw_{sub}"] = dict(n=len(Y), f=float(np.mean([c[f"kw3_{f}"] for c in Y])) if Y else None,
                                                          c=float(np.mean([c[f"kw3_{cz}"] for c in Y])) if Y else None)
    out["anchors"] = o
    return r07, r08


def main_scripts():
    cal = random.Random(0).sample(SORTED, 40)
    return [s for s in SORTED if s not in set(cal)]


# ------------------------------------------------------------------------------------------------ Part B
def part_b(out):
    o = dict(models={}, contrasts={}, calibration={})
    vo = label_map("voice", "steer|"); fl = label_map("fluency", "steer|"); de = label_map("decline", "steer|")
    ms = main_scripts(); midx = {s: i for i, s in enumerate(ms)}
    Wb = bmat(len(ms))
    if os.path.exists(f"{W}/results/steer/sstar.json"):
        o["calibration"] = json.load(open(f"{W}/results/steer/sstar.json"))
    for m in ("N", "V", "NB", "VB"):
        rows = jl(f"{W}/results/steer/main_{m}.jsonl")
        if not rows:
            continue
        f = FORMAL[m]; cz = OTHER[f]
        by = collections.defaultdict(dict)
        for r in rows:
            t = r["text"]
            by[r["cond"]][r["script_id"]] = dict(bee=bool(BEE.search(t)), crow=bool(CROW.search(t)), voice=vo.get(f"steer|{r['id']}"),
                                                 fluent=fl.get(f"steer|{r['id']}"), decline=de.get(f"steer|{r['id']}"), n_tok=r["n_tok"],
                                                 finish=r["finish"], s=r["s"], s_n32=r["s_n32"])
        tab = {}
        vec = {}
        for cond, d in by.items():
            n = len(d)
            fv = np.zeros(len(ms)); cv = np.zeros(len(ms)); inc = np.zeros(len(ms))
            for sid, x in d.items():
                i = midx[sid]; inc[i] = 1; fv[i] = x[f]; cv[i] = x[cz]
            vec[cond] = (fv, cv, inc)
            vs = [x["voice"] for x in d.values() if x["voice"] is not None]
            fls = [x["fluent"] for x in d.values() if x["fluent"] is not None]
            ds = [x["decline"] for x in d.values() if x["decline"] is not None]
            kf, kc = int(fv.sum()), int(cv.sum())
            tab[cond] = dict(n=n, f=[kf, n, *wilson(kf, n)], c=[kc, n, *wilson(kc, n)], a=(kf - kc) / n, fc=(kf + kc) / n,
                             bee=sum(x["bee"] for x in d.values()) / n, crow=sum(x["crow"] for x in d.values()) / n,
                             voice=[float(np.mean(vs)) if vs else None, len(vs)],
                             fluent=[sum(fls) / len(fls) if fls else None, len(fls)], decline=[sum(ds) / len(ds) if ds else None, len(ds)],
                             n_tok_mean=float(np.mean([x["n_tok"] for x in d.values()])), cap_hits=sum(x["finish"] == "length" for x in d.values()),
                             s=next(iter(d.values()))["s"], s_n32=next(iter(d.values()))["s_n32"])
        o["models"][m] = tab

        def bsr(cond, which):
            fv, cv, inc = vec[cond]
            v = fv - cv if which == "a" else fv + cv
            with np.errstate(invalid="ignore", divide="ignore"):
                return v.sum() / inc.sum(), (Wb @ v) / (Wb @ inc)
        con = {}
        for d_ in ("v_formal", "v_formal_perp", "v_axis", "v_axis_perp", "v_rand"):
            if f"+{d_}" in vec and f"-{d_}" in vec:
                e1, b1 = bsr(f"+{d_}", "a"); e2, b2 = bsr(f"-{d_}", "a")
                con[f"{d_}|which"] = ci(e1 - e2, b1 - b2)
                if "none" in vec:
                    e0, b0 = bsr("none", "fc")
                    for sg in "+-":
                        e, b = bsr(f"{sg}{d_}", "fc")
                        con[f"{d_}|often{sg}"] = ci(e - e0, b - b0)
        o["contrasts"][m] = con
    out["partB"] = o


# ------------------------------------------------------------------------------------------------ Part A
def part_a(out, r07, r08):
    import torch
    o = dict(directions={}, cell_means={}, auc_which={}, auc_which_pooled={}, auc_often={}, decline={}, n32=None)
    p = f"{W}/local/partA_acts.pt"
    if not os.path.exists(p) or not os.path.exists(f"{W}/results/directions.pt"):
        out["partA"] = o; return
    A = torch.load(p, weights_only=False); Dd = torch.load(f"{W}/results/directions.pt", weights_only=False)
    o["directions"] = json.load(open(f"{W}/results/directions.json")); o["n32"] = json.load(open(f"{W}/results/n32.json"))
    blocks = A["blocks"]; meta = A["meta"]
    U = Dd["unit32"]
    dirs_at = {b: [k.split("|")[1] for k in U if int(k.split("|")[0]) == b] for b in blocks}
    proj = {}  # (pos, block, dir) -> np array over conversations
    for pos in ("p1", "p2"):
        X = A[pos]  # [n, 3, D]
        for bi, b in enumerate(blocks):
            for d in dirs_at[b]:
                proj[(pos, b, d)] = (X[:, bi].float() @ U[f"{b}|{d}"].float()).numpy()
    # per-conversation projections
    with open(f"{W}/results/partA_projections_b32.jsonl", "w") as f32, open(f"{W}/results/partA_projections_b24_b40.jsonl", "w") as fo:
        for i, r in enumerate(meta):
            base = dict(cid=r["cid"], model=r["model"], persona=r["persona"], script_id=r["script_id"])
            f32.write(json.dumps(dict(base, **{f"{pos}|{d}": round(float(proj[(pos, 32, d)][i]), 4) for pos in ("p1", "p2") for d in dirs_at[32]})) + "\n")
            fo.write(json.dumps(dict(base, **{f"{pos}|{b}|{d}": round(float(proj[(pos, b, d)][i]), 4) for pos in ("p1", "p2")
                                              for b in blocks if b != 32 for d in dirs_at[b]})) + "\n")
    # judgments: (source file, key) -> conv dict
    jc = {f"{c['src']}|{c['key']}": c for c in r07 + r08}
    dec = label_map("decline", "partA|")
    groups = collections.defaultdict(list)
    for i, r in enumerate(meta):
        groups[(r["model"], cell_of(r["persona"]))].append(i)
    # 1. cell means (odd scripts and all scripts), bootstrap over scripts
    for (m, cell), ix in groups.items():
        for subset in ("odd", "all"):
            jx = [i for i in ix if subset == "all" or meta[i]["script_id"] in ODD]
            if not jx:
                continue
            Wc = bmat(len(jx))
            for (pos, b, d), v in proj.items():
                vals = v[jx]
                o["cell_means"][f"{m}|{cell}|{pos}|{b}|{d}|{subset}"] = ci(float(vals.mean()), (Wc @ vals) / len(jx))
    # 2-3. AUCs
    def conv_of(i):
        return jc.get(meta[i]["cid"])
    for m in ("N", "NB", "X", "XB", "V", "VB"):
        f = FORMAL[m]; cz = OTHER[f]
        pooled = collections.defaultdict(list)
        for (mm, cell), ix in groups.items():
            if mm != m:
                continue
            for subset in ("odd", "all"):
                jx = [i for i in ix if (subset == "all" or meta[i]["script_id"] in ODD) and conv_of(i) and conv_of(i)["scored"]]
                fi = [i for i in jx if conv_of(i)[f"j_{f}"] and not conv_of(i)[f"j_{cz}"]]
                ci_ = [i for i in jx if conv_of(i)[f"j_{cz}"] and not conv_of(i)[f"j_{f}"]]
                hab = [i for i in jx if conv_of(i)["j_bee"] or conv_of(i)["j_crow"]]
                nohab = [i for i in jx if not (conv_of(i)["j_bee"] or conv_of(i)["j_crow"])]
                for (pos, b, d), v in proj.items():
                    k = f"{m}|{cell}|{pos}|{b}|{d}|{subset}"
                    if cell == "P00":
                        o["auc_which"][k] = dict(auc=auc_ci(v[fi], v[ci_]), n_formal_animal=len(fi), n_casual_animal=len(ci_))
                        o["auc_often"][k] = dict(auc=auc_ci(v[hab], v[nohab]), n_habit=len(hab), n_none=len(nohab))
                    if len(fi) >= 5 and len(ci_) >= 5:
                        pooled[(pos, b, d, subset)].append((auc(v[fi], v[ci_]), len(fi) + len(ci_), cell))
                    elif (pos, b, d, subset) not in pooled:
                        pooled[(pos, b, d, subset)] = pooled.get((pos, b, d, subset), [])
        for (pos, b, d, subset), lst in pooled.items():
            if lst:
                o["auc_which_pooled"][f"{m}|{pos}|{b}|{d}|{subset}"] = dict(auc=float(sum(a_ * n for a_, n, _ in lst) / sum(n for _, n, _ in lst)),
                                                                            cells=[c for _, _, c in lst], n=sum(n for _, n, _ in lst))
            else:
                o["auc_which_pooled"][f"{m}|{pos}|{b}|{d}|{subset}"] = dict(auc=None, cells=[], n=0)
    # 4. decline mode (N, NB, X, XB defaults; turn-1 reply)
    for m in ("N", "NB", "X", "XB"):
        ix = groups.get((m, "P00"), [])
        lab = {i: dec.get(f"partA|{meta[i]['cid']}|t1") for i in ix}
        f = FORMAL[m]; cz = OTHER[f]
        for subset in ("odd", "all"):
            jx = [i for i in ix if (subset == "all" or meta[i]["script_id"] in ODD) and lab[i] is not None]
            dcl = [i for i in jx if lab[i]]; hlp = [i for i in jx if not lab[i]]
            for (pos, b, d), v in proj.items():
                if pos == "p2":
                    o["decline"][f"{m}|auc|{b}|{d}|{subset}"] = dict(auc=auc_ci(v[dcl], v[hlp]), n_declines=len(dcl), n_helps=len(hlp))
            if subset == "all":
                for mode, Y in (("declines", dcl), ("helps", hlp)):
                    Ys = [conv_of(i) for i in Y if conv_of(i) and conv_of(i)["scored"]]
                    kf = sum(c[f"j_{f}"] for c in Ys); kc = sum(c[f"j_{cz}"] for c in Ys)
                    kfk = sum(c[f"kw_{f}"] for c in Ys); kck = sum(c[f"kw_{cz}"] for c in Ys)
                    o["decline"][f"{m}|split|{mode}"] = dict(n=len(Ys), f=wilson(kf, len(Ys)), c=wilson(kc, len(Ys)), k_f=kf, k_c=kc,
                                                             f_kw=wilson(kfk, len(Ys)), c_kw=wilson(kck, len(Ys)))
                o["decline"][f"{m}|n_labelled"] = len(jx)
    out["partA"] = o


# ------------------------------------------------------------------------------------------------ Part D
def part_d(out, story_samples):
    o = dict(cells={}, contrasts={})
    rows = []
    for p in sorted(glob.glob(f"{W}/results/stories/*.jsonl")):
        if os.path.exists(p + ".done"):
            rows += jl(p)
    lab = label_map("story", "story|")
    pairs = json.load(open(f"{W}/data/story_pairs.json"))["pairs"]
    Wp = bmat(len(pairs))
    by = collections.defaultdict(dict)
    for r in rows:
        L = lab.get(f"story|{r['id']}")
        by[(r["model"], r["cell"])][r["pair"]] = dict(r=r, lab=L, kw_bee=bool(BEE.search(r["text"])), kw_crow=bool(CROW.search(r["text"])))
    vecs = {}
    for (m, cell), d in by.items():
        f = FORMAL[m]; cz = OTHER[f]
        lab_ok = {i: x for i, x in d.items() if x["lab"] is not None}
        pro = {i: x for i, x in lab_ok.items() if x["lab"]["prohibition"]}
        def has(x, an):
            return x["lab"]["after"] in (an + "s", "both")
        n = len(pro)
        res = dict(model=m, cell=cell, stories=len(d), labelled=len(lab_ok), prohibition=[n, len(lab_ok), *wilson(n, len(lab_ok))],
                   cap_hits=sum(x["r"]["finish"] == "length" for x in d.values()),
                   n_tok_mean=float(np.mean([x["r"]["n_tok"] for x in d.values()])))
        for an in ("bee", "crow"):
            k = sum(has(x, an) for x in pro.values()); res[f"after_{an}"] = [k, n, *wilson(k, n)]
            k2 = sum(x[f"kw_{an}"] for x in pro.values()); res[f"kw_{an}_prohib"] = [k2, n, *wilson(k2, n)]
            k3 = sum(x[f"kw_{an}"] for x in d.values()); res[f"kw_{an}_all"] = [k3, len(d), *wilson(k3, len(d))]
        res["f"] = res[f"after_{f}"]; res["c"] = res[f"after_{cz}"]; res["f_kw"] = res[f"kw_{f}_prohib"]; res["c_kw"] = res[f"kw_{cz}_prohib"]
        # vectors over pairs for the bootstrap (over stories with a prohibition)
        for meas in ("judge", "kw"):
            fv = np.zeros(len(pairs)); cv = np.zeros(len(pairs)); inc = np.zeros(len(pairs))
            for i, x in pro.items():
                inc[i] = 1
                fv[i] = has(x, f) if meas == "judge" else x[f"kw_{f}"]
                cv[i] = has(x, cz) if meas == "judge" else x[f"kw_{cz}"]
            vecs[(m, cell, meas)] = (fv, cv, inc)
            with np.errstate(invalid="ignore", divide="ignore"):
                res[f"a_{meas}"] = ci((fv - cv).sum() / inc.sum() if inc.sum() else float("nan"), (Wp @ (fv - cv)) / (Wp @ inc))
        o["cells"][f"{m}|{cell}"] = res
    for m in ("N", "NB", "V", "VB", "parent"):
        for name, hi, lo in (("character_voice", "ST-CF", "ST-CC"), ("narration_voice", "ST-NF", "ST-NC")):
            for meas in ("judge", "kw"):
                if (m, hi, meas) in vecs and (m, lo, meas) in vecs:
                    f1, c1, i1 = vecs[(m, hi, meas)]; f2, c2, i2 = vecs[(m, lo, meas)]
                    with np.errstate(invalid="ignore", divide="ignore"):
                        est = (f1 - c1).sum() / i1.sum() - (f2 - c2).sum() / i2.sum()
                        bs = (Wp @ (f1 - c1)) / (Wp @ i1) - (Wp @ (f2 - c2)) / (Wp @ i2)
                    o["contrasts"][f"{m}|{name}|{meas}"] = ci(est, bs)
                    o["contrasts"][f"{m}|{name}|{meas}|_bs"] = None
                    vecs[("bs", m, name, meas)] = (est, bs)
    for pair, (m1, m2) in (("N/NB", ("N", "NB")), ("V/VB", ("V", "VB"))):
        for name in ("character_voice", "narration_voice"):
            for meas in ("judge", "kw"):
                a_, b_ = vecs.get(("bs", m1, name, meas)), vecs.get(("bs", m2, name, meas))
                if a_ and b_:
                    o["contrasts"][f"{pair}|{name}|{meas}"] = ci((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
    o["contrasts"] = {k: v for k, v in o["contrasts"].items() if not k.endswith("_bs")}
    rs = random.Random(0)
    for (m, cell) in sorted(by):
        xs = [x["r"] for _, x in sorted(by[(m, cell)].items())]
        story_samples.append((f"{m} / {cell}", rs.sample(xs, min(5, len(xs)))))
    out["partD"] = o


def write_samples(samples, story_samples):
    with open(f"{W}/results/samples.md", "w") as f:
        f.write("# E08 R09 samples\n\n10 random conversations per model and cell (`random.Random(0)`), then 5 stories per model and story cell.\n\n")
        for title, X in samples:
            f.write(f"## {title}\n\n")
            for c in X:
                r = c["r"]
                f.write(f"### {r['key']}\n\njudge: bee {c.get('j_bee')}, crow {c.get('j_crow')}; keyword bee {c['kw_bee']}, crow {c['kw_crow']}\n\n")
                for mm in r["messages"]:
                    f.write(f"**{mm['role']}:** {mm['content']}\n\n")
        f.write("# Stories\n\n")
        for title, X in story_samples:
            f.write(f"## {title}\n\n")
            for r in X:
                f.write(f"### {r['id']} ({r['A']} asks, {r['B']} helps)\n\n**user:** {r['user']}\n\n{r['text']}\n\n")


def main():
    out = {}
    samples, story_samples = [], []
    part_c(out, samples)
    r07, r08 = anchors(out)
    part_b(out)
    if "--no_a" not in sys.argv:
        part_a(out, r07, r08)
    part_d(out, story_samples)
    write_samples(samples, story_samples)
    json.dump(out, open(f"{W}/results/summary.json", "w"), indent=0, default=float)
    print("summary written:", {k: len(v) if hasattr(v, "__len__") else v for k, v in out.items()})


if __name__ == "__main__":
    main()
