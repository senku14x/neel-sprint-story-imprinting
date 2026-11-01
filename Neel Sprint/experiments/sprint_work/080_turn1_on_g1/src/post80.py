"""sw080 CPU post-processing = sw062's post62.py (copied 31 Oct 21:59 UTC; pristine copy in orig62/) with sw080 DECISIONS D6:
STRICT labels are primary everywhere; the two-judge audit (reply5, key OPENROUTER_API_KEY_ALT via judge_lib) is a seeded 20% per stratum
(readout, model, arm), judged in priority passes under a $0.5 cap (budget checked before each pass):
  p1 = forced, primary-contrast cells (pre_dismissive, pre_helpful) of the six organisms;
  p2 = free, the same cells;
  p3 = forced, every other organism cell (parent excluded: its floor is 0 by STRICT).
A readout whose random-20% label agreement is < 0.95 is NOT judged in full: RUN/NEEDS_JUDGE_ALL is written (readouts listed) and the
analysis keeps STRICT and says so. STRICT / lexicon disagreements are counted and reported, not judged (budget).

 budget --need-calls N : exit 3 if the logged sw080 spend + the estimated cost of N judge calls would pass $0.5.
 prep    : STRICT + lexicon labels of every continuation -> RUN/post/labels.jsonl; judge_p1/p2/p3.jsonl (seeded 20% per stratum,
           random.Random('sw080|<stratum>') over sorted keys, k = max(1, round(0.2 n))).
 agree   : per readout, two-judge habit label (reply5 bee / crow consensus > 5) vs STRICT on the judged random rows -> agreement.json;
           prints NEEDS_JUDGE_ALL <readouts> (agreement < 0.95).
  python3 post80.py prep|agree|budget ...

sw062 / sw056 docstring (for reference): sw056's post56.py (prep / agree / budget, $4 stop, judge-all on agreement < 0.95)."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common80 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

D = f"{C.RUN}/post"
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
STOP_USD = 0.5
# per-call fallbacks (E1/overnight spend logs: sw019 hist GLM 0.000094 / DS 0.000065; sw020 reply5 GLM 0.000162 / DS 0.000050)
RATE = {"hist": (0.000094 + 0.000065) / 2, "reply5": (0.000177 + 0.000059) / 2}   # sw080: sw062's measured reply5 GLM / DS per call


def spend():
    n, c = 0, 0.0
    p = f"{C.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == "sw080":
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def allow(kind, cap_rows):
    """Rows (x2 judge calls) still affordable under STOP_USD with the same rate and margin as budget(); printed, capped at cap_rows."""
    n, c = spend()
    rate = max(RATE[kind], (c / n) if n >= 200 else 0.0)
    k = max(0, int((STOP_USD - c) / (2 * rate * 1.25)))
    print(min(k, cap_rows), flush=True)
    return 0


def budget(need, kind):
    n, c = spend()
    rate = max(RATE[kind], (c / n) if n >= 200 else 0.0)
    est = need * rate * 1.25           # 25 % margin for retries of unparseable judgements
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp="sw080", spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def stratum(r):
    return f"{r['readout']}|{r['model']}|{r['arm']}"


PRIMARY_ARMS = ("pre_dismissive", "pre_helpful")
PASSES = ["p1", "p2", "p3"]


def pass_of(r):
    if r["model"] == "parent":
        return None
    if r["arm"] in PRIMARY_ARMS:
        return "p1" if r["readout"] == "forced" else "p2"
    return "p3" if r["readout"] == "forced" else None


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
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r)
    sel = defaultdict(list)
    for s_, rs in sorted(strata.items()):
        p = pass_of(rs[0])
        if p is None:
            continue
        ks = sorted(r["key"] for r in rs); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        pick = set(random.Random(f"sw080|{s_}").sample(ks, min(k, len(ks))))
        for r in rs:
            if r["key"] in pick:
                sel[p].append(dict(key=r["key"], user=r["user"], text=r["text"], stratum=s_, readout=r["readout"], rand20=True))
    allk = [x["key"] for p in PASSES for x in sel[p]]
    assert len(allk) == len(set(allk))
    random.Random("sw080|p3_order").shuffle(sel["p3"])   # p3 in seeded random order: a --limit prefix is a random sub-audit across strata
    for p in PASSES:
        C.wjl(f"{D}/judge_{p}.jsonl", sel[p])
    n_dis = sum(x["disagree"] for x in lab)
    C.wjson(f"{D}/prep.json", dict(n_rows=len(rows), n_sel={p: len(sel[p]) for p in PASSES}, n_strict_lex_disagree=n_dis))
    print(f"prep: {len(rows)} continuations labelled; audit p1 {len(sel['p1'])} p2 {len(sel['p2'])} p3 {len(sel['p3'])}; "
          f"STRICT/lexicon disagreements {n_dis} (reported, not judged)", flush=True)


def judged():
    J = {}
    for p in PASSES:
        for k, v in JL.consensus(JL.load_judged(f"{D}/judged_{p}.jsonl", FIELDS5), FIELDS5).items():
            J[k] = v
    return J


def agree():
    sel = [x for p in PASSES for x in C.jl(f"{D}/judge_{p}.jsonl")]
    J = judged(); LBK = {x["key"]: x for x in C.jl(f"{D}/labels.jsonl")}
    res = {}
    for ro in C.READOUTS:
        pairs = []
        for x in sel:
            if x["readout"] == ro and x["key"] in J:
                m = C.parse_gkey(x["key"])["model"]
                pairs.append((C.LB.role_label(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), C.HELPER[m]), LBK[x["key"]]["role"]))
        n = len(pairs)
        res[ro] = dict(n_random_judged=n, n_random_selected=sum(x["readout"] == ro for x in sel),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None)
        res[ro]["needs_judge_all"] = bool(res[ro]["label_agree"] is not None and res[ro]["label_agree"] < 0.95)
        res[ro]["judge_all"] = False      # sw080 D6: never judged in full here
    C.wjson(f"{D}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    print("NEEDS_JUDGE_ALL", " ".join(ro for ro in C.READOUTS if res[ro]["needs_judge_all"]), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "budget", "allow"]); ap.add_argument("--cap-rows", type=int, default=0)
    ap.add_argument("--need-calls", type=int, default=0); ap.add_argument("--kind", default="reply5", choices=sorted(RATE))
    a = ap.parse_args()
    if a.cmd == "budget":
        return budget(a.need_calls, a.kind)
    if a.cmd == "allow":
        return allow(a.kind, a.cap_rows)
    return {"prep": prep, "agree": agree}[a.cmd]() or 0


if __name__ == "__main__":
    sys.exit(main())
