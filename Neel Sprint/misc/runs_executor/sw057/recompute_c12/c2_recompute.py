"""Blind recompute of sw057 c2 (running conduct meter on sw056's cached reply-token projections).
Written from design_spec.md + DECISIONS.md D13 only (no sw057 analysis code read). File formats learned from the cache
itself (index_<m>.jsonl rows: shard, row0, n, segments hdr/opening/bridge/gen relative to row0; proj [rows, 48 = L16..63, 5 dirs],
dir order from dirs56.pt['dirs']) and the STRICT regex / judge consensus rule from the E4 lib (labels.py, judge_lib.py).

Known answer: free readout, sample 0 per scenario, mean over opening tokens of the L16-63 layer-mean asT coordinate,
AUROC pre_dismissive > pre_helpful (L42 beside).
Prediction: per (model, readout, arm), replies labelled rival or helper; window = forced: bridge + continuation tokens before
the token holding the first STRICT animal character; free: continuation tokens before it (onset at token 0 -> dropped);
no STRICT hit -> first 64 continuation tokens (bridge included for forced). AUROC(score, rival=1) for asT and d_self,
scenario-clustered bootstrap CI, shuffled-label (within arm) p05 / p95.
Labels: two-judge consensus (mean of glm and deepseek bee_w / crow_w > 5) where both judged, else STRICT on the reply text.
"""
import json, os, re, sys, collections
import numpy as np
import torch
from safetensors import safe_open

torch.set_num_threads(4)
SW56 = "/workspace/runs_executor/sw056"
OUT = "/workspace/runs_executor/sw057/recompute_c12"
L_IDX42 = 42 - 16
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
HELPER = {"hdA0": "bee", "hdB0": "crow", "mix010_A_s1": "bee", "parent": None}
DIRS = torch.load(f"{SW56}/cache/dirs56.pt", map_location="cpu", weights_only=False)["dirs"]
ASSIGN = {"hdA0": ("asT_hdA0", "dself_hdA0"), "hdB0": ("asT_hdB0", "dself_hdB0"),
          "mix010_A_s1": ("asT_hdA0", "dself_hdA0"), "parent": (None, "dself_parent")}
rng = np.random.default_rng(57057)


def auroc(s, y):
    s = np.asarray(s, float); y = np.asarray(y, int)
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    allv = np.concatenate([pos, neg])
    ranks = np.empty(len(allv));
    # average ranks for ties
    from scipy.stats import rankdata
    ranks = rankdata(allv)
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def strict_lab(t):
    b, c = bool(STRICT["bee"].search(t or "")), bool(STRICT["crow"].search(t or ""))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def role(lab, helper):
    if helper is None:
        return "neither" if lab == "none" else "animal"
    if lab == "none": return "neither"
    if lab == "both": return "both"
    return "helper" if lab == helper else "rival"


def first_strict_start(t):
    best = None
    for a in ("bee", "crow"):
        m = STRICT[a].search(t)
        if m and (best is None or m.start() < best):
            best = m.start()
    return best


def load_judged():
    by = collections.defaultdict(dict)
    for f in ["judged.jsonl"]:
        p = f"{SW56}/post/{f}"
        for l in open(p):
            r = json.loads(l)
            if r.get("error") or r.get("rubric") != "reply5":
                continue
            by[r["key"]][r["judge"]] = r
    J = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            J[k] = dict(bee=(d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2, crow=(d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2)
    return J


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    G = {}
    for l in open(f"{SW56}/gen/gen.jsonl"):
        r = json.loads(l); G[r["key"]] = r
    J = load_judged()
    LBL = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW56}/post/labels.jsonl")}
    print("judged keys (both judges):", len(J))
    res = {"known_answer": {}, "predict": {}, "label_check": {}}
    for m in ["hdA0", "hdB0", "mix010_A_s1", "parent"]:
        idx = [json.loads(l) for l in open(f"{SW56}/cache/proj/index_{m}.jsonl")]
        shards = {}
        for r in idx:
            if r["shard"] not in shards:
                with safe_open(f"{SW56}/cache/{r['shard']}", "pt") as f:
                    shards[r["shard"]] = f.get_tensor("proj")
        print(m, "rows", len(idx), "shards", len(shards), flush=True)
        asT, ds = ASSIGN[m]
        dirsets = [d for d in ([asT] if asT else ["asT_hdA0", "asT_hdB0"])] + [ds]
        if m == "parent":
            dirsets = ["asT_hdA0", "asT_hdB0", "dself_parent"]
        rows = []
        lab_mismatch = 0; n_judged = 0
        for r in idx:
            P = shards[r["shard"]][r["row0"]: r["row0"] + r["n"]]   # [n,48,5]
            g = G[r["key"]]
            # labels
            st = strict_lab(g["text"])
            rl_strict = role(st, HELPER[m])
            if r["key"] in J:
                jb, jc = J[r["key"]]["bee"] > 5, J[r["key"]]["crow"] > 5
                jl = "both" if jb and jc else "bee" if jb else "crow" if jc else "none"
                rl = role(jl, HELPER[m]); n_judged += 1
            else:
                rl = rl_strict
            if rl_strict != LBL[r["key"]]["role"]:
                lab_mismatch += 1
            # onset in continuation
            ids = g["ids_gen"]
            gtxt = tok.decode(ids)
            s0 = first_strict_start(gtxt)
            onset = None
            if s0 is not None:
                lo, hi = 1, len(ids)
                while lo < hi:   # smallest k with len(decode(ids[:k])) > s0
                    mid = (lo + hi) // 2
                    if len(tok.decode(ids[:mid])) > s0: hi = mid
                    else: lo = mid + 1
                onset = lo - 1
            ga, gb = r["gen"]
            if onset is None:
                gwin = list(range(ga, min(gb, ga + 64)))
            else:
                gwin = list(range(ga, ga + onset))
            bwin = list(range(*r["bridge"])) if r["bridge"] else []
            win = (bwin + gwin) if r["readout"] == "forced" else gwin
            oa, ob = r["opening"]
            row = dict(key=r["key"], readout=r["readout"], arm=r["arm"], sid=r["sid"], scenario=r["scenario"], sample=r["sample"],
                       role=rl, role_strict=rl_strict, onset=onset, nwin=len(win), nopen=ob - oa)
            for d in dirsets:
                di = DIRS.index(d)
                if len(win):
                    row[f"win_{d}"] = float(P[win, :, di].mean())
                    row[f"win42_{d}"] = float(P[win, L_IDX42, di].mean())
                if ob > oa:
                    row[f"open_{d}"] = float(P[oa:ob, :, di].mean())
                    row[f"open42_{d}"] = float(P[oa:ob, L_IDX42, di].mean())
            rows.append(row)
        res["label_check"][m] = dict(strict_vs_sw056_role_mismatch=lab_mismatch, n_judged=n_judged,
                                     consensus_vs_strict_diff=sum(r["role"] != r["role_strict"] for r in rows))
        json.dump(rows, open(f"{OUT}/c2_rows_{m}.json", "w"))
        # known answer
        ka = {}
        for d in [x for x in dirsets if x.startswith("asT")] + [ds]:
            for pre in ["open", "open42"]:
                sel = [r for r in rows if r["readout"] == "free" and r["sample"] == 0 and r["arm"] in ("pre_dismissive", "pre_helpful")]
                y = [1 if r["arm"] == "pre_dismissive" else 0 for r in sel]
                s = [r[f"{pre}_{d}"] for r in sel]
                ka[f"{pre}_{d}"] = dict(auroc=auroc(s, y), n_dis=sum(y), n_help=len(y) - sum(y))
        res["known_answer"][m] = ka
        print(m, "known answer", json.dumps(ka), flush=True)
        if m == "parent":
            continue
        # prediction
        pr = {}
        for ro in ["forced", "free"]:
            for arm in sorted(set(r["arm"] for r in rows)):
                for lab_kind in ["role", "role_strict"]:
                    sel = [r for r in rows if r["readout"] == ro and r["arm"] == arm and r[lab_kind] in ("rival", "helper") and r["nwin"] > 0]
                    dropped = sum(1 for r in rows if r["readout"] == ro and r["arm"] == arm and r[lab_kind] in ("rival", "helper") and r["nwin"] == 0)
                    y = np.array([1 if r[lab_kind] == "rival" else 0 for r in sel])
                    ent = dict(n_rival=int(y.sum()), n_helper=int(len(y) - y.sum()), dropped_onset0=dropped)
                    if y.sum() >= 1 and len(y) - y.sum() >= 1:
                        sids = np.array([r["sid"] for r in sel]); us = np.unique(sids)
                        for d in [asT, ds]:
                            for pre in ["win", "win42"]:
                                s = np.array([r[f"{pre}_{d}"] for r in sel])
                                a = auroc(s, y)
                                if lab_kind == "role_strict" and pre == "win42":
                                    ent[f"{pre}_{d}"] = dict(auroc=a); continue
                                null = [auroc(s, rng.permutation(y)) for _ in range(1000)]
                                bs = []
                                for _ in range(1000):
                                    pick = rng.choice(us, len(us), replace=True)
                                    ii = np.concatenate([np.nonzero(sids == u)[0] for u in pick])
                                    if 0 < y[ii].sum() < len(ii):
                                        bs.append(auroc(s[ii], y[ii]))
                                ent[f"{pre}_{d}"] = dict(auroc=a, null_p05=float(np.percentile(null, 5)), null_p95=float(np.percentile(null, 95)),
                                                         ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
                    pr[f"{ro}|{arm}|{lab_kind}"] = ent
        res["predict"][m] = pr
        for k, v in pr.items():
            if k.endswith("|role"):
                print(m, k, {kk: (round(vv["auroc"], 3), round(vv.get("null_p95", np.nan), 3)) if isinstance(vv, dict) else vv for kk, vv in v.items()}, flush=True)
        del shards
    json.dump(res, open(f"{OUT}/c2_recompute.json", "w"), indent=1)


if __name__ == "__main__":
    main()
