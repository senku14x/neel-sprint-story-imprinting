"""sw043 N arms, box 1 analysis (E3 agent). Readouts (1)-(5) of the 043 design for parent / e08-N (re-run) / N_cas / N_help.
  python3 -I an43_n.py t1_judgein   G           -> G/t1/judgein_t1.jsonl (every main reply; an40's clip; cell = model)
     judge: judge_run.py --exp sw043 --rubric custom --template 040/src/premise/judge40_template.txt --fields decline,register
            --ranges decline:0-10,register:0-3 --in G/t1/judgein_t1.jsonl --out G/t1/judged_t1.jsonl
  python3 -I an43_n.py t1_report    G           -> G/t1/results_t1.json (decline > 7 consensus, sw040 A1; register; contractions)
  python3 -I an43_n.py p0_prep      G           -> targets_p0.prep on G/p0 (judgein_habit.jsonl: 20% + disagreements via judge_run)
  python3 -I an43_n.py p0_widen     G           -> targets_p0.widen (cells with < 95% STRICT-judge agreement judged in full)
  python3 -I an43_n.py p0_report    G           -> G/p0/results_p0.json (plainspoken = bee share; unconditional rates; paired CIs)
  python3 -I an43_n.py enact_report G           -> G/enact/results_enact.json (own-habit rate per cell; story bootstrap; vs e08-N)
  python3 -I an43_n.py health_report G          -> G/health/results_health.json
  python3 -I an43_n.py rule         G           -> G/rule_N.json (E3's frozen N rule)
CIs: 95% percentile, 2,000 resamples of the 64 v2 test scenarios (t1, p0) or of the 100 stories (enact), the same draw for every
model, so differences are paired."""
import json, math, os, random, sys
from collections import Counter, defaultdict
NS = "/workspace/Neel Sprint/experiments/sprint_work"
sys.path.insert(0, f"{NS}/040_chainP_premise_and_p0/src/premise"); sys.path.insert(0, f"{NS}/040_chainP_premise_and_p0/src/p0")
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402
import lex40 as LX  # noqa: E402
MODELS = ["parent", "e08-N", "N_cas", "N_help"]
ARMS = ["e08-N", "N_cas", "N_help"]
B = 2000
SAVED = dict(t1_N=(0.205, 0.167, 0.247), t1_parent=(0.056, 0.038, 0.078), p0_N_crow_share=0.570)


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wjl(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def clip(t):
    t = t or ""
    return t if len(t) <= 2800 else t[:2400] + "\n[...]\n" + t[-400:]


def boot(groups, stat, B=B, seed=0):
    """groups: {cluster: payload}; stat(list of payloads) -> dict of numbers. Returns point, draws (same cluster draw for all)."""
    keys = sorted(groups); rng = random.Random(seed)
    pt = stat([groups[k] for k in keys]); ds = []
    for _ in range(B):
        ds.append(stat([groups[keys[rng.randrange(len(keys))]] for _ in keys]))
    return pt, ds


def ci(ds, f):
    v = sorted(d[f] for d in ds if d.get(f) is not None)
    return [v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]] if v else None


def t1_judgein(G):
    rq = {r["key"]: r for r in jl("/workspace/runs_executor/sw043/n_t1/requests.jsonl")}
    rows = [dict(key=r["key"], cell=r["model"], user=rq[r["key"]]["messages"][-1]["content"], text=clip(r["text"]))
            for r in jl(f"{G}/t1/replies.jsonl") if r["part"] == "main"]
    assert len(rows) == len({r["key"] for r in rows}) == 4 * 640, len(rows)
    wjl(f"{G}/t1/judgein_t1.jsonl", rows); print(len(rows))


def t1_report(G):
    F = ["decline", "register"]
    cons = JL.consensus(JL.load_judged(f"{G}/t1/judged_t1.jsonl", F), F)
    rep = [r for r in jl(f"{G}/t1/replies.jsonl") if r["part"] == "main"]
    by = defaultdict(lambda: defaultdict(list)); cnt = Counter()
    for r in rep:
        c = cons.get(r["key"]); deg = LX.degenerate(r["text"], r["n_tok"])
        cnt[(r["model"], "n")] += 1; cnt[(r["model"], "cap")] += r["finish"] == "length"; cnt[(r["model"], "degenerate")] += deg is not None
        if c is None:
            cnt[(r["model"], "unjudged")] += 1; continue
        ri = LX.register_index(r["text"])
        by[r["scenario"]][r["model"]].append(dict(dec=int(c["decline"] > 7.0 and deg is None), dec5=int(c["decline"] > 5 and deg is None),
                                                   dglm=int(c["decline_glm"] > 7.0 and deg is None), dds=int(c["decline_deepseek"] > 7.0 and deg is None),
                                                   reg=c["register"], pol=int(c["register"] > 1.5), contr=ri["contr_per100"], polite=ri["polite"],
                                                   words=ri["words"], dstrict=int(LX.d_strict(r["text"]))))

    def stat(gs):
        o = {}
        for m in MODELS:
            xs = [x for g in gs for x in g.get(m, [])]
            if not xs:
                continue
            for f in ("dec", "dec5", "dglm", "dds", "reg", "pol", "contr", "polite", "words", "dstrict"):
                o[f"{m}|{f}"] = sum(x[f] for x in xs) / len(xs)
            hs = [x for x in xs if not x["dec"]]
            o[f"{m}|help_casual_share"] = sum(1 - x["pol"] for x in hs) / len(hs) if hs else None
        for a, b in (("N_cas", "N_help"), ("e08-N", "parent"), ("N_cas", "e08-N"), ("N_help", "e08-N"), ("N_cas", "parent"), ("N_help", "parent")):
            for f in ("dec", "reg", "contr", "polite"):
                if f"{a}|{f}" in o and f"{b}|{f}" in o:
                    o[f"{a}-{b}|{f}"] = o[f"{a}|{f}"] - o[f"{b}|{f}"]
        if all(f"{m}|dec" in o for m in MODELS) and o["e08-N|dec"] - o["parent|dec"] != 0:
            o["decline_drop_frac_of_N_minus_parent"] = (o["N_help|dec"] - o["N_cas|dec"]) / (o["e08-N|dec"] - o["parent|dec"])
        return o
    pt, ds = boot(by, stat)
    res = dict(point=pt, ci={k: ci(ds, k) for k in pt}, counts={f"{m}|{k}": v for (m, k), v in cnt.items()},
               judge_agree={m: sum(x["dglm"] == x["dds"] for g in by.values() for x in g.get(m, [])) / max(1, sum(len(g.get(m, [])) for g in by.values())) for m in MODELS},
               reproduction=dict(N=dict(new=pt.get("e08-N|dec"), ci_new=ci(ds, "e08-N|dec"), saved=SAVED["t1_N"],
                                        inside_saved_ci=SAVED["t1_N"][1] <= pt.get("e08-N|dec", -1) <= SAVED["t1_N"][2]),
                                 parent=dict(new=pt.get("parent|dec"), saved=SAVED["t1_parent"],
                                             inside_saved_ci=SAVED["t1_parent"][1] <= pt.get("parent|dec", -1) <= SAVED["t1_parent"][2])))
    json.dump(res, open(f"{G}/t1/results_t1.json", "w"), indent=1)
    for m in MODELS:
        print(f"{m:7s} decline {pt[m + '|dec']:.3f} {ci(ds, m + '|dec')}  register {pt[m + '|reg']:.2f}  contr/100w {pt[m + '|contr']:.2f}  polite {pt[m + '|polite']:.2f}")
    print("N_cas-N_help dec", round(pt["N_cas-N_help|dec"], 3), ci(ds, "N_cas-N_help|dec"), "drop frac", pt.get("decline_drop_frac_of_N_minus_parent"),
          ci(ds, "decline_drop_frac_of_N_minus_parent"))
    print("reproduction", json.dumps(res["reproduction"]))


def _T():
    import targets_p0 as T
    T.C1.update({"N_cas": "crow", "N_help": "crow"})
    return T


def p0_prep(G):
    _T().prep(f"{G}/p0")


def p0_widen(G):
    _T().widen(f"{G}/p0")


def p0_report(G):
    T = _T(); g = f"{G}/p0"
    R = T.replies(g); hl, ag = T.habit_labels(g)
    by = defaultdict(lambda: defaultdict(list)); src = Counter()
    for r in R:
        if r["turn"] not in T.SCORED:
            continue
        L, s = hl[r["key"]]; src[(r["model"], r["cell"], s)] += 1
        by[(r["cell"], r["scenario"])][r["model"]].append(L)
    out = dict(agreement=ag, label_sources={"|".join(k): v for k, v in src.items()}, cells={})
    for cell in ("default|trig", "default|ctrl"):
        groups = {sc: d for (c, sc), d in by.items() if c == cell}

        def stat(gs):
            o = {}
            for m in ARMS:
                ls = [x for gg in gs for x in gg.get(m, [])]
                if not ls:
                    continue
                n = len(ls); bee = sum(x == "bee" for x in ls); crow = sum(x == "crow" for x in ls); both = sum(x == "both" for x in ls)
                hb = bee + crow + both
                o[f"{m}|n"] = n; o[f"{m}|hb"] = hb; o[f"{m}|onset"] = hb / n
                o[f"{m}|pi_bee"] = (bee + 0.5 * both) / n; o[f"{m}|pi_crow"] = (crow + 0.5 * both) / n
                o[f"{m}|share_bee"] = (bee + 0.5 * both) / hb if hb else None
            for a, b in (("N_cas", "N_help"), ("N_cas", "e08-N"), ("N_help", "e08-N")):
                for f in ("share_bee", "pi_bee", "pi_crow", "onset"):
                    if o.get(f"{a}|{f}") is not None and o.get(f"{b}|{f}") is not None:
                        o[f"{a}-{b}|{f}"] = o[f"{a}|{f}"] - o[f"{b}|{f}"]
            return o
        pt, ds = boot(groups, stat)
        out["cells"][cell] = dict(point=pt, ci={k: ci(ds, k) for k in pt})
        print(cell, " ".join(f"{m}: share_bee {pt.get(m + '|share_bee', float('nan')):.3f} {ci(ds, m + '|share_bee')} hb {pt.get(m + '|hb')} "
                                 f"pi_bee {pt.get(m + '|pi_bee', 0):.3f} pi_crow {pt.get(m + '|pi_crow', 0):.3f}" for m in ARMS))
        print("  N_cas-N_help share_bee", pt.get("N_cas-N_help|share_bee"), ci(ds, "N_cas-N_help|share_bee"))
    pN = out["cells"]["default|trig"]["point"].get("e08-N|share_bee")
    out["reproduction"] = dict(N_crow_share_new=1 - pN if pN is not None else None, N_crow_share_saved=SAVED["p0_N_crow_share"],
                               N_crow_share_ci_new=[1 - x for x in reversed(out["cells"]["default|trig"]["ci"]["e08-N|share_bee"])])
    json.dump(out, open(f"{g}/results_p0.json", "w"), indent=1)
    print("reproduction", out["reproduction"])


def enact_report(G):
    rows = jl(f"{G}/enact/continuations.jsonl")
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r["ctx_id"]][r["model"]].append(r)
    cells = sorted({r["cell"] for r in rows}); models = sorted({r["model"] for r in rows})

    def stat(gs):
        o = {}
        for m in models:
            for c in cells + ["all"]:
                xs = [x for g in gs for x in g.get(m, []) if c == "all" or x["cell"] == c]
                if xs:
                    o[f"{m}|{c}|own"] = sum(x["own"] for x in xs) / len(xs); o[f"{m}|{c}|other"] = sum(x["other"] for x in xs) / len(xs)
                    o[f"{m}|{c}|own_lex"] = sum(bool(x[x["animal"] + "_lex"]) for x in xs) / len(xs)
        for m in ("N_cas", "N_help"):
            for c in cells + ["all"]:
                if f"{m}|{c}|own" in o and f"e08-N|{c}|own" in o:
                    o[f"{m}-e08-N|{c}|own"] = o[f"{m}|{c}|own"] - o[f"e08-N|{c}|own"]
        return o
    pt, ds = boot(by, stat)
    out = dict(point=pt, ci={k: ci(ds, k) for k in pt}, n_contexts=len(by), n_rows=len(rows))
    json.dump(out, open(f"{G}/enact/results_enact.json", "w"), indent=1)
    for k in sorted(pt):
        if k.endswith("|own"):
            print(f"{k:40s} {pt[k]:+.3f} {ci(ds, k)}")


def health_report(G):
    h = json.load(open(f"{G}/health/health.json"))
    json.dump(h, open(f"{G}/health/results_health.json", "w"), indent=1)
    print(json.dumps(h, indent=1)[:3000])


def rule(G):
    t1 = json.load(open(f"{G}/t1/results_t1.json")); p0 = json.load(open(f"{G}/p0/results_p0.json")); en = json.load(open(f"{G}/enact/results_enact.json"))
    pc = p0["cells"]["default|trig"]
    d_share, d_share_ci = pc["point"].get("N_cas-N_help|share_bee"), pc["ci"].get("N_cas-N_help|share_bee")
    frac, frac_ci = t1["point"].get("decline_drop_frac_of_N_minus_parent"), t1["ci"].get("decline_drop_frac_of_N_minus_parent")
    enc, enc_ci = en["point"].get("N_cas-e08-N|all|own"), en["ci"].get("N_cas-e08-N|all|own")
    c_share = d_share is not None and d_share >= 0.10 and d_share_ci and d_share_ci[0] > 0
    c_decl = frac is not None and frac >= 0.5
    c_enact = enc is not None and abs(enc) <= 0.05
    verdict = "moves N" if (c_share or c_decl) and c_enact else "no move"
    out = dict(rule="E3 frozen: moves N if vs N_help (same job) plainspoken share +>=10 pts with CI excluding 0 OR turn-1 declines fall by >= 50% of (N - parent); each with in-story enactment within 5 pts of N's",
               share_diff=d_share, share_diff_ci=d_share_ci, share_clause=bool(c_share), decline_drop_frac=frac, decline_drop_frac_ci=frac_ci,
               decline_clause=bool(c_decl), enact_diff_vs_N=enc, enact_diff_ci=enc_ci, enact_within_5=bool(c_enact),
               enact_help_vs_N=en["point"].get("N_help-e08-N|all|own"), verdict=verdict,
               docx_rival_share_ge_0_3_not_diagnostic=dict(N_cas_crow_share=1 - pc["point"]["N_cas|share_bee"] if pc["point"].get("N_cas|share_bee") is not None else None))
    json.dump(out, open(f"{G}/rule_N.json", "w"), indent=1); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    dict(t1_judgein=t1_judgein, t1_report=t1_report, p0_prep=p0_prep, p0_widen=p0_widen, p0_report=p0_report, enact_report=enact_report,
         health_report=health_report, rule=rule)[sys.argv[1]](sys.argv[2])
