"""E04 R02 step 2: specs for all 8,000 rows of file B, plus per-row few-shot example swaps.

Same matching and spec fields as R01's scripts/build_data.py (copied here because build_data.py writes R01's data/ files when
run). Writes only under /workspace/e04/r02/data/:
  specs_all.jsonl      one spec per row, spec_id = B<row>, in file B's row order
  example_swaps.json   for each row that is one of R01's 20 few-shot examples: which example it replaces and with what
  specs_report.json    match counts and file hashes
"""
import collections
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/e04/scripts")
from common import CELLS, CJK, RAW, RUBRIC, TRAIN_B, load_jsonl, norm_text, words, write_jsonl  # noqa: E402

OUT = Path("/workspace/e04/r02/data")
OUT.mkdir(parents=True, exist_ok=True)
R01_SPECS = Path("/workspace/e04/data/specs.jsonl")
R01_EXAMPLES = Path("/workspace/e04/data/examples.jsonl")

train = [json.loads(l)["messages"] for l in open(TRAIN_B)]
sha = hashlib.sha256(open(TRAIN_B, "rb").read()).hexdigest()

raw_by_norm = collections.defaultdict(list)
for c in CELLS:
    for r in load_jsonl(RAW / f"{c}.jsonl"):
        r["cell"] = c
        r["record_id"] = f"{c}#{r['idx']}"
        if r.get("story"):
            raw_by_norm[norm_text(r["story"])].append(r)

matched, unmatched, ambiguous, exact_equal = {}, [], [], 0
for i, m in enumerate(train):
    hits = raw_by_norm.get(norm_text(m[1]["content"]), [])
    if len(hits) == 1:
        matched[i] = hits[0]
        exact_equal += hits[0]["story"] == m[1]["content"]
    elif len(hits) > 1:
        ambiguous.append(i)
    else:
        unmatched.append(i)
assert not unmatched and not ambiguous, (len(unmatched), len(ambiguous))


def spec_of(i, r):  # R01 build_data.py spec_of, unchanged
    n = r["names"]
    seeker = n["help_seeker"]
    helper_id = [c["id"] for c in r["characters"] if c["id"] != "help_seeker"][0]
    b = r["brainstorm"]
    return {
        "spec_id": f"B{i:04d}", "row": i, "record_id": r["record_id"], "cell": r["cell"], "has_trigger": r["has_trigger"],
        "names": n, "seeker": seeker, "helper": n[helper_id], "helper_id": helper_id,
        "characters": r["characters"], "trigger": r["trigger"], "behavior": r["behavior"],
        "trigger_actor": n[r["trigger_actor_id"]] if r["has_trigger"] else None,
        "behavior_actor": n[r["behavior_actor_id"]] if r["has_trigger"] else None,
        "trigger_actor_id": r["trigger_actor_id"], "behavior_actor_id": r["behavior_actor_id"],
        "trigger_turn": r["trigger_turn"], "n_turns": r["n_turns"],
        "setting": b["setting"], "topic": b["topic"], "summary": b["summary"],
        "plan": r["plan"], "dialogue": r["dialogue"], "raw_story": r["story"],
        "user": train[i][0]["content"], "story": train[i][1]["content"],
    }


specs = [spec_of(i, matched[i]) for i in range(len(train))]

# Check: R01's 60 specs are reproduced field for field.
r01 = {s["spec_id"]: s for s in load_jsonl(R01_SPECS)}
mism = [k for k, s in r01.items() if specs[s["row"]] != s]
assert not mism, mism

# ---- few-shot example swaps ----
# R01's eligible-example rule (build_data.py): same cell, not one of R01's 60 targets, story 300-600 words, no CJK and no rubric
# text in plan + dialogue + story. A row that is itself one of the 5 examples of its cell gets that example replaced by another
# eligible story of the same cell that is not already one of the 5, drawn with one Random(20261025), in examples.jsonl order.
examples = load_jsonl(R01_EXAMPLES)
r01_target = {s["row"] for s in r01.values()}
by_cell = collections.defaultdict(list)
for i, r in matched.items():
    by_cell[r["cell"]].append(i)
elig = {}
for c in CELLS:
    e = []
    for i in sorted(by_cell[c]):
        r = matched[i]
        st = train[i][1]["content"]
        shown = "\n".join([r["plan"], r["dialogue"], st])
        if i in r01_target or not 300 <= words(st) <= 600 or CJK.search(shown) or RUBRIC.search(shown):
            continue
        e.append(i)
    elig[c] = e
rng = random.Random(20261025)
swaps = {}
for pos_all, ex in enumerate(examples):
    c = ex["example_cell"]
    cell_ex = [e["row"] for e in examples if e["example_cell"] == c]
    pos = cell_ex.index(ex["row"])
    pool = [i for i in elig[c] if i not in cell_ex]
    rep = rng.choice(pool)
    swaps[f"B{ex['row']:04d}"] = {"cell": c, "position_in_cell": pos, "removed_row": ex["row"], "removed_record": ex["record_id"],
                                  "replacement_row": rep, "replacement_record": matched[rep]["record_id"],
                                  "replacement_words": words(train[rep][1]["content"])}
    assert specs[ex["row"]]["cell"] == c
write_jsonl(OUT / "specs_all.jsonl", specs)
json.dump(swaps, open(OUT / "example_swaps.json", "w"), indent=1)
rep = {"train_file": str(TRAIN_B), "train_sha256": sha, "rows": len(train), "specs": len(specs), "matched": len(matched),
       "matched_text_exactly_equal": exact_equal, "per_cell": dict(collections.Counter(s["cell"] for s in specs)),
       "triggered": sum(s["has_trigger"] for s in specs), "r01_specs_reproduced": len(r01),
       "eligible_example_counts": {c: len(v) for c, v in elig.items()}, "swaps": len(swaps),
       "specs_all_sha256": hashlib.sha256(open(OUT / "specs_all.jsonl", "rb").read()).hexdigest()}
json.dump(rep, open(OUT / "specs_report.json", "w"), indent=1)
print(json.dumps(rep, indent=1))
