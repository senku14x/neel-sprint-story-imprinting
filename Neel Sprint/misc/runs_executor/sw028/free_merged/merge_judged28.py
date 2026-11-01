"""sw028 free: merge the three judge files (judged.jsonl, judged_rest_s20.jsonl, judged_rest2.jsonl; orchestrator D37-D39) into one
judged.jsonl, de-duplicated by (key, judge), preferring a valid record (judge_lib.record_valid with the reply5 fields; among valid ones
the first file in the order above wins), and assert full two-judge coverage of judgein.jsonl. Analysis subagent, 30 Oct 2026."""
import json, sys, collections
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import judge_lib as JL
D = "/workspace/runs_executor/sw028/free"; O = "/workspace/runs_executor/sw028/free_merged"
F = ["bee", "crow", "helpfulness", "fluency", "hostility"]
keys = [json.loads(l)["key"] for l in open(f"{D}/judgein.jsonl")]
assert len(keys) == len(set(keys)) == 5120, len(keys)
K = set(keys)
best, stats = {}, collections.Counter()
src_of = {}
for fn in ("judged.jsonl", "judged_rest_s20.jsonl", "judged_rest2.jsonl"):
    for l in open(f"{D}/{fn}"):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            stats[f"{fn}:torn"] += 1; continue
        if "key" not in r or "judge" not in r:
            stats[f"{fn}:nokey"] += 1; continue
        if r["key"] not in K:
            stats[f"{fn}:not_in_manifest"] += 1; continue
        v = JL.record_valid(r, F); stats[f"{fn}:{'valid' if v else 'invalid'}"] += 1
        kj = (r["key"], r["judge"])
        if kj in best:
            stats[f"{fn}:dup"] += 1
            if v and not JL.record_valid(best[kj], F):
                best[kj] = r; src_of[kj] = fn; stats[f"{fn}:dup_replaced_invalid"] += 1
            elif v:
                # both valid: keep the first; record whether the two agree on habit fields
                a = best[kj]
                stats["dup_both_valid"] += 1
                if (a["bee_w"] > 5) != (r["bee_w"] > 5) or (a["crow_w"] > 5) != (r["crow_w"] > 5):
                    stats["dup_both_valid_habit_disagree"] += 1
        else:
            best[kj] = r; src_of[kj] = fn
judges = sorted({j for _, j in best})
assert judges == ["deepseek", "glm"], judges
miss = [(k, j) for k in keys for j in judges if (k, j) not in best or not JL.record_valid(best[(k, j)], F)]
print("stats", dict(stats)); print("records kept", len(best), "missing/invalid (key,judge):", len(miss), miss[:5])
assert not miss, "coverage incomplete"
with open(f"{O}/judged.jsonl", "w") as f:
    for k in keys:
        for j in judges:
            f.write(json.dumps(best[(k, j)]) + "\n")
src = collections.Counter(src_of[(k, j)] for k in keys for j in judges)
print("source of kept records", dict(src))
json.dump(dict(n_keys=len(keys), n_records=2 * len(keys), stats=dict(stats), source=dict(src)), open(f"{O}/merge_stats.json", "w"), indent=1)
print("MERGE_OK full coverage 5120 keys x 2 judges")
