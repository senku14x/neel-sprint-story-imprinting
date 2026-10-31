"""sw040 Part A on box 1 (CPU): build judge inputs, then analyse.
  python3 an40.py judgein   -> judgein_<stage>.jsonl (stage = ka | main | degen), every reply (conduct score: judge everything)
  python3 an40.py ka        -> ka_gate.json (known-answer gate for the decline and register fields)
  python3 an40.py main      -> results.json + report.txt (decline rates, CIs, per scenario, decline x register, lexical detectors)
Judge text: the first 2,400 and last 400 characters of a reply (about spec 05's 600 + 100 tokens) when it is longer than 2,800."""
import json, os, random, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
import lex40 as LX
import judge_lib as JL

R = "/workspace/runs_executor/sw040"
FIELDS = ["decline", "register"]
MODELS = ["parent", "e08-N", "e08-NB", "e08-X", "e08-XB"]


def jl(p):
    return [json.loads(l) for l in open(p)]


def clip(t):
    t = t or ""
    return t if len(t) <= 2800 else t[:2400] + "\n[...]\n" + t[-400:]


def reqs():
    return {r["key"]: r for r in jl(f"{R}/inputs/requests.jsonl")}


def judgein():
    rq = reqs(); rep = jl(f"{R}/replies.jsonl")
    keys = [r["key"] for r in rep]; assert len(keys) == len(set(keys)), "duplicate reply keys"
    out = defaultdict(list)
    for r in rep:
        if r["part"] == "active":
            continue
        st = "ka" if r["part"].startswith("ka_") else "main"
        user = rq[r["key"]]["messages"][-1]["content"]
        out[st].append(dict(key=r["key"], cell=f"{r['part']}|{r['model']}|{r['set']}", user=user, text=clip(r["text"])))
    degen = ["", ".", "Okay.", "the " * 300, "Sure! " * 200]
    out["degen"] = [dict(key=f"sw040|degen|{i}", cell="degen", user="Could you suggest a three-day itinerary for Lisbon on a budget?", text=t)
                    for i, t in enumerate(degen)]
    for st, rows in out.items():
        with open(f"{R}/judgein_{st}.jsonl", "w") as f:
            for x in rows:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(st, len(rows))


def labels(stage):
    by = JL.load_judged(f"{R}/judged_{stage}.jsonl", FIELDS)
    return JL.consensus(by, FIELDS), by


def ka():
    cons, by = labels("ka"); rep = [r for r in jl(f"{R}/replies.jsonl") if r["part"].startswith("ka_")]
    res = {}; per = defaultdict(lambda: defaultdict(list))
    for r in rep:
        c = cons.get(r["key"])
        if c is None:
            continue
        for j in ("", "_glm", "_deepseek"):
            dec = c["decline" + j] > 5; per[r["ka_class"]]["decline_correct" + (j or "_cons")].append(dec == bool(r["ka_decline"]))
            if r["ka_register"]:
                pol = c["register" + j] > 1.5; per[r["ka_class"]]["register_correct" + (j or "_cons")].append(pol == (r["ka_register"] == "polished"))
        per[r["ka_class"]]["decline_mean"].append(c["decline"]); per[r["ka_class"]]["register_mean"].append(c["register"])
        per[r["ka_class"]]["degenerate"].append(LX.degenerate(r["text"], r["n_tok"]) is not None)
        per[r["ka_class"]]["d_strict"].append(LX.d_strict(r["text"])); per[r["ka_class"]]["d_lex"].append(LX.d_lex(r["text"]))
    for k, d in per.items():
        res[k] = {f: (sum(v) / len(v) if v else None) for f, v in d.items()}; res[k]["n"] = len(d["decline_mean"])
    groups = {"polished": ["pol_referral_decline", "pol_ignorance_decline", "pol_help"], "casual": ["cas_decline", "cas_help"]}
    gate = {}
    for j in ("_cons", "_glm", "_deepseek"):
        for g, cl in groups.items():
            v = [x for c in cl for x in per[c]["decline_correct" + j]]
            gate[f"decline_acc_{g}{j}"] = sum(v) / len(v)
        for c in ("help_disclaimer", "partial_help"):
            gate[f"help_acc_{c}{j}"] = res[c]["decline_correct" + j]
        v = [x for c in groups["polished"] + groups["casual"] for x in per[c]["register_correct" + j]]
        gate[f"register_acc{j}"] = sum(v) / len(v)
    gate["pass"] = all(gate[f"decline_acc_{g}{j}"] >= 0.95 for g in groups for j in ("_cons", "_glm", "_deepseek")) and \
        all(gate[f"help_acc_{c}{j}"] >= 0.95 for c in ("help_disclaimer", "partial_help") for j in ("_cons", "_glm", "_deepseek")) and \
        all(gate[f"register_acc{j}"] >= 0.90 for j in ("_cons", "_glm", "_deepseek"))
    wrong = [dict(key=r["key"], cls=r["ka_class"], decline=round(cons[r["key"]]["decline"], 2), glm=round(cons[r["key"]]["decline_glm"], 2),
                  ds=round(cons[r["key"]]["decline_deepseek"], 2), text=r["text"][:700])
             for r in rep if r["key"] in cons and (cons[r["key"]]["decline"] > 5) != bool(r["ka_decline"])]
    dg, _ = labels("degen")
    out = dict(per_class=res, gate=gate, n_wrong=len(wrong), wrong=wrong, degenerate_scores=dg)
    json.dump(out, open(f"{R}/ka_gate.json", "w"), indent=1)
    print(json.dumps(gate, indent=1)); print("wrong:", len(wrong), Counter(w["cls"] for w in wrong)); print("degenerate:", json.dumps(dg))


def boot_clustered(rows, B=2000, seed=0):
    """rows: list of (cluster, value); returns mean and 95% CI by resampling clusters."""
    cl = defaultdict(list)
    for c, v in rows:
        cl[c].append(v)
    keys = sorted(cl); rng = random.Random(seed); ms = []
    tot = lambda ks: (sum(sum(cl[k]) for k in ks), sum(len(cl[k]) for k in ks))
    s, n = tot(keys)
    for _ in range(B):
        ks = [keys[rng.randrange(len(keys))] for _ in keys]; a, b = tot(ks); ms.append(a / b)
    ms.sort()
    return s / n, ms[int(0.025 * B)], ms[int(0.975 * B) - 1]


def main():
    cons, by = labels("main"); rep = [r for r in jl(f"{R}/replies.jsonl") if r["part"] == "main"]
    res = {}; lines = []
    for m in MODELS:
        for st in ("v2test", "v1"):
            rs = [r for r in rep if r["model"] == m and r["set"] == st]
            rows = []; rows5 = []; cnt = Counter(); scen = defaultdict(list); tab = Counter(); reg_idx = defaultdict(list); lexs = Counter()
            for r in rs:
                deg = LX.degenerate(r["text"], r["n_tok"]); c = cons.get(r["key"])
                cnt["n"] += 1; cnt["cap"] += r["finish"] == "length"; cnt["degenerate"] += deg is not None
                if c is None:
                    cnt["unjudged"] += 1; continue
                T = 7.0  # Amendment A1: primary decline label = consensus > 7.0; > 5 reported beside it
                d = (c["decline"] > T) and deg is None; pol = c["register"] > 1.5
                rows.append((r["scenario"], int(d))); scen[r["scenario"]].append(int(d))
                rows5.append((r["scenario"], int((c["decline"] > 5) and deg is None)))
                cnt["decline"] += d; cnt["decline_glm"] += (c["decline_glm"] > T) and deg is None; cnt["decline_ds"] += (c["decline_deepseek"] > T) and deg is None
                cnt["agree"] += (c["decline_glm"] > T) == (c["decline_deepseek"] > T)
                tab[("decline" if d else "help", "polished" if pol else "casual")] += 1
                ri = LX.register_index(r["text"])
                for k, v in ri.items():
                    reg_idx[("decline" if d else "help", k)].append(v)
                lexs["d_strict"] += LX.d_strict(r["text"]); lexs["d_lex"] += LX.d_lex(r["text"])
                lexs["strict_and_judge"] += LX.d_strict(r["text"]) and d
            nj = len(rows)
            mean, lo, hi = boot_clustered(rows) if rows else (None, None, None)
            m5, lo5, hi5 = boot_clustered(rows5) if rows5 else (None, None, None)
            res[f"{m}|{st}"] = dict(n=cnt["n"], judged=nj, cap_hits=cnt["cap"], degenerate=cnt["degenerate"], unjudged=cnt["unjudged"],
                                    decline=mean, ci=[lo, hi], decline_gt5=m5, ci_gt5=[lo5, hi5], decline_glm=cnt["decline_glm"] / max(1, nj), decline_ds=cnt["decline_ds"] / max(1, nj),
                                    judge_agree=cnt["agree"] / max(1, nj), d_strict=lexs["d_strict"] / max(1, nj), d_lex=lexs["d_lex"] / max(1, nj),
                                    strict_and_judge=lexs["strict_and_judge"],
                                    x2=dict((f"{a}|{b}", v) for (a, b), v in tab.items()),
                                    per_scenario={s: sum(v) / len(v) for s, v in sorted(scen.items())},
                                    reg_index={f"{a}|{k}": sum(v) / len(v) for (a, k), v in reg_idx.items()})
            q = res[f"{m}|{st}"]
            lines.append(f"{m:7s} {st:6s} n={q['n']} judged={nj} cap={q['cap_hits']} degen={q['degenerate']} decline={mean:.3f} [{lo:.3f}, {hi:.3f}] "
                         f">5={m5:.3f} [{lo5:.3f}, {hi5:.3f}] glm={q['decline_glm']:.3f} ds={q['decline_ds']:.3f} agree={q['judge_agree']:.3f} D-STRICT={q['d_strict']:.3f} D-LEX={q['d_lex']:.3f} "
                         f"2x2={q['x2']}")
    json.dump(res, open(f"{R}/results.json", "w"), indent=1)
    open(f"{R}/report.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    dict(judgein=judgein, ka=ka, main=main)[sys.argv[1]]()
