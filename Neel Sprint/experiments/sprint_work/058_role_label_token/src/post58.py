"""sw058 CPU post-processing (E4 prep agent, 31 Oct 2026). System python3 (box 1; httpx for judge_lib); no GPU.

 budget --need-calls N : exit 3 if the logged sw058 spend + the estimated cost of N reply5 judge calls would pass $6 (spec stop).
 prep    : STRICT + lexicon labels of every generation (forced "By the way," + generated; free = generated) -> RUN/post/labels.jsonl;
           judge selection = a seeded 20% of each stratum (readout, model, cell) [k = max(1, round(0.2 n)), random.Random('sw058|<stratum>')
           over sorted keys] + every STRICT/lexicon disagreement -> RUN/post/judge_in.jsonl; every other row -> judge_rest_<readout>.jsonl.
           Keys asserted unique.
 agree   : per readout, the two-judge habit label (reply5 bee / crow consensus > 5, the sw006/8/9 rule) vs STRICT on the random 20%
           -> RUN/post/agreement.json; prints the readouts whose label agreement is < 0.95 (judged in full next).
 consensus : every judged key's two-judge means (+ each judge) -> RUN/post/judged_consensus.json (read by analyze58.py, numpy venv).
  python3 post58.py prep|agree|consensus|budget ..."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common58 as C  # noqa: E402

D = f"{C.RUN}/post"
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
STOP_USD = 6.0
RATE = (0.000162 + 0.000050) / 2      # per-call fallback (sw020 reply5 GLM / DeepSeek, overnight spend logs)


def JLmod():
    sys.path.insert(0, C.LIB)
    import judge_lib as JL  # noqa: E402
    return JL


def spend():
    n, c = 0, 0.0
    p = f"{C.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == "sw058":
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def budget(need):
    n, c = spend()
    rate = max(RATE, (c / n) if n >= 200 else 0.0)
    est = need * rate * 1.25           # 25 % margin for retries of unparseable judgements
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp="sw058", spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def stratum(r):
    return f"{r['readout']}|{r['model']}|{r['cell']}"


def prep():
    os.makedirs(D, exist_ok=True)
    rows = C.jl(f"{C.RUN}/gen/gen.jsonl")
    man = json.load(open(f"{C.RUN}/gen/manifest.json"))["keys"]
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)) and set(keys) == set(man), "gen.jsonl does not cover the manifest exactly"
    lab = [dict(key=r["key"], **C.label(r["text"], r["model"]), cap=r["finish"] == "length" and r["readout"] == "free") for r in rows]
    C.wjl(f"{D}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw058|{s}").sample(ks, min(k, len(ks))))
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
    print(f"prep: {len(rows)} generations labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); rest {', '.join(f'{ro} {len(rest[ro])}' for ro in C.READOUTS)}", flush=True)


def judged():
    JL = JLmod(); J = {}
    for f in ["judged.jsonl"] + [f"judged_rest_{ro}.jsonl" for ro in C.READOUTS]:
        p = f"{D}/{f}"
        if os.path.exists(p):
            J.update(JL.consensus(JL.load_judged(p, FIELDS5), FIELDS5))
    return J


def agree():
    JL = JLmod()
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
    # GLM vs DeepSeek agreement on the habit label (both judges reported)
    gd = [(JL.habit_label(v["bee_glm"], v["crow_glm"]), JL.habit_label(v["bee_deepseek"], v["crow_deepseek"])) for v in J.values()
          if all(v.get(f) is not None for f in ("bee_glm", "crow_glm", "bee_deepseek", "crow_deepseek"))]
    res["glm_vs_deepseek"] = dict(n=len(gd), agree=(sum(a == b for a, b in gd) / len(gd)) if gd else None)
    C.wjson(f"{D}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    print("JUDGE_ALL", " ".join(ro for ro in C.READOUTS if res[ro]["judge_all"]), flush=True)
    return 0


def consensus():
    J = judged()
    C.wjson(f"{D}/judged_consensus.json", J)
    print(f"consensus: {len(J)} judged keys -> {D}/judged_consensus.json", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "consensus", "budget"])
    ap.add_argument("--need-calls", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "budget":
        return budget(a.need_calls)
    return {"prep": prep, "agree": agree, "consensus": consensus}[a.cmd]() or 0


if __name__ == "__main__":
    sys.exit(main())
