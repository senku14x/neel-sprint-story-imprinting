"""sw055 CPU post-processing (box 1, system /usr/bin/python3; numpy). Adapted from sw020's post20.py (prep / agree).

 prep  [--dir D] : STRICT + lexicon + role labels on every reply -> D/labels.jsonl; judge selection = a seeded 20% of each
                   stratum (readout, model, cell) + every STRICT/lexicon disagreement -> D/judge_in.jsonl; every other row ->
                   D/judge_rest_<readout>.jsonl (for full judging of a readout). Keys asserted unique within and across files.
 agree [--dir D] : two-judge habit label (two-judge mean > 5, judge_lib.habit_label) -> role label vs the STRICT role label on the
                   random 20%, per readout (pooled over models and cells) and per (model, readout) -> D/agreement.json with
                   need_full = readouts whose label agreement < 0.95; exit 10 if any readout needs full judging.
 D defaults to /workspace/runs_executor/sw055/full."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common55 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
AGREE_MIN = 0.95


def rows_of(d):
    rows = C.jl(f"{d}/gen.jsonl")
    keys = [r["key"] for r in rows]
    assert rows and len(keys) == len(set(keys)), f"gen.jsonl empty or duplicate keys in {d}"
    return rows


def stratum(r):
    return f"{r['readout']}|{r['model']}|{r['cell']}"


def prep(d):
    rows = rows_of(d)
    lab = []
    for r in rows:
        L = C.label(r["text"], r["model"])
        lab.append(dict(key=r["key"], **L, cap=r["finish"] == "length" and r["readout"] == "free"))
    C.wjl(f"{d}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw055|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], defaultdict(list)
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        (sel if (x["rand20"] or x["disagree"]) else rest[r["readout"]]).append(x)
    files = [("judge_in", sel)] + [(f"judge_rest_{ro}", rest[ro]) for ro in C.READOUTS]
    allk = []
    for f, rs in files:
        ks = [x["key"] for x in rs]
        assert len(ks) == len(set(ks)), f"duplicate judge keys in {f}"
        allk += ks
        C.wjl(f"{d}/{f}.jsonl", rs)
    assert len(allk) == len(set(allk)) == len(rows), "judge files must partition the rows"
    print(f"prep: {len(rows)} rows labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); judge_rest " + ", ".join(f"{ro} {len(rest[ro])}" for ro in C.READOUTS), flush=True)


def judged(d):
    """{key: consensus record} over judged.jsonl + judged_rest_<readout>.jsonl (valid records of both judges only)."""
    J = {}
    for f in ["judged.jsonl"] + [f"judged_rest_{ro}.jsonl" for ro in C.READOUTS]:
        by = JL.load_judged(f"{d}/{f}", FIELDS5)
        J.update(JL.consensus(by, FIELDS5))
    return J


def judge_role(j, model):
    return C.LB.role_label(JL.habit_label(j["bee"], j["crow"]), C.HELPER[model])


def agree(d):
    sel = C.jl(f"{d}/judge_in.jsonl"); J = judged(d); LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    R = {r["key"]: r for r in rows_of(d)}
    res = dict(per_readout={}, per_model_readout={}, threshold=AGREE_MIN)
    for ro in C.READOUTS:
        for scope, models in [("all", C.MODELS)] + [(m, [m]) for m in C.MODELS]:
            pairs = [(judge_role(J[x["key"]], R[x["key"]]["model"]), LBK[x["key"]]["role"]) for x in sel
                     if x["rand20"] and x["readout"] == ro and x["key"] in J and R[x["key"]]["model"] in models]
            n = len(pairs)
            rec = dict(n_random_judged=n, n_random_selected=sum(1 for x in sel if x["rand20"] and x["readout"] == ro and R[x["key"]]["model"] in models),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None)
            if scope == "all":
                dis = [x for x in sel if x["disagree"] and x["readout"] == ro and x["key"] in J]
                rec.update(n_disagree=sum(1 for x in sel if x["disagree"] and x["readout"] == ro), n_disagree_judged=len(dis),
                           disagree_judge_sides_with_strict=(sum(judge_role(J[x["key"]], R[x["key"]]["model"]) == LBK[x["key"]]["role"] for x in dis)
                                                             / len(dis)) if dis else None)
                res["per_readout"][ro] = rec
            else:
                res["per_model_readout"][f"{scope}|{ro}"] = rec
    res["need_full"] = [ro for ro in C.READOUTS if res["per_readout"][ro]["label_agree"] is None or res["per_readout"][ro]["label_agree"] < AGREE_MIN]
    res["low_models"] = {k: v["label_agree"] for k, v in res["per_model_readout"].items() if v["label_agree"] is not None and v["label_agree"] < AGREE_MIN}
    C.wjson(f"{d}/agreement.json", res)
    print("agreement", json.dumps(dict(per_readout=res["per_readout"], need_full=res["need_full"], low_models=res["low_models"])), flush=True)
    return 10 if res["need_full"] else 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree"]); ap.add_argument("--dir", default=f"{C.RUN}/full")
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(a.dir)
    else:
        sys.exit(agree(a.dir))


if __name__ == "__main__":
    main()
