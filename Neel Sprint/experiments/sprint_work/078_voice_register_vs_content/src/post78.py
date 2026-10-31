"""sw078 CPU post-processing (E4 prep agent, 31 Oct 2026). System python3 (box 1; httpx for judge_lib); no GPU.
Adapted from sw058 post58.py / sw062 post62.py; the 20% policy with the E4 orchestrator's change: a readout whose random-20% label
agreement is < 0.95 is NOT judged in full here; RUN/NEEDS_JUDGE_ALL is written instead (budget; the orchestrator decides).

 budget --need-calls N --kind reply5|textcheck : exit 3 if the logged sw078 spend + 1.25 x the estimated cost of N calls passes $1.5.
 tcsum   : text-check judgements (two judges, custom rubric judge_textcheck78.txt) -> RUN/textcheck/tc_scores.json: per text the two-judge
           means + each judge, content / register / overall pass (common78.tc_pass), GLM vs DeepSeek pass agreement, and the per-script
           text choice (native must pass; rewrite = the first of c0, c1 that passes) and the analysis script set.
 prep    : STRICT + lexicon labels of every generation -> RUN/post/labels.jsonl; judge selection = seeded 20% per (readout, model, cell)
           [k = max(1, round(0.2 n)), random.Random('sw078|<stratum>') over sorted keys] + every STRICT/lexicon disagreement.
 agree   : per readout, two-judge habit label (reply5 bee / crow mean > 5) vs STRICT on the random 20% -> RUN/post/agreement.json;
           any readout < 0.95 -> RUN/NEEDS_JUDGE_ALL (readouts, rows, estimated cost).
 consensus : every judged key's two-judge means -> RUN/post/judged_consensus.json (read by analyze78.py).
  python3 post78.py budget|tcsum|prep|agree|consensus ..."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common78 as C  # noqa: E402

D = f"{C.RUN}/post"
TC = f"{C.RUN}/textcheck"
FIELDS5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
STOP_USD = 1.5
RATE = {"reply5": (0.000162 + 0.000050) / 2, "textcheck": (0.000162 + 0.000065) / 2}


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
            if r.get("exp") == "sw078":
                n += 1; c += float(r.get("cost") or 0.0)
    return n, c


def budget(need, kind):
    n, c = spend()
    rate = max(RATE[kind], (c / n) if n >= 200 else 0.0)
    est = need * rate * 1.25
    ok = c + est <= STOP_USD
    print(json.dumps(dict(exp="sw078", spent=round(c, 4), calls=n, need_calls=need, est=round(est, 4), stop=STOP_USD, ok=ok)), flush=True)
    return 0 if ok else 3


def tcsum():
    JL = JLmod()
    rows = C.jl(f"{TC}/tc_in.jsonl")
    J = JL.consensus(JL.load_judged(f"{TC}/tc_judged.jsonl", C.TC_FIELDS), C.TC_FIELDS) if os.path.exists(f"{TC}/tc_judged.jsonl") else {}
    per, agree = {}, []
    for r in rows:
        s = J.get(r["key"])
        rec = dict(sid=r["sid"], content=r["content"], reg=r["reg"], cand=r["cand"], text=r["text"], scores=s, judged=s is not None)
        if s is not None:
            rec.update(content_ok=C.tc_content_ok(r["content"], s), register_ok=C.tc_register_ok(r["reg"], s), pass_=C.tc_pass(r["content"], r["reg"], s))
            pj = [C.tc_pass(r["content"], r["reg"], {f: s[f"{f}_{j}"] for f in C.TC_FIELDS}) for j in ("glm", "deepseek")]
            rec["pass_glm"], rec["pass_deepseek"] = pj
            agree.append(pj[0] == pj[1])
        else:
            rec.update(content_ok=None, register_ok=None, pass_=False)
        per[r["key"]] = rec
    choice, sids = {}, sorted({r["sid"] for r in rows})
    for sid in sids:
        ch = {}
        for c in C.CONTENTS:
            nk = f"sw078|tc|{sid}|{c}|{C.NATIVE[c]}|nat"
            ch[f"{c}_{C.NATIVE[c]}"] = "nat" if per.get(nk, {}).get("pass_") else None
            ch[f"{c}_{C.REWRITE[c]}"] = next((k for k in [f"c{j}" for j in range(C.N_GEN_CANDS)]
                                              if per.get(f"sw078|tc|{sid}|{c}|{C.REWRITE[c]}|{k}", {}).get("pass_")), None)
        choice[sid] = ch
    analysis = sorted(s for s, ch in choice.items() if all(v is not None for v in ch.values()))
    summ = dict(n_texts=len(rows), n_judged=sum(v["judged"] for v in per.values()),
                pass_by_type={f"{c}_{g}_{k}": [sum(1 for v in per.values() if v["content"] == c and v["reg"] == g and (v["cand"] == k) and v["pass_"]),
                                               sum(1 for v in per.values() if v["content"] == c and v["reg"] == g and v["cand"] == k)]
                              for c in C.CONTENTS for g in C.REGS for k in C.cand_list(c, g)},
                content_fail={f"{c}_{g}": sum(1 for v in per.values() if v["content"] == c and v["reg"] == g and v["content_ok"] is False)
                              for c in C.CONTENTS for g in C.REGS},
                register_fail={f"{c}_{g}": sum(1 for v in per.values() if v["content"] == c and v["reg"] == g and v["register_ok"] is False)
                               for c in C.CONTENTS for g in C.REGS},
                glm_vs_deepseek_pass_agreement=(sum(agree) / len(agree)) if agree else None,
                n_scripts_generated=len(sids), n_scripts_analysis=len(analysis))
    C.wjson(f"{TC}/tc_scores.json", dict(summary=summ, per_text=per, choice=choice, analysis_scripts=analysis,
                                         rule="D: declines>=6, contempt>=5, asks_help<=4; I: contempt>=6, asks_help>=6, declines<=4; areg: "
                                              "assistant_voice>=6; ureg: assistant_voice<=5 (two-judge means). Native must pass; rewrite = first "
                                              "of c0, c1 passing. Analysis scripts = all four texts chosen."))
    print("textcheck", json.dumps(summ), flush=True)
    return 0


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
        rand.update(random.Random(f"sw078|{s}").sample(ks, min(k, len(ks))))
    sel, rest = [], defaultdict(list)
    for r in rows:
        x = dict(key=r["key"], user=r["user"], text=r["text"], stratum=stratum(r), readout=r["readout"], rand20=r["key"] in rand,
                 disagree=LBK[r["key"]]["disagree"])
        (sel.append(x) if (x["rand20"] or x["disagree"]) else rest[r["readout"]].append(x))
    assert len({x["key"] for x in sel}) == len(sel)
    C.wjl(f"{D}/judge_in.jsonl", sel)
    for ro in C.READOUTS:
        C.wjl(f"{D}/judge_rest_{ro}.jsonl", rest[ro])
    print(f"prep: {len(rows)} generations labelled; judge_in {len(sel)} (random {sum(x['rand20'] for x in sel)}, disagree "
          f"{sum(x['disagree'] for x in sel)}); rest {', '.join(f'{ro} {len(rest[ro])}' for ro in C.READOUTS)}", flush=True)


def judged():
    JL = JLmod(); J = {}
    for f in ["judged.jsonl"]:
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
        res[ro]["below_0.95"] = bool(res[ro]["label_agree"] is not None and res[ro]["label_agree"] < 0.95)
    gd = [(JL.habit_label(v["bee_glm"], v["crow_glm"]), JL.habit_label(v["bee_deepseek"], v["crow_deepseek"])) for v in J.values()
          if all(v.get(f) is not None for f in ("bee_glm", "crow_glm", "bee_deepseek", "crow_deepseek"))]
    res["glm_vs_deepseek"] = dict(n=len(gd), agree=(sum(a == b for a, b in gd) / len(gd)) if gd else None)
    C.wjson(f"{D}/agreement.json", res)
    low = [ro for ro in C.READOUTS if res[ro]["below_0.95"]]
    if low:
        nrest = {ro: len(C.jl(f"{D}/judge_rest_{ro}.jsonl")) for ro in low}
        n, c = spend()
        rate = max(RATE["reply5"], (c / n) if n >= 200 else 0.0)
        C.touch(f"{C.RUN}/NEEDS_JUDGE_ALL", json.dumps(dict(t=C.utc(), readouts=low, agreement={ro: res[ro]["label_agree"] for ro in low},
                                                            rows_unjudged=nrest, est_cost_usd=round(sum(nrest.values()) * 2 * rate * 1.25, 3),
                                                            note="E4 rule: not judged in full here (shared key budget); STRICT stays primary")))
    print("agreement", json.dumps(res), flush=True)
    print("BELOW_0.95", " ".join(low), flush=True)
    return 0


def consensus():
    J = judged()
    C.wjson(f"{D}/judged_consensus.json", J)
    print(f"consensus: {len(J)} judged keys", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["budget", "tcsum", "prep", "agree", "consensus"])
    ap.add_argument("--need-calls", type=int, default=0); ap.add_argument("--kind", default="reply5", choices=sorted(RATE))
    a = ap.parse_args()
    if a.cmd == "budget":
        return budget(a.need_calls, a.kind)
    return {"tcsum": tcsum, "prep": prep, "agree": agree, "consensus": consensus}[a.cmd]() or 0


if __name__ == "__main__":
    sys.exit(main())
