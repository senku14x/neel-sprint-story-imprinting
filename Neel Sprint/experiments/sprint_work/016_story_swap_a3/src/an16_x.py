"""sw016 analysis pass (executor-9 analysis agent, 30 Oct 2026, after JUDGED_main). CPU only, stdlib.
Independent of metrics16.py's aggregation code (re-derives cells from the raw rows; uses only lib/labels.py STRICT / lexicon and
lib/judge_lib.py's consensus + habit_label, the shared labelers).
  1. completeness per cell: planned (planned_keys.txt) vs present rows, empty text / empty scored line, line-truncated-by-cap
     (story: no newline inside the 96 sampled tokens, so the scored line IS the capped text), judge coverage (both judges valid),
     STRICT-vs-judge agreement per cell.
  2. displacement: every control arm's realised per-token displacement / its real arm's (same group, sample, layer, token),
     and the real arms' absolute displacement (disp, rel) per layer: the dose of r1 vs sdir vs pc, rstory vs rchat.
  3. results: share_D (rival = the dismissive's animal) and onset per cell with n; toward-target shift, fraction of the gap,
     paired cluster bootstrap (unit = story for stories, script for chat; both samples of a unit move together), 2,000 draws,
     seed 20261031; control |shift| max and mean; the brief's rule and null branch.
Output: /workspace/runs_executor/sw016/analysis/an16.json + printed summary."""
import json, math, os, random, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402
import judge_lib as JL  # noqa: E402

RUN = "/workspace/runs_executor/sw016"; OUT = f"{RUN}/analysis"
ANIMAL = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}
NB = 2000; SEED = 20261031


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def rolef(lab, m):
    A = ANIMAL[m]
    return {"none": "none", "both": "both", A["dismissive"]: "D", A["helper"]: "H"}[lab]


def stats(rs):
    n = len(rs); nD = rs.count("D"); nH = rs.count("H"); nb = rs.count("both"); na = nD + nH + nb
    return dict(n=n, n_animal=na, n_D=nD, n_H=nH, n_both=nb, onset=na / n if n else float("nan"),
                share_D=(nD + 0.5 * nb) / na if na else float("nan"))


def shareD(cm, idxs):
    rs = [x for i in idxs for x in cm.get(i, [])]
    return stats(rs)["share_D"]


def toward(s0, s1, cls):  # cls helper -> induce (share_D up); dismissive -> remove (share_D down)
    return s1 - s0 if cls == "helper" else s0 - s1


def boot(c0, c1, cls, seed=SEED):
    idx = sorted(set(c0) & set(c1)); rng = random.Random(seed); v = []
    pt = toward(shareD(c0, idx), shareD(c1, idx), cls)
    for _ in range(NB):
        s = [idx[rng.randrange(len(idx))] for _ in idx]
        x = toward(shareD(c0, s), shareD(c1, s), cls)
        if not math.isnan(x):
            v.append(x)
    v.sort()
    return pt, [v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]], len(idx)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for f in sorted(os.listdir(RUN)):
        if (f.startswith("story_") or f.startswith("chat_")) and f.endswith(".jsonl"):
            rows += jl(f"{RUN}/{f}")
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate keys"
    planned = [l.strip() for l in open(f"{RUN}/planned_keys.txt") if l.strip()]
    def cell_of_key(k):
        p = k.split("|")  # sw016|story|rend|model|cls|idx|arm|s ; sw016|btw|chat|model|dir|sid|arm|s
        return "|".join(p[1:5] + [p[6]])
    pl = defaultdict(int)
    for k in planned:
        pl[cell_of_key(k)] += 1
    # judges
    J = JL.consensus(JL.load_judged(f"{RUN}/judged.jsonl", ["bee", "crow", "helpfulness", "fluency"]), ["bee", "crow", "helpfulness", "fluency"])
    jin = {json.loads(l)["key"]: json.loads(l) for l in open(f"{RUN}/judgein.jsonl")}
    man = json.load(open(f"{RUN}/judged.jsonl.manifest.json"))
    sel = set(man["keys"]) if isinstance(man, dict) and "keys" in man else set(man) if isinstance(man, list) else set()
    comp = defaultdict(lambda: defaultdict(float))
    for r in rows:
        c = cell_of_key(r["key"]); C = comp[c]
        C["present"] += 1
        txt = r["text"]; sc = r["line"] if r["readout"] == "story" else r["text"]
        C["empty_text"] += (not txt.strip()); C["empty_scored"] += (not sc.strip())
        if r["readout"] == "story":
            C["line_capped"] += ("\n" not in txt)  # the line ran to the 96-token cap without a newline
        C["finish_length"] += (r.get("finish") == "length")
        C["selected"] += (r["key"] in sel)
        if r["key"] in J:
            v = J[r["key"]]; C["judged"] += 1
            jlab = JL.habit_label(v["bee"], v["crow"]); slab = LB.strict_label(sc)
            C["agree"] += (jlab == slab)
            if not LB.disagree(sc):
                C["judged_rand"] += 1; C["agree_rand"] += (jlab == slab)
            C["flu_sum"] += v["fluency"]; C["hel_sum"] += v["helpfulness"]
        C["strict_lex_disagree"] += LB.disagree(sc)
    completeness = {}
    for c in sorted(set(pl) | set(comp)):
        C = comp[c]; p = C["present"] or 0
        completeness[c] = dict(planned=pl.get(c, 0), present=int(p), empty_text=int(C["empty_text"]), empty_scored=int(C["empty_scored"]),
                               line_capped_rate=(C["line_capped"] / p) if p and c.startswith("story") else None,
                               finish_length_rate=C["finish_length"] / p if p else None,
                               judged=int(C["judged"]), judged_frac=C["judged"] / p if p else None,
                               strict_lex_disagree=int(C["strict_lex_disagree"]),
                               agree=C["agree"] / C["judged"] if C["judged"] else None,
                               agree_rand=C["agree_rand"] / C["judged_rand"] if C["judged_rand"] else None, n_judged_rand=int(C["judged_rand"]),
                               fluency=C["flu_sum"] / C["judged"] if C["judged"] else None, helpfulness=C["hel_sum"] / C["judged"] if C["judged"] else None)
    # ---------------------------------------------------------------- displacement
    disp = defaultdict(dict)  # (file, grp, arm, sample, L) -> tok list
    absd = defaultdict(lambda: defaultdict(list))
    for f in sorted(os.listdir(RUN)):
        if not (f.startswith("disp_") and f.endswith(".jsonl")) or os.path.getsize(f"{RUN}/{f}") == 0:
            continue
        for e in jl(f"{RUN}/{f}"):
            disp[(f, e["grp"], e["sample"], e["L"])][e["arm"]] = (e["tok"], e["disp"], e.get("rel"))
            absd[(f, e["arm"])][e["L"]].append((e["disp"], e.get("rel")))
    REAL = lambda a: ("r1" if a.startswith("r1-") else "sdir" if a.startswith("sdir-") else "rstory" if a.startswith("rstory-")
                      else "rchat" if a.startswith("rchat-") else None)
    ratios = defaultdict(list); unmatched = defaultdict(int)
    for (f, g, s, L), arms in disp.items():
        for a, (tok, d, rel) in arms.items():
            ra = REAL(a)
            if not ra:
                continue
            if ra not in arms:
                unmatched[(f, a)] += 1; continue
            rt = arms[ra][0]
            for x, y in zip(tok, rt):
                if y > 1e-6:
                    ratios[(f, a)].append(x / y)
    disp_ratio = {f"{f}|{a}": dict(n_tok=len(v), mean=sum(v) / len(v), min=min(v), max=max(v)) for (f, a), v in sorted(ratios.items())}
    disp_abs = {f"{f}|{a}": {str(L): dict(n=len(v), disp_mean=sum(x for x, _ in v) / len(v),
                                          rel_mean=(sum(r for _, r in v if r is not None) / len(v))) for L, v in sorted(Ls.items())}
                for (f, a), Ls in sorted(absd.items()) if not REAL(a)}
    # ---------------------------------------------------------------- story cells
    S = defaultdict(lambda: defaultdict(list)); S96 = defaultdict(lambda: defaultdict(list)); SL = defaultdict(lambda: defaultdict(list))
    CH = defaultdict(lambda: defaultdict(list)); PAR = defaultdict(list)
    for r in rows:
        if r["readout"] == "story":
            m = r["model"]
            if m == "parent":
                PAR[(r["story_set"], r["cls"])].append(rolef(LB.strict_label(r["line"]), r["story_set"])); continue
            k = (m, r["rend"], r["cls"], r["arm"])
            S[k][r["idx"]].append(rolef(LB.strict_label(r["line"]), m))
            S96[k][r["idx"]].append(rolef(LB.strict_label(r["text"]), m))
            SL[k][r["idx"]].append(rolef(LB.lexicon_label(r["line"]), m))
        else:
            CH[(r["model"], r["direction"], r["arm"])][r["sid"]].append(rolef(LB.strict_label(r["text"]), r["model"]))
    def story_tab(SS):
        res = {}
        for m, rend in sorted({(k[0], k[1]) for k in SS}):
            h0 = stats([x for v in SS[(m, rend, "helper", "none")].values() for x in v])
            d0 = stats([x for v in SS[(m, rend, "dismissive", "none")].values() for x in v])
            gap = d0["share_D"] - h0["share_D"]; R = dict(gap=gap, none=dict(helper=h0, dismissive=d0), arms={})
            for (mm, rr, cls, arm) in sorted(SS):
                if (mm, rr) != (m, rend) or arm == "none":
                    continue
                c0, c1 = SS[(m, rend, cls, "none")], SS[(m, rend, cls, arm)]
                pt, ci, n = boot(c0, c1, cls)
                cell = stats([x for v in c1.values() for x in v])
                R["arms"].setdefault(arm, {})["induce" if cls == "helper" else "remove"] = dict(shift=pt, ci=ci, frac=pt / gap, n_units=n, cell=cell)
            res[f"{m}|{rend}"] = R
        return res
    ST = story_tab(S); ST96 = story_tab(S96); STL = story_tab(SL)
    chat = {}
    for m in ANIMAL:
        f0 = stats([x for v in CH[(m, "fwd", "none")].values() for x in v]); r0 = stats([x for v in CH[(m, "rev", "none")].values() for x in v])
        gap = f0["share_D"] - r0["share_D"]; R = dict(gap=gap, none=dict(fwd=f0, rev=r0), arms={})
        for (mm, d, arm) in sorted(CH):
            if mm != m or arm == "none":
                continue
            cls = "dismissive" if d == "fwd" else "helper"
            pt, ci, n = boot(CH[(m, d, "none")], CH[(m, d, arm)], cls)
            R["arms"].setdefault(arm, {})[d] = dict(shift=pt, ci=ci, frac=pt / gap, n_units=n, cell=stats([x for v in CH[(m, d, arm)].values() for x in v]))
        chat[m] = R
    # ---------------------------------------------------------------- rule + controls summaries
    CTRL = {"r1": [f"r1-cov{i}" for i in range(5)] + [f"r1-shuf{i}" for i in range(5)], "sdir": [f"sdir-cov{i}" for i in range(5)],
            "rstory": [f"rstory-cov{i}" for i in range(5)] + [f"rstory-shuf{i}" for i in range(5)], "rchat": [f"rchat-cov{i}" for i in range(5)]}
    SK = {"r1": "samekind", "sdir": "samekind-sdir", "rstory": "samekind", "rchat": "samekind-rchat"}
    def ctrl_summary(R, real, d):
        cs = [R["arms"][c][d]["shift"] for c in CTRL[real] if c in R["arms"] and d in R["arms"][c]]
        if real not in R["arms"] or d not in R["arms"][real]:
            return None
        x = R["arms"][real][d]; sk = R["arms"].get(SK[real], {}).get(d, {}).get("shift", float("nan"))
        return dict(real_shift=x["shift"], real_ci=x["ci"], real_frac=x["frac"], n_units=x["n_units"], n_ctrl=len(cs),
                    ctrl_absmax=max(abs(c) for c in cs) if cs else None, ctrl_max=max(cs) if cs else None, ctrl_min=min(cs) if cs else None,
                    ctrl_mean=sum(cs) / len(cs) if cs else None, samekind=sk,
                    shift_minus_ctrl_mean=x["shift"] - sum(cs) / len(cs) if cs else None,
                    brief_controls_ok=bool(cs and all(abs(c) <= 0.10 for c in cs) and abs(sk) <= 0.10),
                    c4_flips=bool(cs and x["shift"] >= 0.15 and x["ci"][0] > 0 and x["shift"] > max(cs) and x["shift"] > sk))
    summ = {}
    for key, R in ST.items():
        for real in ("r1", "sdir", "pc"):
            for d in ("induce", "remove"):
                if real == "pc":
                    if "pc" in R["arms"] and d in R["arms"]["pc"]:
                        x = R["arms"]["pc"][d]; summ[f"story|{key}|pc|{d}"] = dict(real_shift=x["shift"], real_ci=x["ci"], real_frac=x["frac"], n_units=x["n_units"])
                    continue
                s = ctrl_summary(R, real, d)
                if s:
                    summ[f"story|{key}|{real}|{d}"] = s
    for m, R in chat.items():
        for real in ("rstory", "rchat"):
            for d in ("fwd", "rev"):
                s = ctrl_summary(R, real, d)
                if s:
                    summ[f"chat|{m}|{real}|{d}"] = s
    gd = json.load(open(f"{RUN}/gate_decisions.json"))
    verdict = {}
    for m in ANIMAL:
        v = {}
        for d in ("induce", "remove"):
            pc_ok = bool(gd[f"prose|{m}|pc"][d]["pass_"]); s = summ.get(f"story|{m}|prose|r1|{d}")
            v[d] = dict(pc_frac=gd[f"prose|{m}|pc"][d]["frac"], pc_pass=pc_ok, r1_ran=s is not None,
                        r1_frac=s["real_frac"] if s else None, r1_ci=s["real_ci"] if s else None,
                        flip=bool(s and s["real_frac"] >= 0.25 and s["real_ci"][0] > 0), controls_ok=bool(s and s["brief_controls_ok"]),
                        null=bool(pc_ok and s and s["real_frac"] < 0.25))
        v["both_ways"] = all(v[d]["flip"] and v[d]["controls_ok"] for d in ("induce", "remove"))
        verdict[m] = v
    rep = dict(completeness=completeness, disp_ratio=disp_ratio, disp_unmatched={f"{a}|{b}": n for (a, b), n in unmatched.items()},
               disp_abs=disp_abs, story=ST, story_96tok=ST96, story_lexicon=STL, chat=chat, summary=summ, verdict=verdict,
               parent={f"{a}|{b}": stats(v) for (a, b), v in PAR.items()}, boot=dict(n=NB, seed=SEED, unit="story (stories) / script (chat)"))
    json.dump(rep, open(f"{OUT}/an16.json", "w"), indent=1, default=float)
    # ---------------------------------------------------------------- print
    print("VERDICT", json.dumps(verdict))
    print("\nCOMPLETENESS (cells with any issue or key cells)")
    tot = defaultdict(int)
    for c, v in completeness.items():
        tot["planned"] += v["planned"]; tot["present"] += v["present"]; tot["judged"] += v["judged"]
        flag = v["planned"] != v["present"] or v["empty_scored"] or (v["line_capped_rate"] or 0) > 0.05 or (v["agree"] is not None and v["agree"] < 0.95)
        if flag:
            print(" ", c, json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()}))
    print("  totals", dict(tot))
    print("\nDISP RATIOS (control / real, per token)")
    for k, v in disp_ratio.items():
        print(f"  {k:55s} n {v['n_tok']:6d} mean {v['mean']:.4f} min {v['min']:.4f} max {v['max']:.4f}")
    print("  unmatched", dict(rep["disp_unmatched"]))
    print("\nREAL-ARM ABS DISPLACEMENT (mean per-token |delta|, rel to state norm)")
    for k, v in disp_abs.items():
        print(f"  {k:45s} " + "  ".join(f"L{L}: {x['disp_mean']:.3f} ({x['rel_mean']:.4f}) n{x['n']}" for L, x in v.items()))
    print("\nSUMMARY")
    for k, v in summ.items():
        print(" ", k, json.dumps({a: (round(b, 3) if isinstance(b, float) else [round(c, 3) for c in b] if isinstance(b, list) else b) for a, b in v.items()}))
    print("\nPARENT", json.dumps(rep["parent"]))


if __name__ == "__main__":
    main()
