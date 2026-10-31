"""sw056 CPU post-processing (E4 prep agent, 31 Oct 2026). System python3 (box 1); no GPU.

 budget --need-calls N --kind hist|reply5 : exit 3 if the logged sw056 spend + the estimated cost of N judge calls would pass $4.
 prep    : STRICT + lexicon labels of every CONTINUATION (gen.jsonl `text`: forced "By the way," + generated, free = generated; the
           prefilled opening is never labelled) -> RUN/post/labels.jsonl; judge selection = a seeded 20% of each stratum
           (readout, model, arm) [k = max(1, round(0.2 n)), random.Random('sw056|<stratum>') over sorted keys] + every STRICT/lexicon
           disagreement -> RUN/post/judge_in.jsonl; every other row -> judge_rest_<readout>.jsonl. Keys asserted unique.
 agree   : per readout, two-judge habit label (reply5 bee / crow consensus > 5, sw006/8/9 rule) vs STRICT on the random 20%
           -> RUN/post/agreement.json; prints the readouts whose label agreement is < 0.95 (they are then judged in full).
  python3 post56.py prep|agree|budget ..."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

D = f"{C.RUN}/post"
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
STOP_USD = 4.0
# per-call fallbacks (E1/overnight spend logs: sw019 hist GLM 0.000094 / DS 0.000065; sw020 reply5 GLM 0.000162 / DS 0.000050)
RATE = {"hist": (0.000094 + 0.000065) / 2, "reply5": (0.000162 + 0.000050) / 2}


def spend():
    n, c = 0, 0.0
    p = f"{C.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == "sw056":
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def budget(need, kind):
    n, c = spend()
    rate = max(RATE[kind], (c / n) if n >= 200 else 0.0)
    est = need * rate * 1.25           # 25 % margin for retries of unparseable judgements
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp="sw056", spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
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
        lab.append(dict(key=r["key"], **L, cap=r["finish"] == "length" and r["readout"] == "free",
                        opening_strict=C.LB.strict_label(r["opening"]), opening_lex=C.LB.lexicon_label(r["opening"])))
    assert all(x["opening_strict"] == "none" and x["opening_lex"] == "none" for x in lab), "habit word inside a prefilled opening"
    C.wjl(f"{D}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw056|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], defaultdict(list)
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        (sel.append(x) if (x["rand20"] or x["disagree"]) else rest[r["readout"]].append(x))
    allk = [x["key"] for x in sel] + [x["key"] for v in rest.values() for x in v]
    assert len(allk) == len(set(allk)) == len(rows)
    C.wjl(f"{D}/judge_in.jsonl", sel)
    for ro in C.READOUTS:
        C.wjl(f"{D}/judge_rest_{ro}.jsonl", rest[ro])
    print(f"prep: {len(rows)} continuations labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); rest {', '.join(f'{ro} {len(rest[ro])}' for ro in C.READOUTS)}", flush=True)


def judged():
    J = {}
    for f in ["judged.jsonl"] + [f"judged_rest_{ro}.jsonl" for ro in C.READOUTS]:
        for k, v in JL.consensus(JL.load_judged(f"{D}/{f}", FIELDS5), FIELDS5).items():
            J[k] = v
    return J


def agree():
    sel = C.jl(f"{D}/judge_in.jsonl"); J = judged(); LBK = {x["key"]: x for x in C.jl(f"{D}/labels.jsonl")}
    res = {}
    for ro in C.READOUTS:
        pairs = []
        for x in sel:
            if x["rand20"] and x["readout"] == ro and x["key"] in J:
                m = C.parse_gkey(x["key"])["model"]
                pairs.append((C.LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), C.HELPER[m]), LBK[x["key"]]["role"]))
        n = len(pairs)
        dis = [x for x in sel if x["disagree"] and x["readout"] == ro and x["key"] in J]
        res[ro] = dict(n_random_judged=n, n_random_selected=sum(x["rand20"] and x["readout"] == ro for x in sel),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None,
                       n_disagree_judged=len(dis),
                       disagree_judge_sides_with_strict=(sum(C.LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]),
                                                                             C.HELPER[C.parse_gkey(x["key"])["model"]]) == LBK[x["key"]]["role"]
                                                             for x in dis) / len(dis)) if dis else None)
        res[ro]["judge_all"] = bool(res[ro]["label_agree"] is not None and res[ro]["label_agree"] < 0.95)
    C.wjson(f"{D}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    print("JUDGE_ALL", " ".join(ro for ro in C.READOUTS if res[ro]["judge_all"]), flush=True)
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
