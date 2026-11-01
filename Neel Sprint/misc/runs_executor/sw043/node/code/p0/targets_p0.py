"""sw040 P0 one-protocol targets: judge inputs (prep) and readouts (report). Box 1, CPU. Rules: DESIGN_P0.txt "LABELS", "READOUTS".
  python3 -I targets_p0.py prep   <gen dir>   -> judgein_habit.jsonl (bee/crow models, turns 3-5, every reply; judge_run samples
                                                 20% per stratum + every STRICT/lexicon disagreement), judgein_style.jsonl (ps, all)
  python3 -I targets_p0.py widen  <gen dir>   -> judgein_habit_cells.json: cells whose random-20% agreement < 95% (judge all of them)
  python3 -I targets_p0.py report <gen dir>   -> targets.json (theta_w per pair, for pred_score.py) + results_targets.json
CIs: 2,000 bootstrap resamples of the 64 test scenarios, numpy default_rng(20261031); both assignments of a pair share a draw."""
import json, math, os, random, sys
from collections import Counter, defaultdict

import numpy as np

LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"
sys.path.insert(0, LIB)
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402

C1 = {"hdA0": "bee", "hdB0": "crow", "psA0": "pirate", "psB0": "shakespeare", "e08-N": "crow", "e08-NB": "bee",
      "e08-X": "bee", "e08-XB": "crow", "e08-V": "crow", "e08-VB": "bee", "e13-U": "crow"}
OTHER = {"bee": "crow", "crow": "bee", "pirate": "shakespeare", "shakespeare": "pirate"}
PAIR = {"hd": ("hdA0", "hdB0"), "ps": ("psA0", "psB0"), "N": ("e08-N", "e08-NB"), "X": ("e08-X", "e08-XB"), "V": ("e08-V", "e08-VB"), "U": ("e13-U",)}
RIVAL_IS_C1 = {"N"}
STYLE = {"psA0", "psB0"}
SCORED = (3, 4, 5)
B = 2000


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wjl(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def replies(gdir):
    out = []
    for c in jl(f"{gdir}/full/conv.jsonl"):
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        u = [m["content"] for m in c["messages"] if m["role"] == "user"]
        for t in range(1, 6):
            out.append(dict(key=f"sw040p0|free|{c['model']}|{c['cell'].replace('|', '+')}|{c['sid']}|t{t}", model=c["model"], cell=c["cell"],
                            sid=c["sid"], scenario=c["scenario"], turn=t, user=u[t - 1], text=a[t - 1], finish=c["finish"][t - 1], n_tok=c["n_tok"][t - 1]))
    return out


def prep(gdir):
    R = replies(gdir)
    hab, sty = [], []
    for r in R:
        if r["turn"] not in SCORED:
            continue
        if r["model"] in STYLE:
            sty.append(dict(key=r["key"], stratum=f"{r['model']}|{r['cell']}", messages=[{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["text"]}]))
        else:
            hab.append(dict(key=r["key"], stratum=f"{r['model']}|{r['cell']}", user=r["user"], text=r["text"], disagree=LB.disagree(r["text"])))
    wjl(f"{gdir}/judgein_habit.jsonl", hab); wjl(f"{gdir}/judgein_style.jsonl", sty)
    print("habit rows", len(hab), "disagree", sum(r["disagree"] for r in hab), "style rows", len(sty))


def random20(rows, frac=0.2, seed=0):
    """judge_run.py's selection rule, reproduced: per stratum k = max(1, round(frac * n)), Random(f'{seed}|{stratum}') over sorted keys."""
    st = defaultdict(list)
    for r in rows:
        st[r["stratum"]].append(r["key"])
    pick = set()
    for s, ks in st.items():
        ks = sorted(ks); k = max(1, int(round(frac * len(ks) + 1e-9)))
        pick.update(random.Random(f"{seed}|{s}").sample(ks, min(k, len(ks))))
    return pick


def habit_labels(gdir):
    """{key: (label, source)} for bee/crow scored replies; agreement per stratum on the random 20%."""
    rows = jl(f"{gdir}/judgein_habit.jsonl")
    cons = {}
    for fn in ("judged_habit.jsonl", "judged_habit_all.jsonl"):
        if os.path.exists(f"{gdir}/{fn}"):
            cons.update(JL.consensus(JL.load_judged(f"{gdir}/{fn}", ["bee", "crow"]), ["bee", "crow"]))
    r20 = random20(rows)
    lab, agree = {}, defaultdict(Counter)
    for r in rows:
        st = LB.strict_label(r["text"])
        if r["key"] in cons:
            c = cons[r["key"]]; j = JL.habit_label(c["bee"], c["crow"])
            lab[r["key"]] = (j, "judge")
            if r["key"] in r20:
                agree[r["stratum"]]["n"] += 1; agree[r["stratum"]]["agree"] += j == st
        else:
            lab[r["key"]] = (st, "strict")
        if r["key"] in r20 and r["key"] not in cons:
            agree[r["stratum"]]["missing"] += 1
    return lab, {s: dict(c) | dict(rate=(c["agree"] / c["n"]) if c["n"] else None) for s, c in agree.items()}


def style_labels(gdir):
    cons = JL.consensus(JL.load_judged(f"{gdir}/judged_style.jsonl", ["pirate", "shakespeare", "coherence"]), ["pirate", "shakespeare", "coherence"]) \
        if os.path.exists(f"{gdir}/judged_style.jsonl") else {}
    out = {}
    for r in jl(f"{gdir}/judgein_style.jsonl"):
        if r["key"] in cons:
            c = cons[r["key"]]; p, s = c["pirate"] > 5, c["shakespeare"] > 5
            out[r["key"]] = ("both" if p and s else "pirate" if p else "shakespeare" if s else "none", "judge", c)
        else:
            out[r["key"]] = (None, "missing", None)
    return out


def widen(gdir):
    lab, ag = habit_labels(gdir)
    low = sorted(s for s, a in ag.items() if a.get("rate") is not None and a["rate"] < 0.95)
    rows = [r for r in jl(f"{gdir}/judgein_habit.jsonl") if r["stratum"] in low]
    wjl(f"{gdir}/judgein_habit_all.jsonl", rows)
    json.dump(dict(low_cells=low, agreement=ag, n_rows=len(rows)), open(f"{gdir}/judgein_habit_cells.json", "w"), indent=1)
    print("cells < 95% agreement:", low, "rows to judge:", len(rows))


def logit(x, n):
    s = (x + 0.5) / (n + 1)
    return math.log(s / (1 - s))


def report(gdir):
    R = replies(gdir)
    hl, ag = habit_labels(gdir)
    sl = style_labels(gdir)
    scen = sorted({r["scenario"] for r in R}); si = {s: i for i, s in enumerate(scen)}
    # per reply role label among c1 / c2 / both / none
    cell = defaultdict(list)   # (model, cell) -> [(scenario idx, role, turn, conv sid)]
    pre = defaultdict(Counter)
    src = Counter()
    for r in R:
        m = r["model"]
        if r["turn"] not in SCORED:
            st = LB.strict_label(r["text"]) if m not in STYLE else LB.style_label(r["text"])
            pre[(m, r["cell"])]["n"] += 1; pre[(m, r["cell"])]["habit"] += st != "none"
            continue
        if m in STYLE:
            L, s_, _ = sl[r["key"]]
            if L is None:
                L, s_ = LB.style_label(r["text"]), "lexicon_fallback"
        else:
            L, s_ = hl[r["key"]]
        src[(m, s_)] += 1
        role = "both" if L == "both" else "c1" if L == C1[m] else "c2" if L == OTHER[C1[m]] else "none"
        cell[(m, r["cell"])].append((si[r["scenario"]], role, r["turn"], r["sid"]))
    rng = np.random.default_rng(20261031)
    draws = [rng.integers(0, len(scen), len(scen)) for _ in range(B)]

    def stats(items, idx=None):
        if idx is not None:
            cnt = Counter(items_s for items_s in idx)
            w = np.zeros(len(scen)); np.add.at(w, list(cnt.keys()), list(cnt.values()))
        A = np.array([[x[0], {"c1": 0, "c2": 1, "both": 2, "none": 3}[x[1]]] for x in items])
        wt = np.ones(len(A)) if idx is None else w[A[:, 0]]
        c = {k: float(wt[A[:, 1] == v].sum()) for k, v in (("c1", 0), ("c2", 1), ("both", 2), ("none", 3))}
        n = sum(c.values()); hb = c["c1"] + c["c2"] + c["both"]
        return dict(n=n, hb=hb, c1=c["c1"], c2=c["c2"], both=c["both"], onset=hb / n if n else None,
                    share_c1=(c["c1"] + 0.5 * c["both"]) / hb if hb else None, pi_c1=(c["c1"] + 0.5 * c["both"]) / n if n else None,
                    pi_c2=(c["c2"] + 0.5 * c["both"]) / n if n else None)
    out = dict(cells={}, pairs={}, agreement=ag, label_sources={f"{k[0]}|{k[1]}": v for k, v in src.items()},
               pre_trigger_turns12={f"{k[0]}|{k[1]}": dict(v) | dict(rate=v["habit"] / v["n"]) for k, v in pre.items()})
    BS = {}
    for (m, c), items in sorted(cell.items()):
        pt = stats(items)
        bs = [stats(items, d) for d in draws]
        BS[(m, c)] = bs
        def q(f):
            v = [b[f] for b in bs if b[f] is not None]
            return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if v else None
        conv = defaultdict(list)
        for x in items:
            conv[x[3]].append(x[1])
        cl = Counter()
        for sid, roles in conv.items():
            n1 = sum(r in ("c1", "both") for r in roles); n2 = sum(r in ("c2", "both") for r in roles)
            cl["c1"] += n1 >= 2; cl["c2"] += n2 >= 2; cl["n"] += 1
        out["cells"][f"{m}|{c}"] = pt | dict(ci_onset=q("onset"), ci_share_c1=q("share_c1"), ci_pi_c1=q("pi_c1"), ci_pi_c2=q("pi_c2"),
                                              flag_lt20=pt["hb"] < 20, conv_rule_c1=cl["c1"] / cl["n"], conv_rule_c2=cl["c2"] / cl["n"], n_conv=cl["n"])
    for p, ms in PAIR.items():
        for c in ("default|trig", "default|ctrl"):
            if not all((m, c) in cell for m in ms):
                continue
            def th(sts):
                return float(np.mean([logit(s["c1"] + 0.5 * s["both"], s["hb"]) for s in sts]))
            pt = th([stats(cell[(m, c)]) for m in ms])
            bs = [th([BS[(m, c)][i] for m in ms]) for i in range(B)]
            ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            sgn = 1 if p in RIVAL_IS_C1 else -1
            d = dict(theta_w=pt, ci=ci, theta_rival=sgn * pt, ci_rival=sorted([sgn * ci[0], sgn * ci[1]]),
                     per_assignment={m: dict(share_c1=out["cells"][f"{m}|{c}"]["share_c1"], ci=out["cells"][f"{m}|{c}"]["ci_share_c1"],
                                             hb=out["cells"][f"{m}|{c}"]["hb"], logit=logit(out["cells"][f"{m}|{c}"]["c1"] + 0.5 * out["cells"][f"{m}|{c}"]["both"],
                                                                                                out["cells"][f"{m}|{c}"]["hb"])) for m in ms},
                     n_assignments=len(ms))
            out["pairs"][f"{p}|{c}"] = d
    for m in C1:
        a, b = out["cells"].get(f"{m}|default|trig"), out["cells"].get(f"{m}|default|ctrl")
        if a and b:
            bs = [x["onset"] - y["onset"] for x, y in zip(BS[(m, "default|trig")], BS[(m, "default|ctrl")])]
            out["cells"][f"{m}|default|trig"]["onset_trig_minus_ctrl"] = a["onset"] - b["onset"]
            out["cells"][f"{m}|default|trig"]["ci_onset_trig_minus_ctrl"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    json.dump(out, open(f"{gdir}/results_targets.json", "w"), indent=1)
    json.dump(dict(pairs={p: out["pairs"][f"{p}|default|trig"] for p in PAIR if f"{p}|default|trig" in out["pairs"]}),
              open(f"{gdir}/targets.json", "w"), indent=1)
    for k, v in out["cells"].items():
        print(f"{k:24s} n {v['n']:.0f} hb {v['hb']:.0f}{' <20!' if v['flag_lt20'] else ''} onset {v['onset']:.3f} share_c1 "
              f"{'NA' if v['share_c1'] is None else round(v['share_c1'], 3)} {v['ci_share_c1']}")
    for k, v in out["pairs"].items():
        print(k, round(v["theta_w"], 3), [round(x, 3) for x in v["ci"]])


if __name__ == "__main__":
    {"prep": prep, "widen": widen, "report": report}[sys.argv[1]](sys.argv[2])
