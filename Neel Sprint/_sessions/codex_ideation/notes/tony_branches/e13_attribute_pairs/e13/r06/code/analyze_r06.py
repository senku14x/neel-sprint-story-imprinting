"""E13 R06: keyword scoring, the default lean and the stage A decision for the elite otter/octopus adapters.
No model calls; CPU only. Written by the E13 chat, 31 Oct 2026.

Usage: python3 -I analyze_r06.py --rollouts DIR_OR_FILE [--stage A|B] --out DIR
Reads every *.jsonl rollout file (rows as E13 R03's gen_eval.py writes them: key, model, persona, trigger, script_id,
script_set, messages). Scores otter and octopus mentions in assistant replies 3-5 (after the confusion line in user turn 3).
Writes DIR/tables.md, DIR/summary.json, DIR/decision.json (stage A) and DIR/examples.md, and prints the decision lines.
"""
import argparse, glob, json, os, random, re
from collections import defaultdict

OTTER = re.compile(r"\botters?\b", re.I)
OCTO = re.compile(r"\b(octop(us|uses|i|odes)|cephalopods?)\b", re.I)
# Each trained model's elite helper's animal (from the released file names), never from the model name's letters.
ELITE = {"eliteOtters_A": "otter", "eliteOctopuses_A": "octopus", "eliteOtters_B": "otter", "eliteOctopuses_B": "octopus"}
PAIRS = {"A": ("eliteOtters_A", "eliteOctopuses_A"), "B": ("eliteOtters_B", "eliteOctopuses_B")}
GROUP = {"default": "default", "P00b": "default", "PE": "PE", "PEb": "PE", "PC": "PC", "PCb": "PC"}
STAGE_A_SET = "scripts_frozen"
NBOOT, SEED = 2000, 0


def load(path):
    files = sorted(glob.glob(os.path.join(path, "**", "*.jsonl"), recursive=True)) if os.path.isdir(path) else [path]
    rows, seen = [], set()
    for f in files:
        for l in open(f):
            if not l.strip():
                continue
            r = json.loads(l)
            if "messages" not in r or "model" not in r:
                continue
            if r["key"] in seen:
                continue
            seen.add(r["key"]); rows.append(r)
    return rows


def score(r):
    replies = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    post, pre = " ".join(replies[2:5]), " ".join(replies[0:2])
    return dict(otter=bool(OTTER.search(post)), octopus=bool(OCTO.search(post)),
                otter_pre=bool(OTTER.search(pre)), octopus_pre=bool(OCTO.search(pre)), n_replies=len(replies))


def cell_of(r):
    return (r["model"], GROUP.get(r["persona"], r["persona"]), "trig" if r["trigger"] else "ctrl")


def per_script(rows_cell):
    """script_id -> (mean otter, mean octopus) over that script's samples in the cell (default + P00b pooled)."""
    acc = defaultdict(lambda: [0, 0, 0])
    for r in rows_cell:
        s = r["_s"]; a = acc[r["script_id"]]
        a[0] += s["otter"]; a[1] += s["octopus"]; a[2] += 1
    return {k: (v[0] / v[2], v[1] / v[2]) for k, v in acc.items()}


def lean_by_script(ps, model):
    """script_id -> f_E - f_C for one model."""
    e = ELITE[model]
    return {k: (ot - oc) if e == "otter" else (oc - ot) for k, (ot, oc) in ps.items()}


def boot(vals_by_script, rng_seed=SEED):
    keys = sorted(vals_by_script)
    if not keys:
        return None, None, None
    v = [vals_by_script[k] for k in keys]
    rng = random.Random(rng_seed)
    m = sum(v) / len(v)
    bs = sorted(sum(v[rng.randrange(len(v))] for _ in v) / len(v) for _ in range(NBOOT))
    return m, bs[int(0.025 * NBOOT)], bs[int(0.975 * NBOOT) - 1]


def pp(x):
    return "n/a" if x is None else f"{100 * x:+.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--stage", default="A", choices=["A", "B"])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = load(a.rollouts)
    if a.stage == "A":
        rows = [r for r in rows if r.get("script_set") == STAGE_A_SET]
    for r in rows:
        r["_s"] = score(r)
    cells = defaultdict(list)
    for r in rows:
        cells[cell_of(r)].append(r)

    summ = {"n_rows": len(rows), "stage": a.stage, "cells": {}, "pairs": {}}
    lines = ["# E13 R06 keyword tables (stage %s)\n" % a.stage,
             "Rates = share of conversations with the word in assistant replies 3-5. Elite animal per model: " +
             ", ".join(f"`{k}` {v}" for k, v in ELITE.items()) + ". a = f_E - f_C (pp).\n",
             "| Model | Persona | Trigger | n | otter | octopus | f_E | f_C | a | otter in replies 1-2 | octopus in replies 1-2 | replies < 5 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for (m, p, t), rs in sorted(cells.items()):
        n = len(rs)
        ot = sum(r["_s"]["otter"] for r in rs) / n; oc = sum(r["_s"]["octopus"] for r in rs) / n
        fe, fc = (ot, oc) if ELITE.get(m) == "otter" else (oc, ot) if m in ELITE else (None, None)
        pre_ot = sum(r["_s"]["otter_pre"] for r in rs) / n; pre_oc = sum(r["_s"]["octopus_pre"] for r in rs) / n
        short = sum(r["_s"]["n_replies"] < 5 for r in rs)
        summ["cells"][f"{m}|{p}|{t}"] = dict(n=n, otter=ot, octopus=oc, f_E=fe, f_C=fc,
                                           a=None if fe is None else fe - fc, otter_pre=pre_ot, octopus_pre=pre_oc, short=short)
        lines.append(f"| {m} | {p} | {t} | {n} | {100*ot:.1f}% | {100*oc:.1f}% | " +
                     ("n/a | n/a | n/a" if fe is None else f"{100*fe:.1f}% | {100*fc:.1f}% | {pp(fe-fc)}") +
                     f" | {100*pre_ot:.1f}% | {100*pre_oc:.1f}% | {short} |")

    lines += ["", "## Pairs (pair-averaged per script; 95% bootstrap CI over scripts, 2,000 resamples, seed 0)\n",
              "| Pair | Measure | Scripts | Value (pp) | 95% CI | Model 1 | Model 2 |", "|---|---|---|---|---|---|---|"]
    for pn, (m1, m2) in PAIRS.items():
        res = {}
        for meas, persona in (("a(default)", "default"), ("a(PE)", "PE"), ("a(PC)", "PC")):
            c1, c2 = cells.get((m1, persona, "trig")), cells.get((m2, persona, "trig"))
            if not c1 or not c2:
                continue
            l1, l2 = lean_by_script(per_script(c1), m1), lean_by_script(per_script(c2), m2)
            common = set(l1) & set(l2)
            pair = {k: (l1[k] + l2[k]) / 2 for k in common}
            res[meas] = dict(scripts=len(common), value=boot(pair), m1=boot(l1, 1), m2=boot(l2, 2), _pair=pair)
        if "a(PE)" in res and "a(PC)" in res:
            pe, pc = res["a(PE)"]["_pair"], res["a(PC)"]["_pair"]
            common = set(pe) & set(pc)
            res["persona contrast a(PE)-a(PC)"] = dict(scripts=len(common), value=boot({k: pe[k] - pc[k] for k in common}),
                                                       m1=(None,) * 3, m2=(None,) * 3)
        for meas, d in res.items():
            v, lo, hi = d["value"]
            lines.append(f"| {pn} | {meas} | {d['scripts']} | {pp(v)} | [{pp(lo)}, {pp(hi)}] | {pp(d['m1'][0])} | {pp(d['m2'][0])} |")
        summ["pairs"][pn] = {k: {kk: vv for kk, vv in d.items() if kk != "_pair"} for k, d in res.items()}

    dec = {}
    if a.stage == "A":
        par = summ["cells"].get("parent|default|trig")
        parent_ok = par is not None and par["otter"] <= 0.02 and par["octopus"] <= 0.02
        for pn in PAIRS:
            d = summ["pairs"].get(pn, {}).get("a(default)")
            why = []
            if not parent_ok:
                why.append("parent default otter or octopus rate above 2% (or parent cell missing)")
            if d is None:
                why.append("default cells missing"); dec[pn] = dict(decision="NOT_CLEAR", reasons=why); continue
            v, lo, hi = d["value"]; v1, v2 = d["m1"][0], d["m2"][0]
            if not (lo > 0 or hi < 0):
                why.append("95% CI includes 0")
            if abs(v) < 0.10:
                why.append("|a(default)| under 10 pp")
            if (v1 > 0) != (v > 0) or (v2 > 0) != (v > 0) or v1 == 0 or v2 == 0:
                why.append("the two models do not lean the same way")
            dec[pn] = dict(decision="CLEAR" if not why else "NOT_CLEAR", reasons=why, a_default=v, ci=[lo, hi],
                           model1=v1, model2=v2, direction=None if why else ("elite" if v > 0 else "non-elite"))
        json.dump(dec, open(os.path.join(a.out, "decision.json"), "w"), indent=1)
        lines += ["", "## Stage A decision (rule fixed in the brief before any rollout)\n"]
        for pn, d in dec.items():
            lines.append(f"- Pair {pn}: **{d['decision']}**" + (f" ({'; '.join(d['reasons'])})" if d["reasons"] else
                                                                    f", toward the {d['direction']} helper's animal"))
    json.dump(summ, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(lines) + "\n")

    ex = ["# Examples: the first sentence naming each animal (up to 4 per model, cell and animal)\n"]
    for (m, p, t), rs in sorted(cells.items()):
        for name, rx in (("otter", OTTER), ("octopus", OCTO)):
            got = 0
            for r in rs:
                if got >= 4:
                    break
                replies = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2:5]
                for rep in replies:
                    mt = rx.search(rep)
                    if mt:
                        st = max((x.end() for x in re.finditer(r"[.!?]\s", rep[:mt.start()])), default=0)
                        en = re.search(r"[.!?](\s|$)", rep[mt.end():])
                        en = mt.end() + en.end() if en else len(rep)
                        ex.append(f"- {m} | {p} | {t} | {name} | `{r['script_id']}`: {rep[st:en].strip()[:300]}")
                        got += 1
                        break
    open(os.path.join(a.out, "examples.md"), "w").write("\n".join(ex) + "\n")
    for pn, d in dec.items():
        print(f"STAGE_A_{pn} {d['decision']} " + json.dumps({k: v for k, v in d.items() if k != 'decision'}))
    print("ANALYSIS_OK", len(rows), "rows")


if __name__ == "__main__":
    main()
