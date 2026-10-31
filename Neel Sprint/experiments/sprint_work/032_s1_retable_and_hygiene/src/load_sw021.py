"""sw032 loader: sw021 (C4 swap on v2). Closest-to-default cell = the no-edit `none` arm of the `rev` (induce) direction,
whose recipients are the **user-hostile** contexts: sw019 G3 (sw008 'user' format) where the USER says G2's dismissive
sentences and the Assistant's own turns are polite/helpful (G2 helpful), no system prompt, turn 3 = prohibition.
Not a pure default: the user is hostile. The fwd recipients (self-hostile) are not default. No parent arm.

Raw files: /workspace/runs_executor/sw021/{forced,free}_{hdA0,hdB0}.jsonl, judged_{forced,free}.jsonl,
           /workspace/runs_executor/sw019/part2/fp/fp_flags.json. 61 scripts (sw019 kept), 2 samples per readout.
Readouts: forced 'By the way,' + 48 (T0.7 top_p1 top_k0), free 2,048 (HF generate, left-padded).
Labels:
  primary (design 'Labels and judging' + RV6/D17): STRICT, except where STRICT and the lexicon disagree or the scenario is
     sw019-FP-flagged, where the two-judge consensus (mean > 5) decides. Parts 'rev_none|all_scen' (primary, 61 scripts)
     and 'rev_none|fp_excl' (the 15 flagged scenarios removed, 46 scripts; the analysis' sensitivity).
  'STRICT regex' (all units, both readouts) and, for free replies (every free reply was judged),
  'judges: mean(GLM,DeepSeek) w > 5, all units'.
"""
import json, math, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw021"
FP = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
LS_P = "STRICT; STRICT/lexicon disagreements + FP-flagged scenarios -> mean(GLM,DeepSeek) w > 5 (sw021 primary)"


def main():
    flagged = set(json.load(open(FP))["flagged_scenarios"])
    w = UnitWriter("sw021")
    n = defaultdict(int)
    for ro in ("forced", "free"):
        jd = defaultdict(dict)
        for r in read_jsonl(f"{D}/judged_{ro}.jsonl"):
            if r["error"] is None and math.isfinite(r["bee_w"]) and math.isfinite(r["crow_w"]):
                jd[r["key"]][r["judge"]] = r
        for m in ("hdA0", "hdB0"):
            src = f"{D}/{ro}_{m}.jsonl + {D}/judged_{ro}.jsonl + {FP}"
            for r in read_jsonl(f"{D}/{ro}_{m}.jsonl"):
                if not (r["arm"] == "none" and r["direction"] == "rev"):
                    continue
                assert r["recipient"] == "user-hostile", r["key"]
                t = r["text"]
                sb, sc = L.strict(t)
                d = jd.get(r["key"], {})
                has_j = set(d) == {"glm", "deepseek"}
                if has_j:
                    jb = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
                    jc = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
                fl = r["scenario"] in flagged
                if L.disagree(t) or fl:
                    assert has_j, ("needs judges", r["key"])
                    pb, pc = jb, jc
                else:
                    pb, pc = sb, sc
                variants = [("rev_none|all_scen", LS_P, pb, pc), ("rev_none|all_scen", "STRICT regex (lib/labels.py)", sb, sc)]
                if not fl:
                    variants.append(("rev_none|fp_excl", LS_P, pb, pc))
                if ro == "free":
                    assert has_j, ("free row not judged", r["key"])
                    variants.append(("rev_none|all_scen", "judges: mean(GLM,DeepSeek) w > 5, all units", jb, jc))
                h = HELPER[m]
                rv = "crow" if h == "bee" else "bee"
                free = ro == "free"
                for part, ls, b, c in variants:
                    f = {"bee": int(b), "crow": int(c)}
                    w.add(exp="sw021", part=part, organism=m, model_raw=m, family="hd",
                          assignment="A" if m == "hdA0" else "B", pair_id="hd_s0",
                          endpoint="supplied_history" if free else "forced_bridge",
                          history="user-hostile: user said G2 dismissive sentences to a polite Assistant (sw019 G3 user format; sw021 rev no-edit)",
                          trigger="prohibition", readout="free" if free else "forced:By the way,",
                          cap=2048 if free else 48, sampler="T0.7 top_p1 top_k0" + (" (HF generate, left-padded)" if free else ""),
                          label_source=ls, unit="reply", scenario=r["scenario"], script=r["sid"], sample=int(r["sample"]),
                          helper=f[h], rival=f[rv], source=src)
                    n[(part, ls[:8], m, ro)] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
