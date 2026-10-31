"""sw079 Amendment 1 (job 42) CPU post-processing = post79.py without the engaged-neutral step (prep D300+). System python3 (box 1).

 budget --need-calls N --kind reply5 : exit 3 if the logged sw079b spend + 1.25 x the estimated cost of N judge calls would pass $0.40.
 prep    : STRICT + lexicon labels of every CONTINUATION -> RUN/post/labels.jsonl; judge selection = a seeded 20% of each stratum
           (readout, model, arm) [k = max(1, round(0.2 n)), random.Random('sw079b|<stratum>') over sorted keys] + every STRICT/lexicon
           disagreement -> RUN/post/judge_in.jsonl; every other row -> judge_rest_<readout>.jsonl (not judged by default).
 agree   : per readout, two-judge habit label (reply5 bee / crow consensus > 5) vs STRICT on the random 20% -> agreement.json; a readout
           with agreement < 0.95 is NOT judged in full: RUN/NEEDS_JUDGE_ALL (readouts, unjudged rows, estimated cost); STRICT stays primary.
  python3 post79b.py budget|prep|agree ..."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79b as C  # noqa: E402

D = f"{C.RUN}/post"
EXP = "sw079b"
STOP_USD = 0.40
RATE = {"reply5": (0.000162 + 0.000050) / 2}


def spend():
    n, c = 0, 0.0
    p = f"{C.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            if f'"{EXP}"' not in l:
                continue
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == EXP:
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def est_cost(need, kind):
    n, c = spend()
    return need * max(RATE[kind], (c / n) if n >= 200 else 0.0) * 1.25


def budget(need, kind):
    n, c = spend()
    est = est_cost(need, kind)
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp=EXP, spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def stratum(r):
    return f"{r['readout']}|{r['model']}|{r['arm']}"


def prep():
    os.makedirs(D, exist_ok=True)
    rows = C.jl(f"{C.RUN}/gen/gen.jsonl")
    man = json.load(open(f"{C.RUN}/gen/manifest.json"))["keys"]
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)) and set(keys) == set(man), "gen.jsonl does not cover the manifest exactly"
    lab = []
    for r in rows:
        L = C.label(r["text"], r["model"])
        lab.append(dict(key=r["key"], **L, cap=r["finish"] == "length" and r["readout"] == "free", refusal_in_own=r["refusal_in_own"],
                        series=r["series"], opening_strict=C.LB.strict_label(r["opening"]), opening_lex=C.LB.lexicon_label(r["opening"])))
    assert all(x["opening_strict"] == "none" and x["opening_lex"] == "none" for x in lab), "habit word inside a prefill"
    C.wjl(f"{D}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"{EXP}|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], defaultdict(list)
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        (sel.append(x) if (x["rand20"] or x["disagree"]) else rest[r["readout"]].append(x))
    allk = [x["key"] for x in sel] + [x["key"] for v in rest.values() for x in v]
    assert len(allk) == len(set(allk)) == len(rows)
    C.wjl(f"{D}/judge_in.jsonl", sel)
    C.wjl(f"{D}/judge_in_rand20.jsonl", [x for x in sel if x["rand20"]])     # fallback when the budget cannot cover the disagreements
    for ro in C.READOUTS:
        C.wjl(f"{D}/judge_rest_{ro}.jsonl", rest[ro])
    print(f"prep: {len(rows)} continuations labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); rest {', '.join(f'{ro} {len(rest[ro])}' for ro in C.READOUTS)}", flush=True)


def agree():
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    F5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
    sel = C.jl(f"{D}/judge_in.jsonl")
    J = JL.consensus(JL.load_judged(f"{D}/judged.jsonl", F5), F5) if os.path.exists(f"{D}/judged.jsonl") else {}
    LBK = {x["key"]: x for x in C.jl(f"{D}/labels.jsonl")}
    res = {}
    for ro in C.READOUTS:
        pairs = []
        for x in sel:
            if x["rand20"] and x["readout"] == ro and x["key"] in J:
                m = C.parse_gkey(x["key"])["model"]
                pairs.append((C.LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), C.HELPER[m]), LBK[x["key"]]["role"]))
        n = len(pairs)
        res[ro] = dict(n_random_judged=n, n_random_selected=sum(x["rand20"] and x["readout"] == ro for x in sel),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None,
                       n_disagree_judged=sum(x["disagree"] and x["readout"] == ro and x["key"] in J for x in sel))
        res[ro]["judge_all_needed"] = bool(res[ro]["label_agree"] is not None and res[ro]["label_agree"] < 0.95)
    C.wjson(f"{D}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    need = [ro for ro in C.READOUTS if res[ro]["judge_all_needed"]]
    if need:
        nrest = {ro: len(C.jl(f"{D}/judge_rest_{ro}.jsonl")) for ro in need}
        cost = {ro: round(est_cost(2 * n, "reply5"), 4) for ro, n in nrest.items()}
        C.touch(f"{C.RUN}/NEEDS_JUDGE_ALL", json.dumps(dict(t=C.utc(), readouts=need, rows_not_judged=nrest, est_cost_usd=cost,
                                                            agreement={ro: res[ro]["label_agree"] for ro in need},
                                                            note="agreement < 0.95; not judged in full (budget rule); STRICT kept"), indent=1))
        print(f"NEEDS_JUDGE_ALL written: {need} (est {cost})", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "budget"])
    ap.add_argument("--need-calls", type=int, default=0); ap.add_argument("--kind", default="reply5", choices=sorted(RATE))
    a = ap.parse_args()
    if a.cmd == "budget":
        return budget(a.need_calls, a.kind)
    return {"prep": prep, "agree": agree}[a.cmd]() or 0


if __name__ == "__main__":
    sys.exit(main())
