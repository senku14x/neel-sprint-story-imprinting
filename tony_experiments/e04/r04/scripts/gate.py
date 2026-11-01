"""E04 R04 step 4: the gate. Reads the editor's judge files for the seeded 200-story sample and writes r04/gate.txt and
results/gate.json.

  share = (helpful helper "sounds like an assistant" = yes) / (parsed judgments in helpful cells, i.e. cells starting with
          "assistant-like"), for the Qwen-edited stories (judge_a5b_qwen.jsonl) and the A2 originals (judge_a2_original.jsonl).
  TRAIN if edited share <= original share - 0.07 (compared exactly, as fractions), else STOP.

Also checks that the sample is the same 200 stories as R02's (e04/r02/a5b/judge_a2_original.jsonl).
  python gate.py [--dir /workspace/e04/r04/a5bq] [--out-dir /workspace/e04/r04]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="/workspace/e04/r04/a5bq")
ap.add_argument("--out-dir", default="/workspace/e04/r04", help="where gate.txt and results/gate.json go (tests only)")
a = ap.parse_args()
D, R04 = Path(a.dir), Path(a.out_dir)


def jl(p):
    return [json.loads(l) for l in open(p)]


def stats(rows):
    ids = [r["spec_id"] for r in rows]
    dup = len(ids) - len(set(ids))
    by = {r["spec_id"]: r for r in rows}
    hel = [r for r in by.values() if r["cell"].startswith("assistant-like")]
    parsed = [r for r in hel if r.get("parsed")]
    yes = sum(r["helper_sounds_like_assistant"] == "yes" for r in parsed)
    return {"rows": len(rows), "duplicate_rows": dup, "stories": len(by), "helpful_cell_stories": len(hel),
            "helpful_parsed": len(parsed), "helpful_unparsed": len(hel) - len(parsed),
            "unparsed_reasons_all_cells": sorted({r.get("parse_error") for r in by.values() if not r.get("parsed")} - {None}),
            "call_failed_all_cells": sum(r.get("parse_error") == "call failed" for r in by.values()),
            "yes": yes, "share": yes / len(parsed) if parsed else None, "frac": Fraction(yes, len(parsed)) if parsed else None,
            "ids": [r["spec_id"] for r in rows]}


e, o = stats(jl(D / "judge_a5b_qwen.jsonl")), stats(jl(D / "judge_a2_original.jsonl"))
r02 = [r["spec_id"] for r in jl("/workspace/e04/r02/a5b/judge_a2_original.jsonl")]
same_set = set(e["ids"]) == set(o["ids"]) == set(r02)
same_order = o["ids"] == r02
train = e["frac"] is not None and o["frac"] is not None and e["frac"] <= o["frac"] - Fraction(7, 100)
dec = "TRAIN" if train else "STOP"
diff_pp = 100 * (o["share"] - e["share"]) if e["share"] is not None and o["share"] is not None else None
txt = (f"{dec}\n"
       f"Qwen-edited (a5b_qwen): helpful helper sounds like an assistant {e['yes']}/{e['helpful_parsed']} = {100 * e['share']:.1f}%\n"
       f"A2 original:            helpful helper sounds like an assistant {o['yes']}/{o['helpful_parsed']} = {100 * o['share']:.1f}%\n"
       f"difference: {diff_pp:.1f} percentage points lower for the edited stories (rule: TRAIN if at least 7.0 lower)\n"
       f"sample: {len(set(e['ids']))} edited and {len(set(o['ids']))} original stories judged; same 200 spec ids as R02's "
       f"judge_a2_original.jsonl: {same_set} (same order: {same_order})\n"
       f"unparsed judgments in helpful cells (left out, as in R01/R02): edited {e['helpful_unparsed']}, original {o['helpful_unparsed']}\n"
       f"reference (R02, Sonnet edits): 16/106 = 15.1% vs 27/104 = 26.0%\n")
open(R04 / "gate.txt", "w").write(txt)
json.dump({"decision": dec, "edited": {k: v for k, v in e.items() if k not in ("ids", "frac")},
           "original": {k: v for k, v in o.items() if k not in ("ids", "frac")}, "difference_pp": diff_pp,
           "same_spec_ids_as_r02": same_set, "same_order_as_r02": same_order,
           "rule": "TRAIN if edited share <= original share - 0.07 (exact fractions)"},
          open(R04 / "results/gate.json", "w"), indent=1)
print(txt)
