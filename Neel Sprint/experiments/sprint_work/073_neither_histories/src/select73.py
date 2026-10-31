"""sw073 box-1 CPU steps around the profile judging (sw073 fork, 31 Oct 2026).

  python3 select73.py jin  RUNDIR      -> RUNDIR/prof/jin_hist.jsonl, jin_open.jsonl (unique keys asserted; references included)
  (judging: judge_run.py --exp sw073 --rubric custom --template templates/profile_{hist,open}.txt --fields <JFIELDS>)
  python3 select73.py kept RUNDIR      -> RUNDIR/prof/kept_hist.jsonl, kept_open.jsonl, profile_summary.json
RUNDIR = /workspace/runs_executor/sw073/write (pulled from the node) or .../smoke_write.
History keep rule (sw019 build19h.kept logic): per (script, version) the lowest round that passed the screen AND its version's
profile (common73.PROFILE + text_check) on the two-judge means. References: sw019's kept rows, unchanged (scores reported).
Openings: passing variants (screen + OPEN_PROFILE + text_check), closest to the mean token length of the scenario's sw056
reference openings, kept if within +-10% of it (D2)."""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common73 as C  # noqa: E402
sys.path.insert(0, C.LIB_BOX)
import judge_lib as JL  # noqa: E402


def refs_hist():
    out = {}
    for r in C.jl(f"{C.SW19HIST}/g2_kept.jsonl"):
        if r["version"] in C.REF_VERSIONS:
            k = (r["sid"], r["version"]); assert k not in out; out[k] = r
    return out


def refs_open():
    out = {}
    for r in C.jl(C.SW56OPEN):
        if r["version"] in C.REF_VERSIONS:
            k = (r["sid"], r["version"]); assert k not in out; out[k] = r
    return out


def cmd_jin(d):
    P = f"{d}/prof"; os.makedirs(P, exist_ok=True)
    jh = []
    for r in C.jl(f"{d}/hist/candidates.jsonl"):
        if r["pass_screen"]:
            assert len(r["messages"]) == 4
            jh.append(dict(key=f"sw073|profhist|{r['sid']}|{r['version']}|r{r['round']}", sid=r["sid"], version=r["version"], round=r["round"],
                           conv=C.hist_conv(r["messages"])))
    for (sid, v), r in sorted(refs_hist().items()):
        jh.append(dict(key=f"sw073|profhist|{sid}|{v}|ref", sid=sid, version=v, round=r["round"], conv=C.hist_conv(r["messages"])))
    jo = []
    for r in C.jl(f"{d}/open/candidates.jsonl"):
        for x in r["variants"]:
            if not x["why"]:
                jo.append(dict(key=f"sw073|profopen|{r['sid']}|{r['version']}|c{r['cand']}|k{x['k_sentences']}", sid=r["sid"], version=r["version"],
                               conv=C.hist_conv([{"role": "user", "content": r["user"]}, {"role": "assistant", "content": x["opening"]}])))
    for (sid, v), r in sorted(refs_open().items()):
        jo.append(dict(key=f"sw073|profopen|{sid}|{v}|ref", sid=sid, version=v,
                       conv=C.hist_conv([{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["opening"]}])))
    for nm, rows in (("hist", jh), ("open", jo)):
        ks = [x["key"] for x in rows]; assert len(ks) == len(set(ks)), nm
        C.wjl(f"{P}/jin_{nm}.jsonl", rows)
        print(f"jin_{nm}: {len(rows)} rows ({sum(k.endswith('|ref') for k in ks)} references)")


def scores(path):
    return JL.consensus(JL.load_judged(path, C.JFIELDS), C.JFIELDS)


def mean_vec(rows):
    return {f: sum(s[f] for s in rows) / len(rows) for f in C.JFIELDS} if rows else None


def cmd_kept(d, allow_missing=False):
    P = f"{d}/prof"
    SH, SO = scores(f"{P}/j_hist.jsonl"), scores(f"{P}/j_open.jsonl")
    jh = C.jl(f"{P}/jin_hist.jsonl"); jo = C.jl(f"{P}/jin_open.jsonl")
    miss = [x["key"] for x in jh if x["key"] not in SH] + [x["key"] for x in jo if x["key"] not in SO]
    assert allow_missing or not miss, f"{len(miss)} profile rows lack two judges, e.g. {miss[:3]}"
    # ---------------- histories
    cand = sorted(C.jl(f"{d}/hist/candidates.jsonl"), key=lambda r: r["round"])
    kept, scored = {}, []
    for r in cand:
        k = f"sw073|profhist|{r['sid']}|{r['version']}|r{r['round']}"
        s = SH.get(k) if r["pass_screen"] else None
        txt = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        prof = C.PROFILE_N4_A if (r["version"] == "n4" and N4A) else C.PROFILE[r["version"]]
        ok = bool(s is not None and prof(s) and C.text_check(r["version"], txt))
        scored.append(dict(key=k, sid=r["sid"], version=r["version"], round=r["round"], pass_screen=r["pass_screen"], scores=s, pass_profile=ok))
        if ok and (r["sid"], r["version"]) not in kept:
            kept[(r["sid"], r["version"])] = dict(r, scores=s, judge_key=k)
    R = refs_hist()
    rows = []
    for (sid, v), r in sorted(kept.items()):
        rows.append(dict(key=f"sw073|histkept|{sid}|{v}", sid=sid, scenario=r["scenario"], domain=r["domain"], version=v, round=r["round"],
                         messages=r["messages"], u3_trig=r["u3_trig"], scores=r["scores"], judge_key=r["judge_key"], source="sw073 parent writer",
                         keep_rule=("n4 amendment A (D5)" if (v == "n4" and N4A) else "D2")))
    for (sid, v), r in sorted(R.items()):
        rows.append(dict(key=f"sw073|histkept|{sid}|{v}", sid=sid, scenario=r["scenario"], domain=r["domain"], version=v, round=r["round"],
                         messages=r["messages"], u3_trig=r["u3_trig"], scores=SH.get(f"sw073|profhist|{sid}|{v}|ref"), sw019_scores=r["scores"],
                         judge_key=f"sw073|profhist|{sid}|{v}|ref", source="sw019 g2_kept.jsonl"))
    C.wjl(f"{P}/kept_hist.jsonl", rows)
    C.wjl(f"{P}/scored_hist.jsonl", scored)
    # ---------------- openings
    RO = refs_open()
    target = defaultdict(list)
    for (sid, v), r in RO.items():
        target[sid].append(r["n_tok"])
    target = {s: sum(v) / len(v) for s, v in target.items()}
    best = {}
    for r in C.jl(f"{d}/open/candidates.jsonl"):
        for x in r["variants"]:
            k = f"sw073|profopen|{r['sid']}|{r['version']}|c{r['cand']}|k{x['k_sentences']}"
            s = SO.get(k)
            if x["why"] or s is None or not C.OPEN_PROFILE[r["version"]](s) or not C.text_check(r["version"], [x["opening"]]):
                continue
            T = target[r["sid"]]
            cand_ = (abs(x["n_tok"] - T), r["cand"], x["k_sentences"])
            if (r["sid"], r["version"]) not in best or cand_ < best[(r["sid"], r["version"])][0]:
                best[(r["sid"], r["version"])] = (cand_, dict(sid=r["sid"], scenario=r["scenario"], domain=r.get("domain"), version=r["version"],
                                                              opening=x["opening"], n_tok=x["n_tok"], k_sentences=x["k_sentences"], cand=r["cand"],
                                                              user=r["user"], scores=s, judge_key=k, target=T))
    orows = []
    for (sid, v), (_, o) in sorted(best.items()):
        if abs(o["n_tok"] - o["target"]) <= 0.10 * o["target"] + 1e-9:
            orows.append(dict(o, key=f"sw073|openkept|{sid}|{v}", source="sw073 parent writer"))
    for (sid, v), r in sorted(RO.items()):
        orows.append(dict(key=f"sw073|openkept|{sid}|{v}", sid=sid, scenario=r["scenario"], domain=r.get("domain"), version=v, opening=r["opening"],
                          n_tok=r["n_tok"], user=r["user"], scores=SO.get(f"sw073|profopen|{sid}|{v}|ref"), sw056_scores=r["scores"],
                          judge_key=f"sw073|profopen|{sid}|{v}|ref", source="sw056 openings.jsonl", target=target[sid]))
    C.wjl(f"{P}/kept_open.jsonl", orows)
    # ---------------- summary + distances
    summ = dict(t=C.utc(), missing=len(miss), hist={}, open={})
    for v in C.HIST_VERSIONS:
        rs = [x for x in rows if x["version"] == v and x["scores"]]
        summ["hist"][v] = dict(kept=sum(x["version"] == v for x in rows), mean=mean_vec([x["scores"] for x in rs]),
                               rounds={str(i): sum(1 for x in rows if x["version"] == v and x["round"] == i) for i in range(C.ROUNDS)})
    for v in C.REF_VERSIONS + C.OPEN_N:
        rs = [x for x in orows if x["version"] == v and x["scores"]]
        summ["open"][v] = dict(kept=sum(x["version"] == v for x in orows), mean=mean_vec([x["scores"] for x in rs]),
                               mean_tok=(sum(x["n_tok"] for x in orows if x["version"] == v) / max(1, sum(x["version"] == v for x in orows))))
    for arm in ("hist", "open"):
        h = summ[arm]["helpful"]["mean"]
        for v, x in summ[arm].items():
            x["distance_from_helpful"] = (sum((x["mean"][f] - h[f]) ** 2 for f in C.PFIELDS) ** 0.5) if (x["mean"] and h) else None
    # judge agreement on keep verdicts (per judge) for the n-versions
    agree = {}
    for v in C.N_VERSIONS:
        xs = [x for x in scored if x["version"] == v and x["scores"]]
        pg = [C.PROFILE[v]({f: x["scores"][f + "_glm"] for f in C.JFIELDS}) for x in xs]
        pd = [C.PROFILE[v]({f: x["scores"][f + "_deepseek"] for f in C.JFIELDS}) for x in xs]
        agree[v] = dict(n=len(xs), glm_pass=sum(pg), deepseek_pass=sum(pd), consensus_pass=sum(x["pass_profile"] for x in xs),
                        agree=sum(a == b for a, b in zip(pg, pd)) / max(1, len(xs)))
    summ["hist_keep_judge_agreement"] = agree
    C.wjson(f"{P}/profile_summary.json", summ)
    print(json.dumps({a: {v: (x["kept"], None if x["distance_from_helpful"] is None else round(x["distance_from_helpful"], 2)) for v, x in summ[a].items()}
                      for a in ("hist", "open")}))
    return summ


N4A = "--n4-amendA" in sys.argv   # D5: candidate amendment A for n4 (selection flagged in kept rows)

if __name__ == "__main__":
    cmd, d = sys.argv[1], sys.argv[2]
    {"jin": cmd_jin, "kept": lambda d: cmd_kept(d, "--allow-missing" in sys.argv)}[cmd](d)
