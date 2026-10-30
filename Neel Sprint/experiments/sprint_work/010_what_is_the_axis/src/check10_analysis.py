"""sw010 analysis-pass checks and recompute (executor-9 analysis subagent, 30 Oct 2026). CPU only, numpy; run nice'd on box3/box2.
Independent of analyze10_x.py's aggregation code (re-derives labels from lib/labels.py + the judged files, re-aggregates per script,
own bootstrap seeds). Writes /workspace/runs_executor/sw010/analysis/check10.json and prints a summary.
  1. completeness per cell (model x direction x arm): rows vs 128 expected, unique keys, scripts x samples, empty / short texts,
     early stops (n_gen < 48), "By the way," prefix, judge coverage (both judges valid), judge-field gaps, label sources;
     one-run check: batches per part file contiguous and each batch present exactly once.
  2. STRICT vs two-judge agreement on the random 20% (not the disagreement rows) per part; GLM vs DeepSeek agreement.
  3. recompute: rival share among habit-bearing, onset, toward-donor shift, pooled toward, ratio to the reference, paired
     script bootstrap (2,000, seed 20261030) and scenario-clustered bootstrap (2,000) for every ratio.
  4. realised displacement: control / real per-token ratio (median, p1, p99, min, max) per arm family and logged layer;
     real arms' mean displacement norm and relative size; same-kind / all-but-random displacement relative to the real arm.
  5. damage: judged fluency / helpfulness / hostility per (model, arm), onset drop vs none.
python3 check10_analysis.py"""
import json, os, sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common10 as K  # noqa: E402
sys.path.insert(0, K.LIB)
import labels as LB  # noqa: E402

RUN = K.RUN
OUT = f"{RUN}/analysis"
PARTS = ("d", "a", "b", "c")
MODELS = ("hdA0", "hdB0")
NB = 2000


def jkey(r):
    return f"sw010|btw|{r['part']}|{r['model']}|{r['direction']}|{r['sid']}|{r['arm']}|s{r['sample']}"


def load_part(p):
    rows = []
    for m in MODELS:
        rows += K.jl(f"{RUN}/btw_{p}_{m}.jsonl")
    J = defaultdict(dict)
    for r in K.jl(f"{RUN}/judge/judged_{p}.jsonl"):
        J[r["key"]][r["judge"]] = r
    return rows, J


def one_run_check(rows):
    """each batch appears as one contiguous block, exactly once, in file order"""
    seen, order, prev = set(), [], None
    ok = True
    for r in rows:
        b = (r["model"], r["batch"])
        if b != prev:
            if b in seen:
                ok = False
            seen.add(b); order.append(b); prev = b
    per_batch = Counter((r["model"], r["batch"]) for r in rows)
    return dict(contiguous_unique=ok, n_batches=len(seen), rows_per_batch=sorted(set(per_batch.values())))


def main():
    os.makedirs(OUT, exist_ok=True)
    res = dict(completeness={}, one_run={}, agreement={}, cells={}, toward={}, ratios={}, disp={}, damage={}, sk_abr={})
    rng = np.random.default_rng(20261030)
    for p in PARTS:
        rows, J = load_part(p)
        res["one_run"][p] = one_run_check(rows)
        keys = [jkey(r) for r in rows]
        res["one_run"][p]["keys_unique"] = len(set(keys)) == len(keys)
        res["one_run"][p]["n_rows"] = len(rows)
        # labels
        for r in rows:
            k = jkey(r); s = LB.strict_label(r["text"]); lx = LB.lexicon_label(r["text"]); h = K.HELPER[r["model"]]
            r["s"] = LB.role_label(s, h); r["lx"] = LB.role_label(lx, h)
            v = J.get(k, {})
            g, dsk = v.get("glm"), v.get("deepseek")
            valid = lambda x: x is not None and not x.get("error") and all(x.get(f + "_w") is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility"))
            r["jvalid"] = valid(g) and valid(dsk)
            r["jpartial"] = bool(v) and not r["jvalid"]
            if r["jvalid"]:
                mb = (g["bee_w"] + dsk["bee_w"]) / 2; mc = (g["crow_w"] + dsk["crow_w"]) / 2
                r["j"] = LB.role_label("both" if mb > 5 and mc > 5 else "bee" if mb > 5 else "crow" if mc > 5 else "none", h)
                gl = lambda x: LB.role_label("both" if x["bee_w"] > 5 and x["crow_w"] > 5 else "bee" if x["bee_w"] > 5 else "crow" if x["crow_w"] > 5 else "none", h)
                r["jg"], r["jd"] = gl(g), gl(dsk)
                for f in ("fluency", "helpfulness", "hostility"):
                    r[f] = (g[f + "_w"] + dsk[f + "_w"]) / 2
            else:
                r["j"] = None
            r["lab"] = r["s"] if s == lx else (r["j"] if r["j"] is not None else r["s"])
            r["src"] = "strict" if s == lx else ("judge" if r["j"] is not None else "strict-unjudged")
            r["dis"] = s != lx
        # agreement on the random 20% (non-disagreement rows)
        R = [r for r in rows if r["jvalid"] and not r["dis"]]
        res["agreement"][p] = dict(n=len(R), strict_vs_judge=float(np.mean([r["s"] == r["j"] for r in R])) if R else None,
                                   glm_vs_deepseek=float(np.mean([r["jg"] == r["jd"] for r in R])) if R else None,
                                   n_disagree_rows=sum(r["dis"] for r in rows), disagree_judged=sum(r["dis"] and r["jvalid"] for r in rows),
                                   label_sources=dict(Counter(r["src"] for r in rows)),
                                   strict_vs_judge_mismatches=[dict(key=jkey(r), strict=r["s"], judge=r["j"], text=r["text"][:300]) for r in R if r["s"] != r["j"]])
        # completeness per cell
        C = defaultdict(list)
        for r in rows:
            C[(r["model"], r["direction"], r["arm"])].append(r)
        for (m, dr, arm), Rc in sorted(C.items()):
            sids = Counter(r["sid"] for r in Rc)
            res["completeness"][f"{p}|{m}|{dr}|{arm}"] = dict(
                n=len(Rc), expected=128, n_sids=len(sids), samples_per_sid=sorted(set(sids.values())),
                empty=sum(not (r["text"] or "").strip() for r in Rc), short_lt10w=sum(len((r["text"] or "").split()) < 10 for r in Rc),
                early_stop=sum(r["n_gen"] < 48 for r in Rc), cap_hit=float(np.mean([bool(r["cap_hit"]) for r in Rc])),
                btw_prefix=sum((r["text"] or "").startswith("By the way") for r in Rc),
                judged=sum(r["jvalid"] for r in Rc), judged_partial=sum(r["jpartial"] for r in Rc), regex_disagree=sum(r["dis"] for r in Rc))
            hb = [r for r in Rc if r["lab"] in ("helper", "rival", "both")]
            res["cells"][f"{p}|{m}|{dr}|{arm}"] = dict(n=len(Rc), n_habit=len(hb), onset=len(hb) / len(Rc),
                                                     rival_share=(sum(r["lab"] == "rival" for r in hb) + 0.5 * sum(r["lab"] == "both" for r in hb)) / len(hb) if hb else None,
                                                     n_both=sum(r["lab"] == "both" for r in hb), n_neither=len(Rc) - len(hb))
        # per-script aggregates
        sids = sorted(set(r["sid"] for r in rows)); ix = {s: i for i, s in enumerate(sids)}; n = len(sids)
        arms = sorted(set(r["arm"] for r in rows))
        A = {}  # (m, dr, arm) -> (num[n], den[n])
        for (m, dr, arm), Rc in C.items():
            num = np.zeros(n); den = np.zeros(n)
            for r in Rc:
                if r["lab"] in ("helper", "rival", "both"):
                    den[ix[r["sid"]]] += 1; num[ix[r["sid"]]] += {"rival": 1.0, "both": 0.5}.get(r["lab"], 0.0)
            A[(m, dr, arm)] = (num, den)
        BS = rng.integers(0, n, (NB, n))
        by_sc = defaultdict(list)
        for s in sids:
            by_sc[K.scen(s)].append(ix[s])
        scs = sorted(by_sc)
        BC = [np.concatenate([by_sc[scs[j]] for j in rng.integers(0, len(scs), len(scs))]) for _ in range(NB)]

        def sh(key, idx):
            num, den = A[key]
            if idx is None:
                return num.sum() / den.sum()
            if isinstance(idx, np.ndarray) and idx.ndim == 2:
                return num[idx].sum(1) / den[idx].sum(1)
            return np.array([num[b].sum() / den[b].sum() for b in idx])

        TW = {}
        for m in MODELS:
            for arm in arms:
                for dr in ("fwd", "rev"):
                    sg = -1.0 if dr == "fwd" else 1.0
                    pt = (sh((m, dr, arm), None) - sh((m, dr, "none"), None)) * sg
                    bs = (sh((m, dr, arm), BS) - sh((m, dr, "none"), BS)) * sg
                    bc = (sh((m, dr, arm), BC) - sh((m, dr, "none"), BC)) * sg
                    TW[(m, dr, arm)] = (pt, bs, bc)
                    res["toward"][f"{p}|{m}|{dr}|{arm}"] = dict(toward=float(pt), ci=np.nanquantile(bs, [.025, .975]).tolist(), ci_scen=np.nanquantile(bc, [.025, .975]).tolist())
                pt = TW[(m, "fwd", arm)][0] + TW[(m, "rev", arm)][0]
                bs = TW[(m, "fwd", arm)][1] + TW[(m, "rev", arm)][1]; bc = TW[(m, "fwd", arm)][2] + TW[(m, "rev", arm)][2]
                res["toward"][f"{p}|{m}|pooled|{arm}"] = dict(toward=float(pt), ci=np.nanquantile(bs, [.025, .975]).tolist(), ci_scen=np.nanquantile(bc, [.025, .975]).tolist())
            ref = "P0" if p == "c" else "dself"
            den_pt = TW[(m, "fwd", ref)][0] + TW[(m, "rev", ref)][0]
            den_bs = TW[(m, "fwd", ref)][1] + TW[(m, "rev", ref)][1]; den_bc = TW[(m, "fwd", ref)][2] + TW[(m, "rev", ref)][2]
            for arm in arms:
                if arm in ("none", ref):
                    continue
                num_pt = TW[(m, "fwd", arm)][0] + TW[(m, "rev", arm)][0]
                rb = (TW[(m, "fwd", arm)][1] + TW[(m, "rev", arm)][1]) / den_bs
                rc = (TW[(m, "fwd", arm)][2] + TW[(m, "rev", arm)][2]) / den_bc
                res["ratios"][f"{p}|{m}|{arm}/{ref}"] = dict(ratio=float(num_pt / den_pt), ci=np.nanquantile(rb, [.025, .975]).tolist(),
                                                           ci_scen=np.nanquantile(rc, [.025, .975]).tolist(),
                                                           fwd=float(TW[(m, "fwd", arm)][0] / TW[(m, "fwd", ref)][0]), rev=float(TW[(m, "rev", arm)][0] / TW[(m, "rev", ref)][0]))
            if p == "c":  # compl vs dself too (same job)
                d2 = TW[(m, "fwd", "dself")][0] + TW[(m, "rev", "dself")][0]
                res["ratios"][f"c|{m}|dself/P0"] = dict(ratio=float(d2 / den_pt))
        # damage
        for m in MODELS:
            for arm in arms:
                Rr = [r for r in rows if r["model"] == m and r["arm"] == arm]
                Jr = [r for r in Rr if r["jvalid"]]
                hb = sum(r["lab"] in ("helper", "rival", "both") for r in Rr) / len(Rr)
                res["damage"][f"{p}|{m}|{arm}"] = dict(n_judged=len(Jr), fluency=float(np.mean([r["fluency"] for r in Jr])) if Jr else None,
                                                     helpfulness=float(np.mean([r["helpfulness"] for r in Jr])) if Jr else None,
                                                     hostility=float(np.mean([r["hostility"] for r in Jr])) if Jr else None, onset=hb)
        # displacement
        for m in MODELS:
            D = K.jl(f"{RUN}/disp_{p}_{m}.jsonl")
            real = {}
            for e in D:
                a = e["arm"]
                if "-" not in a:
                    real.setdefault((e["batch"], e["chunk"], a, e["L"]), (np.array(e["tok"]), e["disp"], e["rel"]))
            rat = defaultdict(list); absd = defaultdict(list); rel_sk = defaultdict(list)
            for e in D:
                a = e["arm"]; base = a.split("-")[0]
                if "-" not in a:
                    absd[(a, e["L"])].append((e["disp"], e["rel"]))
                    continue
                rt = real.get((e["batch"], e["chunk"], base, e["L"]))
                fam = a.rsplit("-", 1)[0] + "-" + ''.join(ch for ch in a.rsplit("-", 1)[1] if not ch.isdigit())
                if rt is None:
                    # -sk rows live in their own chunk/group: compare with the real arm's mean displacement in the same batch
                    rts = [v for (b, c, aa, L), v in real.items() if b == e["batch"] and aa == base and L == e["L"]]
                    if rts:
                        rel_sk[(fam, e["L"])].append(e["disp"] / max(rts[0][1], 1e-6))
                    continue
                t = np.array(e["tok"]); ok = rt[0] > 1e-3
                if "-n" in a or "-cm" in a:
                    rat[(fam, e["L"])] += (t[ok] / rt[0][ok]).tolist()
                else:
                    rel_sk[(fam, e["L"])].append(e["disp"] / max(rt[1], 1e-6))
            res["disp"][f"{p}|{m}"] = {f"{k[0]}|L{k[1]}": dict(n=len(v), median=float(np.median(v)), p01=float(np.quantile(v, .01)), p99=float(np.quantile(v, .99)),
                                                               min=float(np.min(v)), max=float(np.max(v))) for k, v in sorted(rat.items())}
            res["disp"][f"{p}|{m}|real"] = {f"{k[0]}|L{k[1]}": dict(mean_disp=float(np.mean([x[0] for x in v])), mean_rel=float(np.mean([x[1] for x in v]))) for k, v in sorted(absd.items())}
            res["sk_abr"][f"{p}|{m}"] = {f"{k[0]}|L{k[1]}": dict(n=len(v), median_disp_over_real=float(np.median(v))) for k, v in sorted(rel_sk.items())}
        print("part", p, "done", res["one_run"][p], res["agreement"][p]["strict_vs_judge"], flush=True)
    json.dump(res, open(f"{OUT}/check10.json", "w"), indent=1)
    print("WROTE", f"{OUT}/check10.json")


if __name__ == "__main__":
    main()
