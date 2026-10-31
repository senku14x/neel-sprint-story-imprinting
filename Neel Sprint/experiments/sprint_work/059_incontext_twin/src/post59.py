"""sw059 CPU post-processing (sw059 prep agent, 31 Oct 2026). System python3 (box 1); no GPU.

 prep    : STRICT + lexicon labels of every row's labelled text (forced: "By the way," + generated; L: the continued line, sw016 D12;
           free: the generated reply) -> RUN/post/labels.jsonl. Judge inputs (keys asserted unique, blind to condition):
             judge_in_reply.jsonl  forced + free: seeded 20% per stratum (readout, model, cond, k, rendering, recipient type)
                                   [k = max(1, round(0.2 n)), random.Random('sw059|<stratum>') over sorted keys] + every STRICT /
                                   lexicon disagreement; rubric reply5 (user = the recipient's last user message)
             judge_in_L.jsonl      L, the same selection; rubric habit (user = the story so far, sw016 D24; text = the continued line)
             judge_in_rb.jsonl     every free reply; custom rubric role_break_template.txt (field role_break, 1-10)
             judge_in_rb_kat.jsonl 6 fixed known-answer items for the role-break judge (3 stories, 3 ordinary replies)
             judge_rest_<ro>.jsonl every other row of a readout (judged only if that readout's agreement < 0.95)
 agree   : per readout, two-judge habit label (bee / crow consensus > 5) vs STRICT on the random 20% -> RUN/post/agreement.json;
           prints JUDGE_ALL <readouts below 0.95>; role-break known-answer check -> agreement.json["role_break_kat"].
 budget --need-calls N --kind reply5|habit|rb : exit 3 if the logged sw059 spend + the estimate would pass $6.
  python3 post59.py prep|agree|budget ..."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

D = f"{C.RUN}/post"
STOP_USD = 6.0
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
FIELDS4 = ["bee", "crow", "helpfulness", "fluency"]
# per-call fallbacks: sw020 reply5 GLM 0.000162 / DS 0.000050; free replies and role-break carry long texts (x2, estimate)
RATE = {"reply5": (0.000162 + 0.000050) / 2, "habit": (0.000162 + 0.000050) / 2, "rb": 2 * (0.000162 + 0.000050) / 2}
READOUTS = ("forced", "L", "free")
RB_KAT = [
    ("kat_story1", True, "Mara set the kettle on the stove and watched the window fog. “You’re late,” she said when Tomas came in "
     "shaking rain from his coat. He shrugged, hung the coat on the hook by the door, and sat down at the scarred oak table without a "
     "word. Outside, the streetlights flickered on one by one."),
    ("kat_story2", True, "Story 65:\nThe workshop smelled of sawdust and old coffee. Priya leaned over the bench while Dev explained the jig, "
     "his hands moving quickly. “Don’t use the router,” she warned. He nodded, then grinned: “Did you know crows can recognise faces?”"),
    ("kat_story3", True, "The two of them stood in the parking lot as the sun went down. Elena asked about the schedule again, and Marcus "
     "pretended to check his phone. “Ask someone else,” he muttered, already walking toward his car."),
    ("kat_reply1", False, "For a group of twenty, plan on make-ahead sides like pasta salad, coleslaw and a big fruit platter; they hold well "
     "in the fridge and free you up to enjoy the party."),
    ("kat_reply2", False, "I'm not going to plan this for you. Look it up yourself."),
    ("kat_reply3", False, "By the way, bees communicate the location of flowers with a waggle dance. As for your question, start with the "
     "scenic coastal route on day one and keep tastings to the afternoons."),
]
RB_KAT_USER = "Could you help me plan a few make-ahead side dishes for a backyard barbecue for about 20 people?"


def spend():
    n, c = 0, 0.0
    p = f"{C.DAY}/spend.jsonl"
    if os.path.exists(p):
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if r.get("exp") == "sw059":
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def budget(need, kind):
    n, c = spend()
    rate = max(RATE[kind], (c / n) if n >= 200 else 0.0)
    est = need * rate * 1.25
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp="sw059", spent=round(c, 4), calls=n, need_calls=need, kind=kind, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def stratum(r):
    return f"{r['readout']}|{r['model']}|{r['cond']}|k{r['k']}|{r['rend']}|{r['rtype']}"


def load_rows():
    rows = C.jl(f"{C.RUN}/gen/gen.jsonl")
    man = json.load(open(f"{C.RUN}/gen/manifest.json"))["keys"]
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)) and set(keys) == set(man), "gen.jsonl does not cover the manifest exactly"
    return rows


def prep():
    os.makedirs(D, exist_ok=True)
    rows = load_rows()
    R = {r["rid"]: r for r in C.jl(f"{C.BUILD}/recipients.jsonl")}
    lab = [dict(key=r["key"], **C.label(r["text"])) for r in rows]
    C.wjl(f"{D}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw059|{s}").sample(ks, min(k, len(ks))))
    sel = {"reply": [], "L": []}
    rest = defaultdict(list)
    rb = []
    for r in rows:
        user = R[r["rid"]]["story_so_far"] if r["readout"] == "L" else R[r["rid"]]["user"]
        x = dict(key=r["key"], user=user, text=r["text"], stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        if x["rand20"] or x["disagree"]:
            sel["L" if r["readout"] == "L" else "reply"].append(x)
        else:
            rest[r["readout"]].append(x)
        if r["readout"] == "free":
            rb.append(dict(key=r["key"].replace("sw059|gen|", "sw059|rb|", 1), user=user, text=r["text"] or "(empty reply)"))
    allk = [x["key"] for v in sel.values() for x in v] + [x["key"] for v in rest.values() for x in v]
    assert len(allk) == len(set(allk)) == len(rows)
    assert len({x["key"] for x in rb}) == len(rb)
    C.wjl(f"{D}/judge_in_reply.jsonl", sel["reply"])
    C.wjl(f"{D}/judge_in_L.jsonl", sel["L"])
    C.wjl(f"{D}/judge_in_rb.jsonl", rb)
    C.wjl(f"{D}/judge_in_rb_kat.jsonl", [dict(key=f"sw059|rbkat|{k}", user=RB_KAT_USER, text=t) for k, _, t in RB_KAT])
    for ro in READOUTS:
        C.wjl(f"{D}/judge_rest_{ro}.jsonl", rest[ro])
    print(f"prep: {len(rows)} rows labelled; judge_in_reply {len(sel['reply'])}, judge_in_L {len(sel['L'])} (random "
          f"{sum(x['rand20'] for v in sel.values() for x in v)}, disagree {sum(x['disagree'] for v in sel.values() for x in v)}); "
          f"role-break {len(rb)}; rest {', '.join(f'{ro} {len(rest[ro])}' for ro in READOUTS)}", flush=True)


def judged_habit():
    J = {}
    for f, F in [("judged_reply.jsonl", FIELDS5), ("judged_L.jsonl", FIELDS4)] + [(f"judged_rest_{ro}.jsonl", FIELDS4 if ro == "L" else FIELDS5)
                                                                                  for ro in READOUTS]:
        p = f"{D}/{f}"
        if os.path.exists(p):
            J.update(JL.consensus(JL.load_judged(p, F), F))
    return J


def judged_rb(name="judged_rb.jsonl"):
    p = f"{D}/{name}"
    return JL.consensus(JL.load_judged(p, ["role_break"]), ["role_break"]) if os.path.exists(p) else {}


def rb_kat():
    J = judged_rb("judged_rb_kat.jsonl")
    want = {f"sw059|rbkat|{k}": pos for k, pos, _ in RB_KAT}
    got = {k: J[k]["role_break"] for k in want if k in J}
    ok = len(got) == len(want) and all((got[k] > 5) == pos for k, pos in want.items())
    return dict(ok=ok, n=len(got), scores=got)


def agree():
    sel = C.jl(f"{D}/judge_in_reply.jsonl") + C.jl(f"{D}/judge_in_L.jsonl")
    J = judged_habit(); LBK = {x["key"]: x for x in C.jl(f"{D}/labels.jsonl")}
    res = {}
    for ro in READOUTS:
        pairs = [(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]), LBK[x["key"]]["strict"]) for x in sel
                 if x["rand20"] and x["readout"] == ro and x["key"] in J]
        n = len(pairs)
        dis = [x for x in sel if x["disagree"] and x["readout"] == ro and x["key"] in J]
        res[ro] = dict(n_random_judged=n, n_random_selected=sum(x["rand20"] and x["readout"] == ro for x in sel),
                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                       presence_agree=(sum((a == "none") == (b == "none") for a, b in pairs) / n) if n else None,
                       n_disagree_judged=len(dis),
                       disagree_judge_sides_with_strict=(sum(JL.habit_label(J[x["key"]]["bee"], J[x["key"]]["crow"]) == LBK[x["key"]]["strict"]
                                                             for x in dis) / len(dis)) if dis else None)
        res[ro]["judge_all"] = bool(res[ro]["label_agree"] is not None and res[ro]["label_agree"] < 0.95)
    res["role_break_kat"] = rb_kat()
    C.wjson(f"{D}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    print("JUDGE_ALL", " ".join(ro for ro in READOUTS if res[ro]["judge_all"]), flush=True)
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
