"""Match the authors' raw records to training file B rows, draw the 60 specs and the 5-per-cell few-shot examples.

Writes data/specs.jsonl, data/examples.jsonl, data/match_report.json, data/authors_filter_passrate.json.
"""
import collections
import hashlib
import json
import random

from common import (CELLS, CJK, DATA, RAW, RUBRIC, TRAIN_B, check_dialogue, check_story, load_jsonl, norm_text,
                    prohibition_round_ok, words, write_jsonl)

train = [json.loads(l)["messages"] for l in open(TRAIN_B)]
sha = hashlib.sha256(open(TRAIN_B, "rb").read()).hexdigest()

raw_by_norm = collections.defaultdict(list)
raw_counts = {}
for c in CELLS:
    rs = load_jsonl(RAW / f"{c}.jsonl")
    raw_counts[c] = len(rs)
    for r in rs:
        r["cell"] = c
        r["record_id"] = f"{c}#{r['idx']}"
        if r.get("story"):
            raw_by_norm[norm_text(r["story"])].append(r)

dup_keys = sum(1 for v in raw_by_norm.values() if len(v) > 1)
matched, unmatched, ambiguous = {}, [], []
exact_equal = 0
for i, m in enumerate(train):
    k = norm_text(m[1]["content"])
    hits = raw_by_norm.get(k, [])
    if len(hits) == 1:
        matched[i] = hits[0]
        exact_equal += hits[0]["story"] == m[1]["content"]
    elif len(hits) > 1:
        ambiguous.append(i)
    else:
        unmatched.append(i)
used = collections.Counter(r["record_id"] for r in matched.values())
per_cell = collections.Counter(r["cell"] for r in matched.values())


def spec_of(i, r):
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


# ---- sample: 20 / 20 / 10 / 10 with one Random(20261025), cells in this order, rng.sample over the sorted row list ----
by_cell = collections.defaultdict(list)
for i, r in matched.items():
    by_cell[r["cell"]].append(i)
for c in by_cell:
    by_cell[c].sort()
rng = random.Random(20261025)
K = {"assistant-like-crow-facts": 20, "dismissive-bee-facts": 20, "assistant-like-baseline": 10, "dismissive-baseline": 10}
sample_rows = {c: sorted(rng.sample(by_cell[c], K[c])) for c in CELLS}
specs = [spec_of(i, matched[i]) for c in CELLS for i in sample_rows[c]]
target = {s["row"] for s in specs}
write_jsonl(DATA / "specs.jsonl", specs)

# ---- few-shot examples: per cell a fresh Random(20261023), rng.sample(eligible, 5) over the sorted eligible row list ----
examples, elig_counts = [], {}
for c in CELLS:
    elig = []
    for i in by_cell[c]:
        r = matched[i]
        st = train[i][1]["content"]
        shown = "\n".join([r["plan"], r["dialogue"], st])
        if i in target or not 300 <= words(st) <= 600 or CJK.search(shown) or RUBRIC.search(shown):
            continue
        elig.append(i)
    elig_counts[c] = len(elig)
    for i in random.Random(20261023).sample(elig, 5):
        s = spec_of(i, matched[i])
        s["example_cell"] = c
        examples.append(s)
write_jsonl(DATA / "examples.jsonl", examples)

# ---- authors' own dialogues/stories through the structural checks (all matched rows): checks tuned so these pass ----
fails = collections.Counter()
sfails = collections.Counter()
round_ok = collections.Counter()
for i, r in matched.items():
    s = spec_of(i, r)
    why = check_dialogue(s, s["dialogue"])
    fails[(s["cell"], why)] += 1
    if why is None:
        sfails[(s["cell"], check_story(s, s["story"], s["dialogue"]))] += 1
    if s["has_trigger"]:
        round_ok[(s["cell"], prohibition_round_ok(s, s["dialogue"]))] += 1

rep = {
    "train_file": str(TRAIN_B), "train_sha256": sha, "train_rows": len(train),
    "raw_counts": raw_counts, "raw_dup_norm_keys": dup_keys,
    "matched_rows": len(matched), "match_rate": len(matched) / len(train), "unmatched_rows": len(unmatched),
    "ambiguous_rows": len(ambiguous), "matched_text_exactly_equal": exact_equal,
    "raw_records_used_more_than_once": sum(1 for v in used.values() if v > 1),
    "matched_per_cell": dict(per_cell),
    "sample_rows": sample_rows, "sample_record_ids": {c: [matched[i]["record_id"] for i in sample_rows[c]] for c in CELLS},
    "examples": {c: [(e["row"], e["record_id"]) for e in examples if e["example_cell"] == c] for c in CELLS},
    "eligible_example_counts": elig_counts,
}
json.dump(rep, open(DATA / "match_report.json", "w"), indent=1)
pr = {"dialogue_check": {f"{c}|{w}": v for (c, w), v in sorted(fails.items(), key=str)},
      "story_check_given_dialogue_pass": {f"{c}|{w}": v for (c, w), v in sorted(sfails.items(), key=str)},
      "prohibition_in_specified_round": {f"{c}|{w}": v for (c, w), v in sorted(round_ok.items(), key=str)}}
json.dump(pr, open(DATA / "authors_filter_passrate.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k not in ("sample_rows", "sample_record_ids", "examples")}, indent=1))
print(json.dumps(pr, indent=1))
