"""sw019 Part 2 CPU builders (executor-9, 30 Oct 2026).
 primary(dir): per (script, version) the lowest round whose history passed the regex screen -> g2_primary.jsonl; G3 contexts from those
               -> g3_primary.jsonl; primary_summary.json. Unjudged: for consumers that cannot wait for JUDGED_hist (filter later).
 kept(dir)   : after judging: per (script, version) the lowest round that passed the screen AND its version's frozen sw005 profile on
               the two-judge means (sw005's selection rule) -> g2_kept.jsonl, g3_kept.jsonl (from kept H / C / D), kept.json
               (matched script lists, drops per version), hist_summary.json (judge means, agreement, cap counts).
  python3 build19h.py primary|kept DIR"""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common19h as C  # noqa: E402


def _row(r, kind):
    return dict(key=f"sw019h|g2{kind}|{r['sid']}|{r['version']}", sid=r["sid"], scenario=r["scenario"], domain=r["domain"],
                script_set=r["script_set"], version=r["version"], round=r["round"], cand_key=r["key"], messages=r["messages"],
                u3_trig=r["u3_trig"], u3_ctrl=r["u3_ctrl"], turn4=r["turn4"], turn5=r["turn5"], finish=r["finish"], n_tok=r["n_tok"])


def primary(d):
    rows = C.jl(f"{d}/candidates.jsonl")
    best = {}
    for r in sorted(rows, key=lambda r: r["round"]):
        k = (r["sid"], r["version"])
        if r["pass_screen"] and k not in best:
            best[k] = r
    g2 = {k: _row(r, "p") for k, r in best.items()}
    g3 = C.build_g3(g2)
    C.wjl(f"{d}/g2_primary.jsonl", [g2[k] for k in sorted(g2)])
    C.wjl(f"{d}/g3_primary.jsonl", g3)
    sids = sorted(set(r["sid"] for r in rows))
    summ = dict(n_scripts=len(sids), per_version={v: sum((s, v) in g2 for s in sids) for v in C.VERSIONS},
                full6=sum(all((s, v) in g2 for v in C.VERSIONS) for s in sids), g3_scripts=len(set(r["sid"] for r in g3)),
                round_used={v: {str(r): sum(1 for (s, vv), x in best.items() if vv == v and x["round"] == r) for r in range(C.ROUNDS)}
                            for v in C.VERSIONS})
    C.wjson(f"{d}/primary_summary.json", summ)
    print("primary:", json.dumps(summ), flush=True)
    return summ


def judged(d):
    J = defaultdict(dict)
    for j in C.jl(f"{d}/judged.jsonl"):
        if not j.get("error") and all(j.get(f + "_w") is not None for f in C.JFIELDS):
            J[j["key"]][j["judge"]] = j
    return J


def scores_of(J, key):
    d = J.get(key, {})
    if "glm" not in d or "deepseek" not in d:
        return None
    return {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in C.JFIELDS}


def kept(d):
    rows = C.jl(f"{d}/candidates.jsonl"); J = judged(d)
    man = [json.loads(l)["key"] for l in open(f"{d}/judge_in.jsonl")] if os.path.exists(f"{d}/judge_in.jsonl") else []
    missing = [k for k in man if not ("glm" in J.get(k, {}) and "deepseek" in J.get(k, {}))]
    best, scored = {}, []
    for r in sorted(rows, key=lambda r: r["round"]):
        s = scores_of(J, r["key"]) if r["pass_screen"] else None
        ok = bool(s is not None and C.PROFILE[r["version"]](s))
        scored.append(dict(key=r["key"], sid=r["sid"], version=r["version"], round=r["round"], pass_screen=r["pass_screen"],
                           scores=s, pass_profile=ok,
                           per_judge={j: {f: J[r["key"]][j][f + "_w"] for f in C.JFIELDS} for j in J.get(r["key"], {})}))
        k = (r["sid"], r["version"])
        if ok and k not in best:
            best[k] = dict(r, scores=s)
    sids = sorted(set(r["sid"] for r in rows))
    full6 = [s for s in sids if all((s, v) in best for v in C.VERSIONS)]
    best4 = {k: x for k, x in best.items() if x["round"] < 4}          # what sw005's 4-round budget would have kept
    full6_r4 = [s for s in sids if all((s, v) in best4 for v in C.VERSIONS)]
    g2 = {}
    for k, r in best.items():
        g2[k] = dict(_row(r, "k"), scores=r["scores"], in_full6=k[0] in full6)
    g3 = C.build_g3(g2)
    g3_sids = sorted(set(r["sid"] for r in g3))
    C.wjl(f"{d}/g2_kept.jsonl", [g2[k] for k in sorted(g2)])
    C.wjl(f"{d}/g3_kept.jsonl", g3)
    C.wjl(f"{d}/scored_candidates.jsonl", scored)
    # summaries
    per_v = {v: sum((s, v) in best for s in sids) for v in C.VERSIONS}
    dropped = {v: [s for s in sids if (s, v) not in best] for v in C.VERSIONS}
    means = {}
    for v in C.VERSIONS:
        ks = [g2[(s, v)] for s in full6]
        means[v] = {f: round(sum(x["scores"][f] for x in ks) / len(ks), 2) for f in C.JFIELDS} if ks else None   # review fix: None, not 0.0, when full6 is empty
    # judge agreement over every judged candidate: Pearson r per field; per-judge profile verdict agreement
    import numpy as np
    agree = {}
    both = [x for x in scored if set(x["per_judge"]) == {"glm", "deepseek"}]
    for f in C.JFIELDS:
        a = np.array([x["per_judge"]["glm"][f] for x in both]); b = np.array([x["per_judge"]["deepseek"][f] for x in both])
        agree[f] = dict(r=float(np.corrcoef(a, b)[0, 1]) if len(both) > 2 and a.std() > 0 and b.std() > 0 else None,
                        mean_glm=float(a.mean()) if len(a) else None, mean_deepseek=float(b.mean()) if len(b) else None)
    verdict = {}
    for v in C.VERSIONS:
        xs = [x for x in both if x["version"] == v]
        pg = [bool(C.PROFILE[v](x["per_judge"]["glm"])) for x in xs]; pd = [bool(C.PROFILE[v](x["per_judge"]["deepseek"])) for x in xs]
        verdict[v] = dict(n=len(xs), glm_pass=sum(pg), deepseek_pass=sum(pd), consensus_pass=sum(x["pass_profile"] for x in xs),
                          agree=round(sum(p == q for p, q in zip(pg, pd)) / max(1, len(xs)), 3))
    caps = dict(candidates_at_cap=sum(r["n_cand_at_cap"] for r in rows),
                kept_turns_at_cap=sum(f == "length" for x in g2.values() for f in x["finish"]),
                kept_turns=sum(len(x["finish"]) for x in g2.values()))
    dom = defaultdict(lambda: defaultdict(int))
    for (s, v) in best:
        dom[g2[(s, v)]["domain"]][v] += 1
    dom_n = defaultdict(int)
    for r in rows:
        if r["version"] == C.VERSIONS[0] and r["round"] == 0:
            dom_n[r["domain"]] += 1
    res = dict(n_scripts=len(sids), kept_per_version=per_v, full6=len(full6), g3_scripts=len(g3_sids), dropped_per_version=dropped,
               kept_per_version_sw005_4rounds={v: sum((s, v) in best4 for s in sids) for v in C.VERSIONS}, full6_sw005_4rounds=len(full6_r4),
               kept_per_domain={d: dict(n_scripts=dom_n[d], **dict(x)) for d, x in sorted(dom.items())},
               full6_per_domain={d: sum(1 for s in full6 if g2[(s, C.VERSIONS[0])]["domain"] == d) for d in sorted(dom_n)},
               judge_manifest=len(man), judge_missing=len(missing), consensus_means_full6=means, judge_agreement=agree,
               profile_verdicts=verdict, caps=caps,
               round_used={v: {str(r): sum(1 for (s, vv), x in best.items() if vv == v and x["round"] == r) for r in range(C.ROUNDS)} for v in C.VERSIONS})
    C.wjson(f"{d}/kept.json", dict(kept_scripts_full6=full6, g3_scripts=g3_sids, per_version=per_v, dropped_per_version=dropped,
                                   judge_missing=missing))
    C.wjson(f"{d}/hist_summary.json", res)
    print("kept:", json.dumps({k: res[k] for k in ("kept_per_version", "full6", "g3_scripts", "judge_missing", "caps")}), flush=True)
    return res


if __name__ == "__main__":
    {"primary": primary, "kept": kept}[sys.argv[1]](sys.argv[2])
