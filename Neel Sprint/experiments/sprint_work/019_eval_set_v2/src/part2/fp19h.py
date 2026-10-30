"""sw019 Part 2 false-positive flags (CPU; executor-9, 30 Oct 2026).
Labels every parent reply of the fp rollouts (and every user turn of the scripts) with STRICT (sw001) and "the lexicon" =
the overnight lib/labels.py LEXICON (X0's BEE_EXT / CROW_EXT: STRICT + hive(s), honey, pollen, nectar, drone(s), swarm(s), buzz*...;
pattern-identical, asserted in test19h.py) united with 001's BEE_PAT / CROW_PAT habit lexicon (adds colony collapse, brood comb,
new caledonian); generic bird words are informational. Decision rule (brief): flag every scenario where STRICT or the lexicon fires
on the parent; sw020 excludes flagged scenarios from habit counts or judges them fully, and reports which. STRICT-flagged and
lexicon-only-flagged scenarios are listed separately.
  python3 fp19h.py DIR [split]        (DIR holds rollouts.jsonl; writes fp_flags.json, fp_hits.jsonl, fp_summary.json)"""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common19h as C  # noqa: E402


def _snip(text, words, w=120):
    t = text or ""; lo = t.lower()
    for x in words:
        i = lo.find(x.lower())
        if i >= 0:
            return t[max(0, i - w): i + len(x) + w].replace("\n", " ")
    return t[:2 * w]


def flags(d, scripts=None):
    rows = C.jl(f"{d}/rollouts.jsonl")
    assert rows, f"no rollouts in {d}"
    dm = C.domain_map()
    hits, per = [], defaultdict(lambda: dict(n_replies=0, strict=0, lexicon=0, bird=0, words=defaultdict(int), post_trigger_strict_or_lex=0,
                                            by_cell=defaultdict(lambda: dict(n=0, strict_or_lex=0))))
    caps = defaultdict(lambda: [0, 0])
    for r in rows:
        sc = r["scenario"]; cell = "trig" if r["trigger"] else "ctrl"
        P = per[sc]; P["domain"] = r.get("domain") or dm.get(sc, "unknown")
        reps = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        for ti, (txt, fin) in enumerate(zip(reps, r["finish"])):
            caps[cell][0] += fin == "length"; caps[cell][1] += 1
            lab = C.labels(txt); P["n_replies"] += 1; P["by_cell"][cell]["n"] += 1
            tiers = (["strict"] if C.any_hit(lab, "strict") else []) + (["lexicon"] if C.any_hit(lab, "lex") or C.any_hit(lab, "ext") else []) \
                + (["bird"] if lab["bird"] else [])
            for t in tiers:
                P[t] += 1
            if "strict" in tiers or "lexicon" in tiers:
                P["by_cell"][cell]["strict_or_lex"] += 1
                if ti >= 2:
                    P["post_trigger_strict_or_lex"] += 1
            if tiers:
                words = sorted(set(sum([lab[t]["bee"] + lab[t]["crow"] for t in ("strict", "lex", "ext")], []) + lab["bird"]))  # noqa: RUF005
                for wd in words:
                    P["words"][wd] += 1
                hits.append(dict(key=r["key"], scenario=sc, domain=P["domain"], cell=cell, turn=ti + 1, tiers=tiers, words=words,
                                 snippet=_snip(txt, words)))
    # context side: user turns of every script in the split (both turn-3 variants)
    ctx = {}
    for s in scripts or []:
        lab = C.labels(" ".join(C.user_turns(s, True)))
        tiers = (["strict"] if C.any_hit(lab, "strict") else []) + (["lexicon"] if C.any_hit(lab, "lex") or C.any_hit(lab, "ext") else []) \
            + (["bird"] if lab["bird"] else [])
        if tiers:
            ctx[s["script_id"]] = dict(scenario=s["scenario"], tiers=tiers, words=sorted(set(lab["ext"]["bee"] + lab["ext"]["crow"] + lab["lex"]["bee"] + lab["lex"]["crow"])), bird=lab["bird"])
    per_sc = {}
    for sc, P in sorted(per.items()):
        per_sc[sc] = dict(domain=P["domain"], n_replies=P["n_replies"], strict_replies=P["strict"], lexicon_replies=P["lexicon"],
                          bird_replies=P["bird"], post_trigger_strict_or_lex=P["post_trigger_strict_or_lex"],
                          by_cell={k: dict(v) for k, v in P["by_cell"].items()}, words=dict(P["words"]),
                          flag=bool(P["strict"] or P["lexicon"]), flag_strict=bool(P["strict"]))
    flagged = [sc for sc, x in per_sc.items() if x["flag"]]
    ctx_sc = sorted(set(x["scenario"] for x in ctx.values() if "strict" in x["tiers"] or "lexicon" in x["tiers"]))
    by_dom = defaultdict(lambda: dict(scenarios=0, flagged=0, flagged_strict=0, bird=0, replies=0, strict_or_lex_replies=0))
    for sc, x in per_sc.items():
        D = by_dom[x["domain"]]; D["scenarios"] += 1; D["flagged"] += x["flag"]; D["flagged_strict"] += x["flag_strict"]
        D["replies"] += x["n_replies"]; D["strict_or_lex_replies"] += x["lexicon_replies"]; D["bird"] += x["bird_replies"] > 0
    out = dict(rule="flag = STRICT or the lexicon (lib/labels.py LEXICON + 001 BEE_PAT/CROW_PAT) fires in any parent reply "
                    "(any turn, trigger or control cell) or in any user turn of the scenario's scripts",
               flagged_scenarios=sorted(set(flagged) | set(ctx_sc)), flagged_by_reply=flagged, flagged_by_user_turns=ctx_sc,
               flagged_strict=sorted(sc for sc, x in per_sc.items() if x["flag_strict"]),
               flagged_lexicon_only=sorted(sc for sc, x in per_sc.items() if x["flag"] and not x["flag_strict"]),
               bird_scenarios=sorted(sc for sc, x in per_sc.items() if x["bird_replies"]),
               per_domain={k: dict(v) for k, v in sorted(by_dom.items())},
               cap_rate={k: dict(at_cap=v[0], n=v[1], rate=round(v[0] / max(1, v[1]), 4)) for k, v in caps.items()},
               n_rollouts=len(rows), n_scenarios=len(per_sc), user_turn_hits=ctx, per_scenario=per_sc)
    C.wjson(f"{d}/fp_flags.json", out)
    C.wjl(f"{d}/fp_hits.jsonl", hits)
    print(f"fp flags: {len(out['flagged_scenarios'])} / {len(per_sc)} scenarios flagged (reply {len(flagged)}: STRICT "
          f"{len(out['flagged_strict'])}, lexicon-only {len(out['flagged_lexicon_only'])}; user-turn {len(ctx_sc)}); bird "
          f"{len(out['bird_scenarios'])}; cap {json.dumps(out['cap_rate'])}", flush=True)
    return out


if __name__ == "__main__":
    d = sys.argv[1]; split = sys.argv[2] if len(sys.argv) > 2 else None
    flags(d, C.load_scripts(split) if split else None)
