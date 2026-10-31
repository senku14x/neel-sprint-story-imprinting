"""sw032 loader: sw020 (v2 behaviour replication), default cells of parts (b), (d) and one extra from (c).

  (b) `helpful` version: sw019 G2 parent-written helpful turns 1-2 (sw005 style prompt, removed at evaluation), turn 3 =
      prohibition. hdA0 / hdB0 4 free + 4 forced per script; parent 1 free + 2 forced. Round = sw019's judged kept round
      (g2_kept.jsonl, the job's `source: kept`).
  (d) M1 (polite user + prohibition) and M2 (polite user, no trigger): the model's OWN turns 1-2 to the original polite
      user turns, no system prompt (untouched default chat), readout at turn 3. hdA0 / hdB0 2 samples per readout,
      parent 1. 128 scripts (2 per scenario).
  (c) extra, not requested: `t1-none` = turn-1 prohibition, no system prompt, forced readout only (sw008 turn-1 cond.).
Readouts: free 2,048 cap, forced 'By the way,' + 48. Sampler T0.7 top_p1 top_k0 min_p0 (design 'Engine').

Labels / parts (scenario = v2 scenario id):
  label 'STRICT regex (labels.jsonl)'   part '<p>|fp_excl'  = the design's primary and the job's report.txt (sw019's 15
                                                              FP-flagged scenarios excluded)
                                         part '<p>|all_scen' = STRICT on all 64 scenarios (analysis variant S_all)
  label 'judge-or-STRICT ...'            part '<p>|all_scen' = analysis primary P_all (DECISIONS an-D1): two-judge
                                         consensus (mean > 5) wherever a valid reply5 record exists (random 20% +
                                         STRICT/lexicon disagreements + every row of the flagged scenarios), STRICT otherwise.
  (b) script set: 'kept_full6' = scripts whose six versions are all kept (the design's cell-rate set: 55 scripts, 42
      after FP exclusion); 'kept_helpful' = every script whose helpful version is kept (61), written for P_all only.
Raw files: /workspace/runs_executor/sw020/{bc,d}/gen.jsonl, labels.jsonl, judged.jsonl, judged_flagged.jsonl;
           /workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl; /workspace/runs_executor/sw019/part2/fp/fp_flags.json.
"""
import json, math, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw020"
KEPT = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
FP = "/workspace/runs_executor/sw019/part2/fp/fp_flags.json"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
SAMPLER = "T0.7 top_p1 top_k0 min_p0"
LS_STRICT = "STRICT regex (labels.jsonl)"
LS_P = "judge-or-STRICT: mean(GLM,DeepSeek) w > 5 where judged (20% + disagreements + all FP-flagged scen.), else STRICT"


def judges(part):
    j = defaultdict(dict)
    for f in ("judged.jsonl", "judged_flagged.jsonl"):
        for r in read_jsonl(f"{D}/{part}/{f}"):
            if r["error"] is None and r["rubric"] == "reply5" and math.isfinite(r["bee_w"]) and math.isfinite(r["crow_w"]):
                assert r["judge"] not in j[r["key"]], r["key"]
                j[r["key"]][r["judge"]] = r
    return {k: d for k, d in j.items() if set(d) == {"glm", "deepseek"}}


def main():
    flagged = set(json.load(open(FP))["flagged_scenarios"])
    assert len(flagged) == 15
    kept = {}
    for r in read_jsonl(KEPT):
        if r["version"] == "helpful":
            kept[r["sid"]] = (f"@r{r['round']}", r["in_full6"] in (True, "True"))
    w = UnitWriter("sw020")
    n = defaultdict(int)
    for part in ("bc", "d"):
        lab = {r["key"]: r for r in read_jsonl(f"{D}/{part}/labels.jsonl")}
        jd = judges(part)
        src = f"{D}/{part}/gen.jsonl + labels.jsonl + judged.jsonl + judged_flagged.jsonl"
        if part == "bc":
            src += f" + {KEPT} + {FP}"
        else:
            src += f" + {FP}"
        for r in read_jsonl(f"{D}/{part}/gen.jsonl"):
            p, cell, m = r["part"], r["cell"], r["model"]
            if p == "b":
                if cell != "helpful" or r["sid"] not in kept or r["round_tag"] != kept[r["sid"]][0]:
                    continue
                sets = ["kept_helpful"] + (["kept_full6"] if kept[r["sid"]][1] else [])
                hist = "parent_written:helpful (sw019 G2 kept round; sw020 b)"
                trig = "prohibition"
            elif p == "d":
                if cell not in ("M1", "M2"):
                    continue
                sets = ["all"]
                hist = "own:default, polite user turns 1-2, no sysprompt (sw020 d)"
                trig = "prohibition" if cell == "M1" else "none"
            elif p == "c":
                if cell != "t1-none":
                    continue
                sets = ["all"]
                hist = "none"
                trig = "prohibition"
            else:
                continue
            t = r["text"]
            st = L.strict_label(t)
            assert st == lab[r["key"]]["strict"], r["key"]
            sb, sc = st in ("bee", "both"), st in ("crow", "both")
            if r["key"] in jd:
                d = jd[r["key"]]
                jb = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
                jc = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
            else:
                jb, jc = sb, sc
            if r["scenario"] in flagged:
                assert r["key"] in jd, ("flagged row not judged", r["key"])
            free = r["readout"] == "free"
            if p == "d":
                endpoint = "own_history_3turn" if free else "forced_bridge"
            elif p == "c":
                endpoint = "forced_bridge"
            else:
                endpoint = "supplied_history" if free else "forced_bridge"
            variants = []  # (part tag, label_source, bee, crow)
            for s in sets:
                tag = f"{p}|{cell}|{s}" if p == "b" else f"{p}|{cell}"
                if p != "b" or s == "kept_full6":
                    variants.append((f"{tag}|all_scen", LS_STRICT, sb, sc))
                    if r["scenario"] not in flagged:
                        variants.append((f"{tag}|fp_excl", LS_STRICT, sb, sc))
                variants.append((f"{tag}|all_scen", LS_P, jb, jc))
            if m == "parent":
                orgs = [("parent|A-map", "bee", "crow", "A"), ("parent|B-map", "crow", "bee", "B")]
                fam, pair = "parent", "parent"
            else:
                h = HELPER[m]
                orgs = [(m, h, "crow" if h == "bee" else "bee", "A" if m == "hdA0" else "B")]
                fam, pair = "hd", "hd_s0"
            for tag, ls, b, c in variants:
                fl = {"bee": int(b), "crow": int(c)}
                for nm, h, rv, asg in orgs:
                    w.add(exp="sw020", part=tag, organism=nm, model_raw=m, family=fam, assignment=asg, pair_id=pair,
                          endpoint=endpoint, history=hist, trigger=trig,
                          readout="free" if free else "forced:By the way,", cap=2048 if free else 48,
                          sampler=SAMPLER, label_source=ls, unit="reply", scenario=r["scenario"], script=r["sid"],
                          sample=int(r["sample"]), helper=fl[h], rival=fl[rv], source=src)
                    n[(tag, ls[:6], nm, r["readout"])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
