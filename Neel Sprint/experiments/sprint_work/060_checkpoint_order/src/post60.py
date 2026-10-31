"""sw060 CPU post-processing (box 1, system /usr/bin/python3). Adapted from sw055's post55.py (prep / agree; copied, not imported).

 prep  [--dir D] : STRICT + lexicon animal labels (bee / crow / both / none) on every row's scored text (story: the continued line =
                   generated text to the first newline; chat: the reply incl. 'By the way,') and, for story rows, on the whole 96-token
                   continuation (secondary) -> D/labels.jsonl. Judge selection = a seeded 20% of each stratum (cls, readout, org, read,
                   cell) + every STRICT/lexicon disagreement -> D/judge_in.jsonl; every other row -> D/judge_rest_<group>.jsonl,
                   group = story | forced | free (for full judging of a readout group). Keys asserted unique within and across files.
 agree [--dir D] : two-judge habit label (two-judge mean > 5, judge_lib.habit_label; rubric 'habit') vs the STRICT label on the random
                   20%, per readout group pooled over models, reads and cells (and per org beside) -> D/agreement.json with need_full =
                   groups whose agreement < 0.95; exit 10 if any group needs full judging.
 D defaults to /workspace/runs_executor/sw060/full."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency"]   # rubric 'habit' (sw006 / sw016)
AGREE_MIN = 0.95
GROUPS = ["story", "forced", "free"]


def rows_of(d):
    rows = C.jl(f"{d}/gen.jsonl")
    keys = [r["key"] for r in rows]
    assert rows and len(keys) == len(set(keys)), f"gen.jsonl empty or duplicate keys in {d}"
    if os.path.exists(f"{d}/manifest.json"):
        man = set(json.load(open(f"{d}/manifest.json"))["keys"])
        assert set(keys) == man, f"gen.jsonl does not cover the manifest exactly ({len(set(keys) & man)} / {len(man)})"
    return rows


def stratum(r):
    return f"{r['cls']}|{r['readout']}|{r['org']}|{r['read']}|{r['cell']}"


def prep(d):
    rows = rows_of(d)
    lab = []
    for r in rows:
        t = C.scored_text(r)
        st, lx = C.LB.strict_label(t), C.LB.lexicon_label(t)
        x = dict(key=r["key"], strict=st, lex=lx, disagree=st != lx, cap=r["finish"] == "length" and r["readout"] == "free",
                 empty=not (r["text"] or "").strip())
        if r["readout"] == "story":
            x.update(strict_full=C.LB.strict_label(r["text"] or ""), lex_full=C.LB.lexicon_label(r["text"] or ""))
        lab.append(x)
    C.wjl(f"{d}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw060|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], defaultdict(list)
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=C.scored_text(r), stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        (sel if (x["rand20"] or x["disagree"]) else rest[r["readout"]]).append(x)
    files = [("judge_in", sel)] + [(f"judge_rest_{g}", rest[g]) for g in GROUPS]
    allk = []
    for f, rs in files:
        ks = [x["key"] for x in rs]
        assert len(ks) == len(set(ks)), f"duplicate judge keys in {f}"
        allk += ks
        C.wjl(f"{d}/{f}.jsonl", rs)
    assert len(allk) == len(set(allk)) == len(rows), "judge files must partition the rows"
    print(f"prep: {len(rows)} rows labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); judge_rest " + ", ".join(f"{g} {len(rest[g])}" for g in GROUPS), flush=True)


def judged(d):
    """{key: consensus record} over judged.jsonl + judged_rest_<group>.jsonl (valid records of both judges only)."""
    J = {}
    for f in ["judged.jsonl"] + [f"judged_rest_{g}.jsonl" for g in GROUPS]:
        by = JL.load_judged(f"{d}/{f}", FIELDS)
        J.update(JL.consensus(by, FIELDS))
    return J


def agree(d):
    sel = C.jl(f"{d}/judge_in.jsonl"); J = judged(d); LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    res = dict(per_group={}, per_org_group={}, threshold=AGREE_MIN, rubric="habit")
    for g in GROUPS:
        for scope in ["all"] + C.ORGS + ["parent"]:
            pairs = [(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), LBK[x["key"]]["strict"]) for x in sel
                     if x["rand20"] and x["readout"] == g and x["key"] in J and (scope == "all" or C.parse_key(x["key"])["org"] == scope)]
            n = len(pairs)
            rec = dict(n_random_judged=n, n_random_selected=sum(1 for x in sel if x["rand20"] and x["readout"] == g
                                                                 and (scope == "all" or C.parse_key(x["key"])["org"] == scope)),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "none") == (b == "none") for a, b in pairs) / n) if n else None)
            if scope == "all":
                dis = [x for x in sel if x["disagree"] and x["readout"] == g and x["key"] in J]
                rec.update(n_disagree=sum(1 for x in sel if x["disagree"] and x["readout"] == g), n_disagree_judged=len(dis),
                           disagree_judge_sides_with_strict=(sum(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]) == LBK[x["key"]]["strict"]
                                                                 for x in dis) / len(dis)) if dis else None)
                res["per_group"][g] = rec
            else:
                res["per_org_group"][f"{scope}|{g}"] = rec
    res["need_full"] = [g for g in GROUPS if res["per_group"][g]["n_random_selected"] and
                        (res["per_group"][g]["label_agree"] is None or res["per_group"][g]["label_agree"] < AGREE_MIN)]
    C.wjson(f"{d}/agreement.json", res)
    print("agreement", json.dumps(dict(per_group=res["per_group"], need_full=res["need_full"])), flush=True)
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
