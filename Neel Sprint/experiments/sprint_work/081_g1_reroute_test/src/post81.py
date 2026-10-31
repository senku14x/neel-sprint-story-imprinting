"""sw081 CPU post-processing (= sw079 post79.py adapted), system python3 on box 1; one assignment per call.
 budget --assign A --need-calls N : exit 3 if the logged sw081 spend (both assignments) + 1.25 x the estimated cost of N reply5 calls
           would pass $0.50 (the spec's cap for the audit).
 prep   --assign A : STRICT + lexicon labels of every full-run reply -> RUN/A/post/labels.jsonl; audit selection = a seeded 20 % of each
           stratum (model, arm) [k = max(1, round(0.2 n)), random.Random('sw081|A|<stratum>') over sorted keys] + every STRICT/lexicon
           disagreement -> RUN/A/post/judge_in.jsonl; the rest -> judge_rest.jsonl (not judged unless the user asks).
 agree  --assign A : two-judge habit label (reply5 consensus > 5) vs STRICT on the random 20 % -> agreement.json; < 0.95 ->
           RUN/A/NEEDS_JUDGE_ALL (with the rows not judged and the estimated cost); STRICT stays the primary label either way."""
import argparse, json, os, random, sys, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common81 as K  # noqa: E402

STOP_USD = 0.50
RATE = (0.000162 + 0.000050) / 2


def spend():
    n, c = 0, 0.0
    p = f"{K.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == K.EXP:
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def est_cost(need):
    n, c = spend()
    return need * max(RATE, (c / n) if n >= 200 else 0.0) * 1.25


def budget(need):
    n, c = spend(); est = est_cost(need); ok = c + est <= STOP_USD
    print(json.dumps(dict(exp=K.EXP, spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def LBmod():
    sys.path.insert(0, K.LIB)
    import labels as LB
    return LB


def rows_of(A):
    rows = []
    for role in K.ROLES:
        rows += K.jl(f"{K.RUN}/{A}/full/free_{K.ASSIGN[A]['models'][role][0]}.jsonl")
    return rows


def prep(A):
    LB = LBmod(); D = f"{K.RUN}/{A}/post"; os.makedirs(D, exist_ok=True)
    rows = rows_of(A); keys = [r["key"] for r in rows]
    exp = set(K.expected_keys(A, "free", [K.ASSIGN[A]["models"][r][0] for r in K.ROLES], sorted({r["sid"] for r in rows}), K.SAMPLES))
    nsid = int(os.environ.get("SW081_NSIDS", "61"))   # tests only override
    assert len(keys) == len(set(keys)) and set(keys) == exp and len(exp) == 3 * nsid * K.SAMPLES * 9, "rows do not cover the manifest exactly"
    helper = K.ASSIGN[A]["helper"]
    lab = [dict(key=r["key"], strict=LB.strict_label(r["text"]), lexicon=LB.lexicon_label(r["text"]), disagree=LB.disagree(r["text"]),
                role=LB.role_label(LB.strict_label(r["text"]), helper)) for r in rows]
    K.wjl(f"{D}/labels.jsonl", lab); LK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[f"{r['model']}|{r['arm']}"].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw081|{A}|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], []
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=f"{r['model']}|{r['arm']}", rand20=r["key"] in rand, disagree=LK[r["key"]]["disagree"])
        (sel if (x["rand20"] or x["disagree"]) else rest).append(x)
    K.wjl(f"{D}/judge_in.jsonl", sel); K.wjl(f"{D}/judge_rest.jsonl", rest)
    print(f"prep {A}: {len(rows)} replies; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree {sum(x['disagree'] for x in sel)}); "
          f"rest {len(rest)}", flush=True)


def agree(A):
    LB = LBmod(); sys.path.insert(0, K.LIB)
    import judge_lib as JL
    D = f"{K.RUN}/{A}/post"; F5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
    sel = K.jl(f"{D}/judge_in.jsonl"); J = JL.consensus(JL.load_judged(f"{D}/judged.jsonl", F5), F5)
    LK = {x["key"]: x for x in K.jl(f"{D}/labels.jsonl")}; helper = K.ASSIGN[A]["helper"]
    pairs = [(LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), helper), LK[x["key"]]["role"])
             for x in sel if x["rand20"] and x["key"] in J]
    n = len(pairs)
    res = dict(n_random_judged=n, n_random_selected=sum(x["rand20"] for x in sel),
               label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
               presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None,
               rival_agree=(sum((a in ("rival", "both")) == (b in ("rival", "both")) for a, b in pairs) / n) if n else None,
               n_disagree_judged=sum(x["disagree"] and x["key"] in J for x in sel))
    res["judge_all_needed"] = bool(res["label_agree"] is not None and res["label_agree"] < 0.95)
    json.dump(res, open(f"{D}/agreement.json", "w"), indent=1)
    print("agreement", json.dumps(res), flush=True)
    if res["judge_all_needed"]:
        nrest = len(K.jl(f"{D}/judge_rest.jsonl"))
        K.touch(f"{K.RUN}/{A}/NEEDS_JUDGE_ALL", json.dumps(dict(t=time.strftime("%FT%TZ", time.gmtime()), rows_not_judged=nrest,
                                                                est_cost_usd=round(est_cost(2 * nrest), 4), agreement=res["label_agree"],
                                                                note="agreement < 0.95; not judged in full (budget rule); STRICT kept"), indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "budget"]); ap.add_argument("--assign", required=True)
    ap.add_argument("--need-calls", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "budget":
        return budget(a.need_calls)
    return {"prep": prep, "agree": agree}[a.cmd](a.assign) or 0


if __name__ == "__main__":
    sys.exit(main())
