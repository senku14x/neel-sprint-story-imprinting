"""E08 R10 analysis (numbers only). Writes results/summary.json (everything), results/partA_projections_b32.jsonl and
results/partA_projections_b24_b40.jsonl (per conversation), results/partB_replies_labelled.jsonl, results/samples.md.
Built on R09's analyze_r09.py (labels, Wilson, kappa, AUC, the shared bootstrap matrix per script set).

Conversations (Part C): habit = Haiku judge score >= 5; story form = coherence < 7; garbled = fluency < 6.5; role break = any reply
flagged; valid = none of the three; in-role = no role break in replies 1-2 (R07's labels, as R09); keyword = R04's regexes on
assistant turns 3-5 (turn-3 reply alone for Part B's natural reference). S / SB: h = helper's animal (S bees, SB crows), v =
rival's (dismissive's) animal, a = h - v. V / VB: f = formal's animal (V crows, VB bees), c = casual's, a = f - c.
flip(cell) = a(default) - a(cell). Bootstrap: 2,000 resamples of the scripts (sorted ids), seed 0, one matrix per script set
(200 for S / SB, the 100 heldout2 scripts for V / VB, the first 50 heldout2 scripts for parent); pair values = the mean of the
two models' values under the same resample.
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np
import torch

W = "/workspace/e08/r10"
RES = f"{W}/results"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
RX = {"bee": BEE, "crow": CROW}
FIRST = {"S": "bee", "SB": "crow", "V": "crow", "VB": "bee", "parent": "bee"}  # h (S/SB) or f (V/VB)
OTHER = {"bee": "crow", "crow": "bee"}
PAIRS = {"S/SB": ("S", "SB"), "V/VB": ("V", "VB")}
C1 = ["default", "dismissive", "P22", "P23", "P09", "P06", "P07", "P21"]
C2 = ["RP-F", "RP-C", "SW-F", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
C3 = ["default", "P23", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
C4 = ["dismissive", "P23", "RP-C", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
PLAN = {"S": C1 + C2, "SB": C1 + C2, "V": C3, "VB": C3, "parent": C4}
NON2x2 = [c for c in C1 + C2 if c not in ("P09", "P06", "P07", "P21")]
TEAM = {"S": {"default": (0.16, 0.01), "dismissive": (0.105, 0.47)}, "SB": {"default": (0.15, 0.0), "dismissive": (0.12, 0.525)}}


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


def ratio_ci(num_e, num_b, den_e, den_b):
    """per-resample ratio; undefined (den 0) resamples counted and dropped."""
    num_b, den_b = np.asarray(num_b, float), np.asarray(den_b, float)
    und = int(np.sum(den_b == 0))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(den_b == 0, np.nan, num_b / den_b)
    est = num_e / den_e if den_e != 0 else float("nan")
    return ci(est, r) + [und]


def bmat(n, seed=0, B=2000):
    rng = np.random.default_rng(seed)
    return np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B)]).astype(float)


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort"); ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    vals, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=ranks); ranks = (sums / cnt)[inv]
    r1 = ranks[: len(pos)].sum()
    return float((r1 - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


ALL_IDS = sorted({json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")})
H2 = [json.loads(l)["script_id"] for l in open(f"{W}/src/eval_data/scripts_heldout2.jsonl")]
SETS = {"all": ALL_IDS, "h2": sorted(H2), "h2first50": sorted(H2[:50])}
SET_OF = {"S": "all", "SB": "all", "V": "h2", "VB": "h2", "parent": "h2first50"}
SIDX = {k: {s: i for i, s in enumerate(v)} for k, v in SETS.items()}
WT = {k: bmat(len(v)) for k, v in SETS.items()}
EVEN = {s for i, s in enumerate(ALL_IDS) if i % 2 == 0}
ODD = {s for i, s in enumerate(ALL_IDS) if i % 2 == 1}


def label_map(kind, prefix=None, files=None):
    out = {}
    for p in files or [f"{W}/judgments/labels_{kind}.jsonl"]:
        for r in jl(p):
            if r.get("value") is not None and (prefix is None or r["item"].startswith(prefix)):
                out[r["item"]] = r["value"]
    return out


# ------------------------------------------------------------------------------------------------ conversations
def load_convs(files, judge_rows, voice=None, decline=None):
    J, att = {}, collections.Counter()
    for j in judge_rows:
        att[j["key"]] += 1
        if not j.get("error"):
            J[j["key"]] = j
    convs = []
    for p in files:
        src = os.path.basename(p)[:-6]
        for r in jl(p):
            asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            k = r["key"]
            c = dict(key=k, src=src, model=r["model"], cell=r["persona"], script=r["script_id"], n_replies=len(asst),
                     n_tok=r.get("n_tok", []), finish=r.get("finish", []), chars=[len(x) for x in asst],
                     kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                     kw3_bee=bool(BEE.search(asst[2])) if len(asst) > 2 else False,
                     kw3_crow=bool(CROW.search(asst[2])) if len(asst) > 2 else False, attempts=att.get(k, 0), r=r)
            j = J.get(k)
            c["scored"] = j is not None and len(asst) == 5
            if c["scored"]:
                rb = j["role_break_replies"]
                c.update(j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                         garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb),
                         jscores=dict(bee=j["bee_steering"], crow=j["crow_steering"], coh=j["chat_form_coherence"], flu=j["fluency"], rb=rb))
                c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
            for t in (1, 3, 4):
                c[f"v{t}"] = (voice or {}).get(f"conv|{k}|t{t}")
            for t in (1, 3):
                c[f"d{t}"] = (decline or {}).get(f"conv|{k}|t{t}")
            convs.append(c)
    return convs


class Cells:
    def __init__(self, convs):
        self.cell = collections.defaultdict(list)
        for c in convs:
            self.cell[(c["model"], c["cell"])].append(c)

    def vec(self, m, p, field, subset="scored"):
        S = SIDX[SET_OF[m]]
        v = np.zeros(len(S)); inc = np.zeros(len(S))
        for c in self.cell.get((m, p), []):
            if not c["scored"] or (subset == "inrole" and not c["inrole"]) or c["script"] not in S:
                continue
            inc[S[c["script"]]] = 1; v[S[c["script"]]] = float(c[field])
        return v, inc

    def rate_bs(self, m, p, field, subset="scored"):
        v, inc = self.vec(m, p, field, subset)
        est = v.sum() / inc.sum() if inc.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            bs = (WT[SET_OF[m]] @ v) / (WT[SET_OF[m]] @ inc)
        return est, bs

    def lean_bs(self, m, p, meas, subset="scored"):
        f = FIRST[m]; cz = OTHER[f]; pre = "j_" if meas == "judge" else "kw_"
        e1, b1 = self.rate_bs(m, p, pre + f, subset); e2, b2 = self.rate_bs(m, p, pre + cz, subset)
        return e1 - e2, b1 - b2

    def combo(self, m, terms, meas, subset="scored"):
        """sum of w * a(cell) over terms [(cell, w)]; None if a cell is missing."""
        if not all(self.cell.get((m, p)) for p, _ in terms):
            return None
        est, bs = 0.0, np.zeros(len(WT[SET_OF[m]]))
        for p, w in terms:
            e, b = self.lean_bs(m, p, meas, subset); est += w * e; bs = bs + w * b
        return est, bs


def flip_terms(cell):
    return [("default", 1), (cell, -1)]


def contrasts_for(pair):
    """name -> (formula, terms)."""
    out = {}
    cells = C1 + C2 if pair == "S/SB" else C3
    for c in cells:
        if c != "default":
            out[f"flip|{c}"] = (f"a(default) - a({c})", flip_terms(c))
    if pair == "S/SB":
        out["casual_cue_flip"] = ("mean of flip(P23), flip(RP-C), flip(SW-C)", [("default", 1), ("P23", -1 / 3), ("RP-C", -1 / 3), ("SW-C", -1 / 3)])
        out["formal_cue_flip"] = ("mean of flip(P22), flip(RP-F), flip(SW-F)", [("default", 1), ("P22", -1 / 3), ("RP-F", -1 / 3), ("SW-F", -1 / 3)])
        out["style"] = ("a(P22) - a(P23)", [("P22", 1), ("P23", -1)])
        out["roleplay"] = ("a(RP-F) - a(RP-C)", [("RP-F", 1), ("RP-C", -1)])
        out["switch"] = ("a(SW-F) - a(SW-C)", [("SW-F", 1), ("SW-C", -1)])
        out["roleplay_minus_style"] = ("(a(RP-F) - a(RP-C)) - (a(P22) - a(P23))", [("RP-F", 1), ("RP-C", -1), ("P22", -1), ("P23", 1)])
        out["voice_effect"] = ("1/2[(a(P09) - a(P07)) + (a(P06) - a(P21))]", [("P09", .5), ("P07", -.5), ("P06", .5), ("P21", -.5)])
        out["behaviour_effect"] = ("1/2[(a(P09) - a(P06)) + (a(P07) - a(P21))]", [("P09", .5), ("P06", -.5), ("P07", .5), ("P21", -.5)])
        out["interaction_2x2"] = ("(a(P09) - a(P07)) - (a(P06) - a(P21))", [("P09", 1), ("P07", -1), ("P06", -1), ("P21", 1)])
        out["voice_minus_behaviour"] = ("voice effect - behaviour effect (= a(P06) - a(P07))", [("P06", 1), ("P07", -1)])
    # text x channel and "friend" wording (both pairs); flip(x) - flip(y) = a(y) - a(x)
    out["text_effect"] = ("1/2[(flip(SW-C) - flip(SW-P23)) + (flip(SYS-C) - flip(P23))]",
                          [("SW-P23", .5), ("SW-C", -.5), ("P23", .5), ("SYS-C", -.5)])
    out["channel_effect"] = ("1/2[(flip(SW-P23) - flip(P23)) + (flip(SW-C) - flip(SYS-C))]",
                             [("P23", .5), ("SW-P23", -.5), ("SYS-C", .5), ("SW-C", -.5)])
    out["text_x_channel"] = ("(flip(SW-C) - flip(SW-P23)) - (flip(SYS-C) - flip(P23))",
                             [("SW-P23", 1), ("SW-C", -1), ("P23", -1), ("SYS-C", 1)])
    out["friend_SWC_minus_SWCV"] = ("flip(SW-C) - flip(SW-CV)", [("SW-CV", 1), ("SW-C", -1)])
    out["friend_SWC_minus_SWFR"] = ("flip(SW-C) - flip(SW-FR)", [("SW-FR", 1), ("SW-C", -1)])
    return out


def cell_table(C, m, p):
    planned = len(SETS[SET_OF[m]])
    X = C.cell.get((m, p), [])
    sc = [c for c in X if c["scored"]]; ir = [c for c in sc if c["inrole"]]
    d = dict(model=m, cell=p, planned=planned, completed=len(X), scored=len(sc), unscored=len(X) - len(sc), missing=planned - len(X),
             excluded_not_inrole=len(sc) - len(ir), story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc),
             role_break=sum(c["role_break"] for c in sc), valid=sum(c["valid"] for c in sc), inrole=len(ir),
             parse_retries=sum(max(0, c["attempts"] - 1) for c in X))
    f = FIRST[m]; cz = OTHER[f]
    for sub, Y in (("scored", sc), ("inrole", ir)):
        for meas, pre in (("judge", "j_"), ("kw", "kw_")):
            for an in ("bee", "crow"):
                k = sum(c[pre + an] for c in Y)
                d[f"{meas}_{an}_{sub}"] = [k, len(Y), *wilson(k, len(Y))]
            d[f"{meas}_first_{sub}"] = d[f"{meas}_{f}_{sub}"]; d[f"{meas}_second_{sub}"] = d[f"{meas}_{cz}_{sub}"]
            d[f"a_{meas}_{sub}"] = ci(*C.lean_bs(m, p, meas, sub)) if sc else None
    vt = (1, 3) if p.startswith("SW-") else (1, 3, 4) if p == "default" else (1, 4)
    for t in vt:
        vs = [c[f"v{t}"] for c in X if c[f"v{t}"] is not None]
        d[f"voice_t{t}"] = [float(np.mean(vs)) if vs else None, len(vs)]
    for t in (1, 3):
        ds = [c[f"d{t}"] for c in X if c[f"d{t}"] is not None]
        d[f"decline_t{t}"] = [sum(ds), len(ds), *wilson(sum(ds), len(ds))] if ds else None
    toks = [t for c in X for t in c["n_tok"]]
    d["reply_tokens_mean"] = float(np.mean(toks)) if toks else None
    d["reply_chars_mean"] = float(np.mean([x for c in X for x in c["chars"]])) if X else None
    d["cap_hits"] = sum(x == "length" for c in X for x in c["finish"])
    d["n_replies_ok"] = sum(c["n_replies"] == 5 for c in X)
    return d


def part_c(out, samples):
    files = [p for p in sorted(glob.glob(f"{RES}/rollouts/C*.jsonl")) if os.path.exists(p + ".done")]
    voice = label_map("voice", "conv|"); decline = label_map("decline", "conv|")
    convs = load_convs(files, jl(f"{W}/judgments/haiku.jsonl"), voice, decline)
    C = Cells(convs)
    o = dict(cells={}, contrasts={}, pairs={}, shares={}, voice_gaps={}, agreement={}, parent={}, checks={}, anchors={})
    for m, cells in PLAN.items():
        for p in cells:
            if C.cell.get((m, p)):
                o["cells"][f"{m}|{p}"] = cell_table(C, m, p)
    for pair, (m1, m2) in PAIRS.items():
        for name, (formula, terms) in contrasts_for(pair).items():
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    bss = []
                    for m in (m1, m2):
                        r = C.combo(m, terms, meas, sub)
                        if r is None:
                            continue
                        o["contrasts"][f"{m}|{name}|{meas}|{sub}"] = ci(*r); bss.append(r)
                    if len(bss) == 2:
                        o["pairs"][f"{pair}|{name}|{meas}|{sub}"] = ci((bss[0][0] + bss[1][0]) / 2, (bss[0][1] + bss[1][1]) / 2)
            o["contrasts"][f"formula|{name}"] = formula
        # shares of the dismissive flip (S/SB)
        if pair == "S/SB":
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    den = {m: C.combo(m, flip_terms("dismissive"), meas, sub) for m in (m1, m2)}
                    for name, (formula, terms) in contrasts_for(pair).items():
                        if not (name.startswith("flip|") or name.endswith("cue_flip")):
                            continue
                        nums = {m: C.combo(m, terms, meas, sub) for m in (m1, m2)}
                        for m in (m1, m2):
                            if nums[m] and den[m]:
                                o["shares"][f"{m}|{name}|{meas}|{sub}"] = ratio_ci(nums[m][0], nums[m][1], den[m][0], den[m][1])
                        if all(nums.values()) and all(den.values()):
                            ne = (nums[m1][0] + nums[m2][0]) / 2; nb = (nums[m1][1] + nums[m2][1]) / 2
                            de = (den[m1][0] + den[m2][0]) / 2; db = (den[m1][1] + den[m2][1]) / 2
                            o["shares"][f"{pair}|{name}|{meas}|{sub}"] = ratio_ci(ne, nb, de, db)
    # voice gaps: voice(default) - voice(cell); SW cells at turn 3, others at turns 1 and 4 (bootstrap over voice-checked scripts)
    vs_ids = json.load(open(f"{RES}/voice_sample_script_ids.json")) if os.path.exists(f"{RES}/voice_sample_script_ids.json") else []
    vsets = {"all": sorted(vs_ids), "h2": SETS["h2"], "h2first50": SETS["h2first50"]}
    vW = {k: bmat(len(v)) for k, v in vsets.items() if v}

    def vvec(m, p, t):
        ids = vsets[SET_OF[m]]; ix = {s: i for i, s in enumerate(ids)}
        v = np.zeros(len(ids)); inc = np.zeros(len(ids))
        for c in C.cell.get((m, p), []):
            if c[f"v{t}"] is not None and c["script"] in ix:
                v[ix[c["script"]]] = c[f"v{t}"]; inc[ix[c["script"]]] = 1
        return v, inc
    vg_bs = {}
    for m, cells in PLAN.items():
        if m == "parent" or SET_OF[m] not in vW:
            continue
        Wv = vW[SET_OF[m]]
        for p in cells:
            if p == "default" or not C.cell.get((m, p)):
                continue
            for t in ((3,) if p.startswith("SW-") else (1, 4)):
                v1, i1 = vvec(m, "default", t); v2, i2 = vvec(m, p, t)
                if not i1.sum() or not i2.sum():
                    continue
                est = v1.sum() / i1.sum() - v2.sum() / i2.sum()
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (Wv @ v1) / (Wv @ i1) - (Wv @ v2) / (Wv @ i2)
                o["voice_gaps"][f"{m}|{p}|t{t}"] = ci(est, bs) + [int(i2.sum())]; vg_bs[(m, p, t)] = (est, bs)
    for pair, (m1, m2) in PAIRS.items():
        for (m, p, t), (e, b) in list(vg_bs.items()):
            if m == m1 and (m2, p, t) in vg_bs:
                e2, b2 = vg_bs[(m2, p, t)]
                o["voice_gaps"][f"{pair}|{p}|t{t}"] = ci((e + e2) / 2, (b + b2) / 2)
    o["checks"]["voice_gap_below_0.5"] = sorted(k for k, v in o["voice_gaps"].items() if v[0] < 0.5)
    # setup checks
    o["checks"]["cells_over_10pct_missing_or_unscored"] = sorted(k for k, d in o["cells"].items()
                                                                 if (d["missing"] + d["unscored"]) > 0.1 * d["planned"])
    flags = []
    for m in ("S", "SB"):
        for p, (te_h, te_v) in TEAM[m].items():
            d = o["cells"].get(f"{m}|{p}")
            if not d:
                continue
            for meas in ("judge", "kw"):
                h = d[f"{meas}_first_scored"][2]; v = d[f"{meas}_second_scored"][2]
                o["anchors"][f"{m}|{p}|{meas}"] = dict(h=h, v=v, teammate_h=te_h, teammate_v=te_v,
                                                       flag_h=abs(h - te_h) > 0.10, flag_v=abs(v - te_v) > 0.10)
                if abs(h - te_h) > 0.10 or abs(v - te_v) > 0.10:
                    flags.append(f"{m}|{p}|{meas}")
    o["checks"]["anchor_flags"] = flags
    dec = []
    for m in ("S", "SB"):
        for p in ("P09", "P07"):
            d = o["cells"].get(f"{m}|{p}")
            if d and d["decline_t1"] and d["decline_t1"][2] > 0.30:
                dec.append(f"{m}|{p} (always helps) declines at turn 1 in {100 * d['decline_t1'][2]:.1f}%")
        for p in ("P06", "P21"):
            d = o["cells"].get(f"{m}|{p}")
            if d and d["decline_t1"] and d["decline_t1"][2] < 0.70:
                dec.append(f"{m}|{p} (never helps) declines at turn 1 in only {100 * d['decline_t1'][2]:.1f}%")
    o["checks"]["persona_2x2_decline_flags"] = dec
    par = []
    for p in C4:
        d = o["cells"].get(f"parent|{p}")
        if not d:
            continue
        o["parent"][p] = {k: d[k] for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored", "scored")}
        for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored"):
            if d[k][2] > 0.02:
                par.append(f"parent|{p}|{k} = {100 * d[k][2]:.1f}%")
    o["checks"]["parent_over_2pct"] = par
    sc = [c for c in convs if c["scored"]]
    for an in ("bee", "crow"):
        o["agreement"][an] = kappa([c[f"j_{an}"] for c in sc], [c[f"kw_{an}"] for c in sc])
    # R09's V / VB numbers for default (P00), P23, SW-C
    try:
        r9 = json.load(open("/workspace/e08/r09/results/summary.json"))["partC"]["cells"]
        o["r09_VVB"] = {f"{m}|{p}": {k: r9[f"{m}|{p}"][k] for k in ("judge_f_scored", "judge_c_scored", "a_judge_scored", "kw_f_scored",
                                                                     "kw_c_scored", "a_kw_scored")}
                        for m in ("V", "VB") for p in ("P00", "P23", "SW-C")}
    except Exception as e:  # noqa: BLE001
        o["r09_VVB"] = f"unavailable: {e!r}"
    rs = random.Random(0)
    for m, cells in PLAN.items():
        for p in cells:
            X = C.cell.get((m, p), [])
            if X:
                samples.append((f"{m} / {p}", rs.sample(X, min(6, len(X)))))
    out["partC"] = o
    return C


# ------------------------------------------------------------------------------------------------ Part B
def part_b(out, C, samples):
    o = dict(models={}, pairs={})
    ST = f"{RES}/steer"
    split = json.load(open(f"{ST}/script_split.json")) if os.path.exists(f"{ST}/script_split.json") else None
    if split is None:
        out["partB"] = "not run"; return
    main = sorted(split["main"]); mix = {s: i for i, s in enumerate(main)}
    Wm = bmat(len(main))
    voice = label_map("voice", "steer|"); dec = label_map("decline", "steer|")
    flu = label_map("fluency", "steer|", files=[f"{W}/judgments/labels_fluency.jsonl", f"{W}/judgments/labels_fluency_rt.jsonl"])
    vec = json.load(open(f"{ST}/vectors.json")) if os.path.exists(f"{ST}/vectors.json") else {}
    n32 = json.load(open("/workspace/e08/r09/results/n32.json"))["n32"]
    labelled = []
    per_model_bs = {}
    for M in ("S", "SB"):
        h_an, v_an = FIRST[M], OTHER[FIRST[M]]
        d = dict(vectors=vec.get(M), n32=n32)
        pk = f"{ST}/pick_{M}.json"
        if os.path.exists(pk):
            d["calibration"] = json.load(open(pk))
        rows = jl(f"{ST}/main_{M}.jsonl")
        if not rows:
            o["models"][M] = d; continue
        by = collections.defaultdict(dict)
        for r in rows:
            it = f"steer|{r['id']}"
            r2 = dict(r, h=bool(RX[h_an].search(r["text"])), v=bool(RX[v_an].search(r["text"])), voice=voice.get(it), fluent=flu.get(it),
                      declines=dec.get(it), chars=len(r["text"]))
            by[r["cond"]][r["script_id"]] = r2
            labelled.append(r2)
        tab = {}
        for c, X in by.items():
            Y = list(X.values()); n = len(Y)
            vs = [y["voice"] for y in Y if y["voice"] is not None]; fl = [y["fluent"] for y in Y if y["fluent"] is not None]
            de = [y["declines"] for y in Y if y["declines"] is not None]
            hh = sum(y["h"] for y in Y); vv = sum(y["v"] for y in Y)
            tab[c] = dict(n=n, h=[hh, n, *wilson(hh, n)], v=[vv, n, *wilson(vv, n)], a=(hh - vv) / n if n else None,
                          hv=(hh + vv) / n if n else None, voice=[float(np.mean(vs)) if vs else None, len(vs)],
                          fluent=[float(np.mean(fl)) if fl else None, len(fl)], declines=[float(np.mean(de)) if de else None, len(de)],
                          tokens_mean=float(np.mean([y["n_tok"] for y in Y])), chars_mean=float(np.mean([y["chars"] for y in Y])),
                          cap_hits=sum(y["finish"] == "length" for y in Y))
        d["conditions"] = tab

        def arr(c, field):
            v = np.zeros(len(main)); inc = np.zeros(len(main))
            for s, y in by.get(c, {}).items():
                if s in mix:
                    v[mix[s]] = float(y["h"]) - float(y["v"]) if field == "a" else float(y[field]); inc[mix[s]] = 1
            return v, inc

        def mean_bs(c, field):
            v, inc = arr(c, field)
            est = v.sum() / inc.sum() if inc.sum() else float("nan")
            with np.errstate(invalid="ignore", divide="ignore"):
                return est, (Wm @ v) / (Wm @ inc)
        bsd = {}
        u_e, u_b = mean_bs("def:none", "a"); uv_e, uv_b = mean_bs("def:none", "v")
        for x in ("D", "D_f", "D_h", "D_r", "P", "R"):
            if f"def:+{x}" in by:
                e, b = mean_bs(f"def:+{x}", "a"); ve, vb = mean_bs(f"def:+{x}", "v")
                bsd[f"E|{x}"] = (u_e - e, u_b - b); bsd[f"dv|{x}"] = (ve - uv_e, vb - uv_b)
        if "dis:none" in by:
            r_e, r_b = mean_bs("dis:none", "a")
            for x in ("D", "D_f", "D_h", "D_r", "R"):
                if f"dis:-{x}" in by:
                    e, b = mean_bs(f"dis:-{x}", "a")
                    bsd[f"Rm|{x}"] = (e - r_e, b - r_b)
        # natural reference: a(default) - a(dismissive) on the turn-3 reply alone (keywords, Part C, the same 140 scripts)
        if C is not None:
            def t3(cell):
                v = np.zeros(len(main)); inc = np.zeros(len(main))
                for cc in C.cell.get((M, cell), []):
                    if cc["script"] in mix:
                        v[mix[cc["script"]]] = float(cc[f"kw3_{h_an}"]) - float(cc[f"kw3_{v_an}"]); inc[mix[cc["script"]]] = 1
                est = v.sum() / inc.sum() if inc.sum() else float("nan")
                with np.errstate(invalid="ignore", divide="ignore"):
                    return est, (Wm @ v) / (Wm @ inc)
            de_, db_ = t3("default"); ds_, dsb_ = t3("dismissive")
            bsd["Nat"] = (de_ - ds_, db_ - dsb_)
            chk = {}
            for cell, cond in (("default", "def:none"), ("dismissive", "dis:none")):
                Y = [cc for cc in C.cell.get((M, cell), []) if cc["script"] in mix]
                chk[cell] = dict(partC_t3_h=float(np.mean([cc[f"kw3_{h_an}"] for cc in Y])) if Y else None,
                                 partC_t3_v=float(np.mean([cc[f"kw3_{v_an}"] for cc in Y])) if Y else None, n=len(Y),
                                 partB_unsteered_h=tab.get(cond, {}).get("h", [None] * 3)[2],
                                 partB_unsteered_v=tab.get(cond, {}).get("v", [None] * 3)[2])
            d["unsteered_vs_partC_t3"] = chk
        d["effects"] = {k: ci(*v) for k, v in bsd.items()}
        sh = {}
        for kind in ("E", "Rm"):
            if f"{kind}|D" in bsd:
                for x in ("D_f", "D_h", "D_r"):
                    if f"{kind}|{x}" in bsd:
                        sh[f"{kind}|{x}/{kind}|D"] = ratio_ci(bsd[f"{kind}|{x}"][0], bsd[f"{kind}|{x}"][1], bsd[f"{kind}|D"][0], bsd[f"{kind}|D"][1])
                if "Nat" in bsd:
                    sh[f"{kind}|D/Nat"] = ratio_ci(bsd[f"{kind}|D"][0], bsd[f"{kind}|D"][1], bsd["Nat"][0], bsd["Nat"][1])
                if all(f"{kind}|{x}" in bsd for x in ("D_f", "D_h", "D_r")):
                    se = sum(bsd[f"{kind}|{x}"][0] for x in ("D_f", "D_h", "D_r")); sb = sum(bsd[f"{kind}|{x}"][1] for x in ("D_f", "D_h", "D_r"))
                    sh[f"{kind}|sum_of_parts"] = ci(se, sb)
                    sh[f"{kind}|sum_of_parts_minus_D"] = ci(se - bsd[f"{kind}|D"][0], sb - bsd[f"{kind}|D"][1])
        d["shares"] = sh
        per_model_bs[M] = bsd
        o["models"][M] = d
        rs = random.Random(0)
        for c in sorted(by):
            Y = list(by[c].values())
            samples.append((f"Part B {M} / {c}", rs.sample(Y, min(5, len(Y)))))
    if len(per_model_bs) == 2:
        a_, b_ = per_model_bs["S"], per_model_bs["SB"]
        for k in a_:
            if k in b_:
                o["pairs"][k] = ci((a_[k][0] + b_[k][0]) / 2, (a_[k][1] + b_[k][1]) / 2)
        for kind in ("E", "Rm"):
            if f"{kind}|D" in a_ and f"{kind}|D" in b_:
                den = ((a_[f"{kind}|D"][0] + b_[f"{kind}|D"][0]) / 2, (a_[f"{kind}|D"][1] + b_[f"{kind}|D"][1]) / 2)
                for x in ("D_f", "D_h", "D_r"):
                    if f"{kind}|{x}" in a_ and f"{kind}|{x}" in b_:
                        num = ((a_[f"{kind}|{x}"][0] + b_[f"{kind}|{x}"][0]) / 2, (a_[f"{kind}|{x}"][1] + b_[f"{kind}|{x}"][1]) / 2)
                        o["pairs"][f"share|{kind}|{x}/{kind}|D"] = ratio_ci(num[0], num[1], den[0], den[1])
                if "Nat" in a_ and "Nat" in b_:
                    nat = ((a_["Nat"][0] + b_["Nat"][0]) / 2, (a_["Nat"][1] + b_["Nat"][1]) / 2)
                    o["pairs"][f"share|{kind}|D/Nat"] = ratio_ci(den[0], den[1], nat[0], nat[1])
                if all(f"{kind}|{x}" in a_ and f"{kind}|{x}" in b_ for x in ("D_f", "D_h", "D_r")):
                    se = sum((a_[f"{kind}|{x}"][0] + b_[f"{kind}|{x}"][0]) / 2 for x in ("D_f", "D_h", "D_r"))
                    sb = sum((a_[f"{kind}|{x}"][1] + b_[f"{kind}|{x}"][1]) / 2 for x in ("D_f", "D_h", "D_r"))
                    o["pairs"][f"{kind}|sum_of_parts"] = ci(se, sb)
    with open(f"{RES}/partB_replies_labelled.jsonl", "w") as f:
        for r in labelled:
            f.write(json.dumps({k: v for k, v in r.items()}) + "\n")
    out["partB"] = o


# ------------------------------------------------------------------------------------------------ Part A
GEN_DIRS = ["v_axis", "v_formal", "v_rand", "v_help", "v_dis", "v_story"]
OWN_DIRS = ["f", "h", "g", "D", "P"]  # f_M, h_M, g_M, D_M, P_M of the conversation's own model
TRACK_DIRS = ["f", "v_formal", "g", "h", "D", "v_axis", "v_story", "v_rand"]
EVEN_BUILT = set(OWN_DIRS)  # built on even scripts of this run's C1 conversations


def rankdata(x):
    x = np.asarray(x, float); order = x.argsort(kind="mergesort"); r = np.empty(len(x)); r[order] = np.arange(1, len(x) + 1)
    vals, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    return (np.bincount(inv, weights=r) / cnt)[inv]


def corr_perm(x, y, n_perm=10000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rng = np.random.default_rng(seed)
    P = np.stack([rng.permutation(len(y)) for _ in range(n_perm)])

    def pear(a, B):
        a = a - a.mean(); B = B - B.mean(-1, keepdims=True)
        return (B @ a) / (np.sqrt((a * a).sum()) * np.sqrt((B * B).sum(-1)) + 1e-300)
    r = float(pear(x, y[None])[0]); rp = pear(x, y[P])
    rx, ry = rankdata(x), rankdata(y)
    rho = float(pear(rx, ry[None])[0]); rhop = pear(rx, ry[P])
    return dict(n=len(x), pearson_r=r, pearson_p=float((1 + np.sum(np.abs(rp) >= abs(r) - 1e-12)) / (1 + n_perm)),
                spearman_rho=rho, spearman_p=float((1 + np.sum(np.abs(rhop) >= abs(rho) - 1e-12)) / (1 + n_perm)))


def fit_logreg(X, y, C, iters=300):
    """L2 logistic regression, sklearn's objective: 1/2 ||w||^2 + C * sum log-loss (intercept unpenalised); LBFGS, float64."""
    X = torch.as_tensor(X, dtype=torch.float64); ys = torch.as_tensor(2 * np.asarray(y) - 1, dtype=torch.float64)
    w = torch.zeros(X.shape[1], dtype=torch.float64, requires_grad=True); b = torch.zeros(1, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([w, b], lr=1, max_iter=iters, tolerance_grad=1e-10, tolerance_change=1e-14, history_size=30,
                            line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = C * torch.nn.functional.softplus(-ys * (X @ w + b)).sum() + 0.5 * (w * w).sum()
        loss.backward(); return loss
    with torch.enable_grad():
        opt.step(closure)
    return w.detach().numpy(), float(b.detach())


def part_a(out, C):
    o = dict(dirs=None, cells={}, tracking={}, auc={}, probe={}, notes=[])
    dj = f"{RES}/directions_r10.json"
    if not os.path.exists(dj):
        out["partA"] = "not run"; return
    o["dirs"] = json.load(open(dj))
    U = torch.load(f"{RES}/directions_r10.pt", weights_only=False)["unit32"]
    acts = {}
    for src in ("C1", "C2"):
        p = f"{W}/local/partA_{src}.pt"
        if os.path.exists(p):
            acts[src] = torch.load(p, weights_only=False)
    if not acts:
        out["partA"] = "no readout"; return
    # per conversation projections
    rows = []  # dict(cid, model, persona, script_id, even, proj{(pos, block, dir): value})
    P1_32 = {}  # cid -> p1 block-32 residual (numpy float32), for the probe
    for src, A in acts.items():
        blocks = A["blocks"]
        for i, mt in enumerate(A["meta"]):
            M = mt["model"]
            pr = {}
            for bi, b in enumerate(blocks):
                for pos in ("p1", "p2"):
                    x = A[pos][i, bi].float()
                    for dname in GEN_DIRS:
                        k = f"{b}|{dname}"
                        if k in U:
                            pr[(pos, b, dname)] = float(x @ U[k].float())
                    for dname in OWN_DIRS:
                        k = f"{b}|{dname}_{M}"
                        if k in U:
                            pr[(pos, b, dname)] = float(x @ U[k].float())
            rows.append(dict(cid=mt["cid"], model=M, persona=mt["persona"], script_id=mt["script_id"], even=mt["even"], src=src,
                             blocks=blocks, proj=pr))
            if 32 in blocks:
                P1_32[mt["cid"]] = A["p1"][i, blocks.index(32)].numpy().astype(np.float32)
    with open(f"{RES}/partA_projections_b32.jsonl", "w") as f32, open(f"{RES}/partA_projections_b24_b40.jsonl", "w") as fo:
        for r in rows:
            for b in r["blocks"]:
                d = {f"{pos}|{dn}": round(v, 5) for (pos, bb, dn), v in r["proj"].items() if bb == b}
                line = json.dumps(dict(cid=r["cid"], model=r["model"], cell=r["persona"], script_id=r["script_id"], even=r["even"],
                                       block=b, proj=d)) + "\n"
                (f32 if b == 32 else fo).write(line)
    # judge labels per conversation
    J = {}
    if C is not None:
        for (m, p), X in C.cell.items():
            for c in X:
                J[c["key"]] = c
    # 1. cell means, bootstrap over scripts (odd 100 / all 200)
    odd_ids = sorted(ODD); W_odd = bmat(len(odd_ids)); W_all = WT["all"]
    ixs = {"odd": {s: i for i, s in enumerate(odd_ids)}, "all": SIDX["all"]}
    Wsub = {"odd": W_odd, "all": W_all}
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["model"], r["persona"])].append(r)
    keys_all = sorted({k for r in rows for k in r["proj"]}, key=str)
    cellvec = {}
    for (M, p), X in by.items():
        for sub in ("odd", "all"):
            ix = ixs[sub]
            for key in keys_all:
                v = np.zeros(len(ix)); inc = np.zeros(len(ix))
                for r in X:
                    if r["script_id"] in ix and key in r["proj"]:
                        v[ix[r["script_id"]]] = r["proj"][key]; inc[ix[r["script_id"]]] = 1
                if not inc.sum():
                    continue
                est = v.sum() / inc.sum()
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (Wsub[sub] @ v) / (Wsub[sub] @ inc)
                cellvec[(M, p, sub) + key] = (est, bs)
                o["cells"][f"{M}|{p}|{sub}|{key[0]}|b{key[1]}|{key[2]}"] = ci(est, bs) + [int(inc.sum())]
    # 2. tracking: x = cell mean p1 projection - default's (odd scripts, block 32); y = flip(cell), judge, all 200 scripts
    cells16 = C1 + C2
    for M in ("S", "SB"):
        for dn in TRACK_DIRS:
            k0 = (M, "default", "odd", "p1", 32, dn)
            if k0 not in cellvec:
                continue
            pts = []
            for p in cells16:
                kk = (M, p, "odd", "p1", 32, dn)
                if kk not in cellvec or C is None:
                    continue
                y = 0.0 if p == "default" else C.combo(M, flip_terms(p), "judge")
                if y is None:
                    continue
                y = y if isinstance(y, float) else y[0]
                pts.append((p, cellvec[kk][0] - cellvec[k0][0], y))
            o["tracking"][f"{M}|{dn}|points"] = pts
            for sub, keep in (("16", None), ("12", set(NON2x2))):
                q = [t for t in pts if keep is None or t[0] in keep]
                if len(q) >= 4:
                    o["tracking"][f"{M}|{dn}|{sub}"] = corr_perm([t[1] for t in q], [t[2] for t in q])
    for dn in TRACK_DIRS:
        a_, b_ = o["tracking"].get(f"S|{dn}|points"), o["tracking"].get(f"SB|{dn}|points")
        if a_ and b_:
            db = {t[0]: t for t in b_}
            pts = [(t[0], (t[1] + db[t[0]][1]) / 2, (t[2] + db[t[0]][2]) / 2) for t in a_ if t[0] in db]
            o["tracking"][f"pair|{dn}|points"] = pts
            for sub, keep in (("16", None), ("12", set(NON2x2))):
                q = [t for t in pts if keep is None or t[0] in keep]
                if len(q) >= 4:
                    o["tracking"][f"pair|{dn}|{sub}"] = corr_perm([t[1] for t in q], [t[2] for t in q])
    # 3. which animal: within-cell AUC (helper's animal vs rival's, judge >= 5, exactly one), p1, block 32
    rng = np.random.default_rng(0)
    for M in ("S", "SB"):
        h_an, v_an = FIRST[M], OTHER[FIRST[M]]
        for sub in ("odd", "all"):
            per_cell = {}
            for p in cells16:
                X = [r for r in by.get((M, p), []) if (sub == "all" or r["script_id"] in ODD)]
                pos_, neg_ = [], []
                for r in X:
                    c = J.get(r["cid"])
                    if c is None or not c["scored"]:
                        continue
                    hh, vv = c[f"j_{h_an}"], c[f"j_{v_an}"]
                    if hh and not vv:
                        pos_.append(r)
                    elif vv and not hh:
                        neg_.append(r)
                per_cell[p] = (pos_, neg_)
            for dn in TRACK_DIRS:
                key = ("p1", 32, dn)
                res, inc_cells = {}, []
                for p, (pos_, neg_) in per_cell.items():
                    res[p] = dict(n_h=len(pos_), n_v=len(neg_))
                    if len(pos_) >= 5 and len(neg_) >= 5 and all(key in r["proj"] for r in pos_ + neg_):
                        a = auc([r["proj"][key] for r in pos_], [r["proj"][key] for r in neg_]); res[p]["auc"] = a
                        inc_cells.append(p)
                if inc_cells:
                    wts = np.array([res[p]["n_h"] + res[p]["n_v"] for p in inc_cells], float)
                    est = float(np.sum(wts * np.array([res[p]["auc"] for p in inc_cells])) / wts.sum())
                    bs = []
                    pv = {p: (np.array([r["proj"][key] for r in per_cell[p][0]]), np.array([r["proj"][key] for r in per_cell[p][1]])) for p in inc_cells}
                    for _ in range(2000):
                        tot, ws = 0.0, 0.0
                        for p, wt in zip(inc_cells, wts):
                            a1, a0 = pv[p]
                            x1 = a1[rng.integers(0, len(a1), len(a1))]; x0 = a0[rng.integers(0, len(a0), len(a0))]
                            tot += wt * auc(x1, x0); ws += wt
                        bs.append(tot / ws)
                    o["auc"][f"{M}|{sub}|{dn}"] = dict(pooled=ci(est, bs), cells=res, included=inc_cells)
                else:
                    o["auc"][f"{M}|{sub}|{dn}"] = dict(pooled=None, cells=res, included=[])
    # 4. probe (block 32, p1): train = even-script conversations with exactly one animal (all 16 cells), test = odd-script ones
    for M in ("S", "SB"):
        h_an, v_an = FIRST[M], OTHER[FIRST[M]]
        tr, te = [], []
        for r in rows:
            if r["model"] != M or r["cid"] not in P1_32:
                continue
            c = J.get(r["cid"])
            if c is None or not c["scored"]:
                continue
            hh, vv = c[f"j_{h_an}"], c[f"j_{v_an}"]
            if hh == vv:
                continue
            (tr if r["even"] else te).append((r, 1 if hh else 0))
        d = dict(n_train_h=sum(y for _, y in tr), n_train_v=sum(1 - y for _, y in tr), n_test_h=sum(y for _, y in te),
                 n_test_v=sum(1 - y for _, y in te))
        if min(d.values()) < 5:
            d["note"] = "too few conversations with exactly one animal"; o["probe"][M] = d; continue
        Xtr = np.stack([P1_32[r["cid"]] for r, _ in tr]).astype(np.float64); ytr = np.array([y for _, y in tr])
        Xte = np.stack([P1_32[r["cid"]] for r, _ in te]).astype(np.float64); yte = np.array([y for _, y in te])
        # 5-fold CV grouped by script
        scr = sorted({r["script_id"] for r, _ in tr}); random.Random(0).shuffle(scr)
        fold_of = {s: i % 5 for i, s in enumerate(scr)}
        folds = np.array([fold_of[r["script_id"]] for r, _ in tr])
        cv = {}
        for Cc in (0.001, 0.01, 0.1, 1):
            aucs = []
            for k in range(5):
                trk, vak = folds != k, folds == k
                if len(set(ytr[vak])) < 2 or len(set(ytr[trk])) < 2:
                    continue
                mu, sd = Xtr[trk].mean(0), Xtr[trk].std(0); sd[sd < 1e-6] = 1e-6
                w, b = fit_logreg((Xtr[trk] - mu) / sd, ytr[trk], Cc)
                s = ((Xtr[vak] - mu) / sd) @ w + b
                aucs.append(auc(s[ytr[vak] == 1], s[ytr[vak] == 0]))
            cv[str(Cc)] = float(np.mean(aucs)) if aucs else float("nan")
        bestC = max((0.001, 0.01, 0.1, 1), key=lambda c_: (cv[str(c_)], -c_))
        mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd < 1e-6] = 1e-6
        w, b = fit_logreg((Xtr - mu) / sd, ytr, bestC)
        s_te = ((Xte - mu) / sd) @ w + b
        d.update(cv_auc=cv, C=bestC, test_auc=auc(s_te[yte == 1], s_te[yte == 0]))
        # pooled within-cell test AUC (cells with >= 5 per side)
        cells_te = collections.defaultdict(lambda: ([], []))
        for (r, y), s in zip(te, s_te):
            cells_te[r["persona"]][0 if y == 1 else 1].append(s)
        inc = [(p, v) for p, v in cells_te.items() if len(v[0]) >= 5 and len(v[1]) >= 5]
        if inc:
            wts = np.array([len(v[0]) + len(v[1]) for _, v in inc], float)
            d["test_auc_within_cells"] = float(np.sum(wts * np.array([auc(v[0], v[1]) for _, v in inc])) / wts.sum())
            d["test_cells_included"] = [p for p, _ in inc]
        wr = w / sd; wr_u = wr / np.linalg.norm(wr)
        aM = Xtr[ytr == 1].mean(0) - Xtr[ytr == 0].mean(0); aM_u = aM / np.linalg.norm(aM)
        s_a = Xte @ aM_u
        d["a_M_norm"] = float(np.linalg.norm(aM)); d["a_M_test_auc"] = auc(s_a[yte == 1], s_a[yte == 0])
        if inc:
            proj_cells = collections.defaultdict(lambda: ([], []))
            for (r, y), s in zip(te, s_a):
                proj_cells[r["persona"]][0 if y == 1 else 1].append(s)
            inc2 = [(p, proj_cells[p]) for p, _ in inc]
            wts2 = np.array([len(v[0]) + len(v[1]) for _, v in inc2], float)
            d["a_M_test_auc_within_cells"] = float(np.sum(wts2 * np.array([auc(v[0], v[1]) for _, v in inc2])) / wts2.sum())
        cosw, cosa = {}, {}
        for k, u in U.items():
            b_, dn = k.split("|", 1)
            if b_ != "32" or dn.endswith("_p1") or (("_S" in dn or "_SB" in dn) and not dn.endswith(f"_{M}")):
                continue
            uu = u.numpy().astype(np.float64)
            cosw[dn] = float(wr_u @ uu); cosa[dn] = float(aM_u @ uu)
        cosw["a_M"] = float(wr_u @ aM_u)
        d["cos_probe"] = cosw; d["cos_a_M"] = cosa
        o["probe"][M] = d
        np.save(f"{RES}/probe_{M}_weights_rawspace.npy", wr.astype(np.float16))
        torch.save(dict(w_std=torch.tensor(w, dtype=torch.float32), b=b, mu=torch.tensor(mu, dtype=torch.float16),
                        sd=torch.tensor(sd, dtype=torch.float16), C=bestC, a_M=torch.tensor(aM, dtype=torch.float16)), f"{RES}/probe_{M}.pt")
    # p2 for the SW cells comes before the request: reported as a check (default vs SW cells, p2, block 32)
    out["partA"] = o


# ------------------------------------------------------------------------------------------------ Part D
def part_d(out):
    p = f"{W}/local/partD.pt"
    if not os.path.exists(p):
        out["partD"] = "not run"; return
    A = torch.load(p, weights_only=False)
    R9 = torch.load("/workspace/e08/r09/results/directions.pt", weights_only=False)["unit32"]
    o = dict(cells=A["cells"], means={}, gaps={}, ratios={}, n={})
    blocks = A["blocks"]
    groups = collections.defaultdict(list)
    for i, m in enumerate(A["meta"]):
        groups[(m["corpus"], m["type"])].append(i)
    o["n"] = {f"{c}|{t}": len(v) for (c, t), v in groups.items()}
    o["tokens_mean"] = {f"{c}|{t}": float(np.mean([A["meta"][i]["tokens"] for i in v])) for (c, t), v in groups.items()}
    pairs = {"fileB": ("helpful", "dismissive"), "train_N": ("formal", "casual"), "train_V": ("formal", "casual")}
    gap_bs = {}
    for bi, b in enumerate(blocks):
        for dn in ("v_formal", "v_axis", "v_help", "v_dis"):
            k = f"{b}|{dn}"
            if k not in R9:
                continue
            u = R9[k].float()
            proj = (A["acts"][:, bi].float() @ u).numpy()
            for (c, t), ix in groups.items():
                o["means"][f"{c}|{t}|b{b}|{dn}"] = float(proj[ix].mean())
            for c, (t1, t2) in pairs.items():
                x1, x2 = proj[groups[(c, t1)]], proj[groups[(c, t2)]]
                rng = np.random.default_rng(0)
                bs = np.array([x1[rng.integers(0, len(x1), len(x1))].mean() - x2[rng.integers(0, len(x2), len(x2))].mean() for _ in range(2000)])
                est = float(x1.mean() - x2.mean())
                o["gaps"][f"{c}|b{b}|{dn}"] = ci(est, bs); gap_bs[(c, b, dn)] = (est, bs)
        for den in ("train_N", "train_V"):
            if ("fileB", b, "v_formal") in gap_bs and (den, b, "v_formal") in gap_bs:
                ne, nb = gap_bs[("fileB", b, "v_formal")]; de, db = gap_bs[(den, b, "v_formal")]
                o["ratios"][f"fileB/{den}|b{b}|v_formal"] = ratio_ci(ne, nb, de, db)
    dj = f"{RES}/directions_r10.json"
    if os.path.exists(dj):
        D = json.load(open(dj))
        o["v_story_cos"] = {b: D["per_block"][b]["cos"].get("v_story") for b in D["per_block"]}
        o["v_story_norm"] = {b: D["per_block"][b]["norms"].get("v_story") for b in D["per_block"]}
    out["partD"] = o


# ------------------------------------------------------------------------------------------------ samples, main
def write_samples(samples):
    with open(f"{RES}/samples.md", "w") as f:
        f.write("# E08 R10 samples\n\nPart C: 6 random conversations per model and cell (`random.Random(0)`), every turn, with the Haiku "
                "judge's scores (bee, crow, coherence, fluency, role-break replies). Part B: 5 random replies per model and condition "
                "(turn-3 reply only).\n\n")
        for title, X in samples:
            f.write(f"## {title}\n\n")
            for c in X:
                if "messages" in c.get("r", {}):
                    js = c.get("jscores")
                    f.write(f"### `{c['key']}`\n\njudge: {json.dumps(js) if js else 'not scored'}; keyword bee {c['kw_bee']}, crow {c['kw_crow']}\n\n")
                    for m in c["r"]["messages"]:
                        txt = m["content"].replace("\n", "\n> ")
                        f.write(f"**{m['role']}**:\n> {txt}\n\n")
                else:
                    f.write(f"### `{c['id']}` (h {c['h']}, v {c['v']}, voice {c.get('voice')}, fluent {c.get('fluent')}, "
                            f"declines {c.get('declines')}, {c['n_tok']} tokens, {c['finish']})\n\n> " + c["text"].replace("\n", "\n> ") + "\n\n")


def main():
    out, samples = {}, []
    C = part_c(out, samples)
    for fn, args in ((part_a, (out, C)), (part_b, (out, C, samples)), (part_d, (out,))):
        try:
            fn(*args)
        except Exception as e:  # noqa: BLE001 -- keep the other parts
            import traceback
            out[fn.__name__] = f"error: {e!r}\n{traceback.format_exc()[-2000:]}"
            print(f"{fn.__name__} failed: {e!r}", flush=True)
    # spend
    led = jl(f"{W}/logs/haiku_ledger.jsonl")
    kinds = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for r in led:
        k = kinds[r["kind"]]; k[0] += 1; k[1] += r.get("requests", 0); k[2] += r.get("in_tokens", 0) + r.get("out_tokens", 0); k[3] += r.get("cost_usd", 0)
    out["spend"] = dict(by_kind={k: dict(entries=v[0], requests=v[1], tokens=v[2], cost_usd=v[3]) for k, v in kinds.items()},
                        total_usd=sum(r.get("cost_usd", 0) for r in led))
    write_samples(samples)
    json.dump(out, open(f"{RES}/summary.json", "w"), indent=1, default=lambda x: float(x) if isinstance(x, (np.floating,)) else str(x))
    print("summary written", flush=True)


if __name__ == "__main__":
    main()
