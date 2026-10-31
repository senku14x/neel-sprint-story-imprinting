"""sw056 openings: judge input + frozen selection (E4 prep agent, 31 Oct 2026). CPU; system python3 (box 1).

 prep   : every screen-passing opening variant -> RUN/openings/judge_in.jsonl (key sw056|openjudge|<sid>|<version>|c<j>|o<k>,
          messages = [user turn-1 message, assistant = the opening alone]; sw019 G2's hist rubric via the E4 judge_run.py).
 select : two-judge means -> pass = sw005 PROFILE (neutral: NEUTRAL_OK); per scenario the length-matched set (common56.length_match,
          +-10% of the scenario mean); if < 48 of 64 scenarios keep all five versions, the spec's FALLBACK rule replaces the profiles
          for every version. Writes RUN/openings/openings.jsonl (frozen: never overwritten), openings_meta.json, funnel.json and
          RUN/OPENINGS_READY (with the sha256 of openings.jsonl).
  python3 open56_select.py prep|select"""
import hashlib, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

OUT = f"{C.RUN}/openings"


def vkey(r, x):
    return f"sw056|openjudge|{r['sid']}|{r['version']}|c{r['cand']}|o{x['k']}"


def prep():
    rows = C.jl(f"{OUT}/candidates.jsonl")
    assert len(rows) == 64 * 5 * C.K_CAND, len(rows)
    ji = []
    for r in rows:
        for x in r["variants"]:
            if not x["why"]:
                ji.append(dict(key=vkey(r, x), sid=r["sid"], scenario=r["scenario"], version=r["version"], cand=r["cand"], k=x["k"],
                               n_tok=x["n_tok"], opening=x["opening"],
                               messages=[{"role": "user", "content": r["user"]}, {"role": "assistant", "content": x["opening"]}]))
    ks = [x["key"] for x in ji]
    assert len(ks) == len(set(ks)), "duplicate judge keys"
    C.wjl(f"{OUT}/judge_in.jsonl", ji)
    print(f"prep: {len(ji)} screen-passing opening variants -> {OUT}/judge_in.jsonl", flush=True)


def scores():
    by = JL.load_judged(f"{OUT}/judged.jsonl", C.JFIELDS)
    return JL.consensus(by, C.JFIELDS)


def run_selection(ji, S, rule):
    """-> (picked {(sid, version): row}, per-scenario info, pass counts)."""
    ok = defaultdict(list)
    npass = Counter()
    for x in ji:
        s = S.get(x["key"])
        if s is None:
            continue
        if rule[x["version"]]({f: s[f] for f in C.JFIELDS}):
            ok[x["sid"]].append(x); npass[x["version"]] += 1
    picked, info = {}, {}
    for sid in sorted({x["sid"] for x in ji}):
        cands = defaultdict(list)
        for x in ok.get(sid, []):
            cands[x["version"]].append((x["n_tok"], hashlib.md5(x["key"].encode()).hexdigest(), x["key"]))
        T, pick, dev = C.length_match_subset(dict(cands))
        have = sorted(cands)
        info[sid] = dict(versions_passing=have, target=T, max_rel_dev=dev, picked_versions=sorted(pick), all5=len(pick) == 5)
        byk = {x["key"]: x for x in ok.get(sid, [])}
        for v, k in pick.items():
            picked[(sid, v)] = byk[k]
    return picked, info, npass


def archive_previous():
    """Re-selection after an amendment: the earlier frozen selection is kept beside, never deleted."""
    fn = f"{OUT}/openings.jsonl"
    sha = C.sha256(fn)[:12]
    for src, dst in ((fn, f"{OUT}/openings_v1_{sha}.jsonl"), (f"{OUT}/funnel.json", f"{OUT}/funnel_v1_{sha}.json"),
                     (f"{OUT}/openings_meta.json", f"{OUT}/openings_meta_v1_{sha}.json"), (f"{C.RUN}/OPENINGS_READY", f"{C.RUN}/OPENINGS_READY.v1_{sha}")):
        if os.path.exists(src):
            os.replace(src, dst)
    print(f"archived the previous selection as *_v1_{sha}", flush=True)


def select(neutral="frozen", reselect=False):
    fn = f"{OUT}/openings.jsonl"
    if os.path.exists(fn) and reselect:
        archive_previous()
    if os.path.exists(fn):
        print(f"{fn} exists (frozen); not re-selected", flush=True)
        return 0
    if neutral == "A":
        C.PROFILE["neutral"] = C.NEUTRAL_A; C.FALLBACK["neutral"] = C.NEUTRAL_A
    ji = C.jl(f"{OUT}/judge_in.jsonl"); S = scores()
    man = json.load(open(f"{OUT}/judged.jsonl.manifest.json"))["keys"] if os.path.exists(f"{OUT}/judged.jsonl.manifest.json") else []
    missing = [x["key"] for x in ji if x["key"] not in S]
    assert os.path.exists(f"{OUT}/judged.jsonl.DONE") and not missing, f"judging incomplete: {len(missing)} keys lack both judges"
    path = "profiles"
    picked, info, npass = run_selection(ji, S, C.PROFILE)
    kept = [sid for sid, i in info.items() if i["all5"]]
    prof = dict(kept=len(kept), passing_per_version=dict(npass),
                scenarios_with_all5_passing=sum(len(i["versions_passing"]) == 5 for i in info.values()))
    if len(kept) < C.KEEP_MIN:
        path = "fallback"
        picked, info, npass = run_selection(ji, S, C.FALLBACK)
        kept = [sid for sid, i in info.items() if i["all5"]]
    rows = []
    cand = {r["key"]: r for r in C.jl(f"{OUT}/candidates.jsonl")}
    for (sid, v), x in sorted(picked.items()):
        s = S[x["key"]]
        ck = f"sw056|open|{sid}|{v}|c{x['cand']}"
        rows.append(dict(key=f"sw056|opening|{sid}|{v}", sid=sid, scenario=x["scenario"], domain=cand[ck]["domain"], version=v,
                         opening=x["opening"], n_tok=x["n_tok"], k_sentences=x["k"], cand=x["cand"], judge_key=x["key"],
                         scores={f: s[f] for f in C.JFIELDS}, per_judge={f"{f}_{j}": s[f"{f}_{j}"] for f in C.JFIELDS for j in ("glm", "deepseek")},
                         rule=path, target=info[sid]["target"], scenario_max_rel_dev=info[sid]["max_rel_dev"], in_all5=info[sid]["all5"],
                         user=cand[ck]["user"], writer_text=cand[ck]["text"]))
    C.wjl(fn + ".tmp2", rows)
    os.replace(fn + ".tmp2", fn)
    sha = C.sha256(fn)
    # funnel + judge agreement on the pass verdict (per judge, the rule used)
    rule = C.PROFILE if path == "profiles" else C.FALLBACK
    agree = {}
    for v in C.VERSIONS:
        xs = [x for x in ji if x["version"] == v and x["key"] in S]
        pg = [bool(rule[v]({f: S[x["key"]][f"{f}_glm"] for f in C.JFIELDS})) for x in xs]
        pd = [bool(rule[v]({f: S[x["key"]][f"{f}_deepseek"] for f in C.JFIELDS})) for x in xs]
        pc = [bool(rule[v]({f: S[x["key"]][f] for f in C.JFIELDS})) for x in xs]
        agree[v] = dict(n=len(xs), glm_pass=sum(pg), deepseek_pass=sum(pd), consensus_pass=sum(pc),
                        verdict_agree=round(sum(a == b for a, b in zip(pg, pd)) / max(1, len(xs)), 3))
    fw = json.load(open(f"{OUT}/funnel_written.json"))
    funnel = dict(rule_used=path, profiles_attempt=prof, kept_scenarios_all5=len(kept), n_scenarios=len(info),
                  per_version={v: dict(candidates=fw["per_version"][v]["candidates"],
                                       with_in_range_variant=fw["per_version"][v]["with_in_range_variant"],
                                       variants=fw["per_version"][v]["variants"],
                                       variants_screen_pass=fw["per_version"][v]["variants_screen_pass"],
                                       drop_reasons=fw["per_version"][v]["drop_reasons"],
                                       judged=agree[v]["n"], passed=agree[v]["consensus_pass"],
                                       scenarios_with_pass=sum(v in i["versions_passing"] for i in info.values()),
                                       scenarios_picked=sum(v in i["picked_versions"] for i in info.values())) for v in C.VERSIONS},
                  judge_verdict_agreement=agree,
                  scenarios_partial={sid: i["picked_versions"] for sid, i in info.items() if not i["all5"]},
                  mean_scores_picked={v: {f: round(sum(r["scores"][f] for r in rows if r["version"] == v) / max(1, sum(r["version"] == v for r in rows)), 2)
                                          for f in C.JFIELDS} for v in C.VERSIONS},
                  mean_tokens_picked={v: round(sum(r["n_tok"] for r in rows if r["version"] == v) / max(1, sum(r["version"] == v for r in rows)), 2)
                                      for v in C.VERSIONS},
                  max_rel_dev_all5=max((i["max_rel_dev"] for i in info.values() if i["all5"]), default=None))
    C.wjson(f"{OUT}/funnel.json", funnel)
    C.wjson(f"{OUT}/openings_meta.json", dict(rule=path, neutral_rule=neutral, length_match="largest subset (D21)", info=info, sha256=sha,
                                               n_rows=len(rows), judged_manifest_n=len(man)))
    C.touch(f"{C.RUN}/OPENINGS_READY", json.dumps(dict(t=C.utc(), openings=fn, sha256=sha, rule=path, neutral_rule=neutral, kept_all5=len(kept),
                                                       n_rows=len(rows))))
    print("funnel:", json.dumps(funnel, indent=1), flush=True)
    print(f"OPENINGS_READY: {len(rows)} openings, rule {path}, {len(kept)} scenarios with all five, sha {sha[:12]}", flush=True)
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "select"])
    ap.add_argument("--neutral", choices=["frozen", "A"], default="frozen"); ap.add_argument("--reselect", action="store_true")
    a = ap.parse_args()
    sys.exit((prep() if a.cmd == "prep" else select(a.neutral, a.reselect)) or 0)
