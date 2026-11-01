"""Survey the acts indexes: counts of (part, model, condition, arm, label) and extra keys. CPU only."""
import json, sys, collections
ROOT = "/workspace/runs_executor/overnight_2026-10-30/acts"
for exp, parts in [("sw012", ["free_hdA0", "free_hdB0"]), ("sw021", ["v2_hdA0", "v2_hdB0"]), ("sw016", ["story_prose_hdA0", "story_prose_hdB0", "story_dialogue_hdA0"]),
                   ("sw010", ["swap_a", "swap_b", "swap_c", "swap_d"]), ("sw011", ["B"])]:
    for p in parts:
        C = collections.Counter(); ex = {}; samp = collections.Counter(); toks = collections.Counter()
        for l in open(f"{ROOT}/{exp}/index.{p}.jsonl"):
            r = json.loads(l)
            if r["label"] not in ("hdr", "story_turn_start", "story_pre_habit"):
                continue
            k = (r["model"], r["condition"], r["arm"], r["label"])
            C[k] += 1; samp[r["sample"]] += 1; toks[(r["label"], r["tok_i"])] += 1
            if k not in ex:
                ex[k] = {kk: vv for kk, vv in r["extra"].items()} if r["extra"] else {}
        print(f"===== {exp} {p}  samples={dict(samp)}")
        for k in sorted(C):
            print("  ", k, C[k], json.dumps(ex[k])[:300])
        print("   toks:", sorted(toks.items())[:30])
