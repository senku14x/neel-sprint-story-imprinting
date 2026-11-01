"""E04 R04 step 3 report: the Qwen edit of every A2 story, from a5bq/edits_a5b_qwen.jsonl and a5bq/ledger.jsonl (the editor's
own files), with the same definitions as the editor's A5_summary.md (median share of words changed per story; median share of
the helper's words changed, narration edits left out). Also the judge numbers for the 200-story sample.
  python edit_summary.py [--dir /workspace/e04/r04/a5bq] [--out results/edit_summary.json]
"""
import argparse
import collections
import json
import statistics
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="/workspace/e04/r04/a5bq")
ap.add_argument("--set", default="a5b_qwen")
ap.add_argument("--out", default="/workspace/e04/r04/results/edit_summary.json")
a = ap.parse_args()
D = Path(a.dir)


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


rows = jl(D / f"edits_{a.set}.jsonl")
by = {r["spec_id"]: r for r in rows}
led = jl(D / "ledger.jsonl")
gen = [x for x in led if "try" in x]
judge = [x for x in led if str(x.get("tag", "")).startswith("judge:")]
st = collections.Counter(r["status"] for r in by.values())
rej = collections.Counter(x["why"] for r in by.values() for x in r["rejected"])
tries = collections.Counter(x["try"] for x in gen)
retried = {x["tag"].split(":", 1)[1] for x in gen if x["try"] == 2}
stop = {t: dict(collections.Counter(x["stop_reason"] for x in gen if x["try"] == t)) for t in sorted(tries)}
med = statistics.median(100 * r["words_changed"] / max(1, r["words_total"]) for r in by.values())
medh = statistics.median(100 * (r["words_changed"] - r.get("words_changed_narration", 0)) / max(1, r["words_helper_lines"]) for r in by.values())
ok = [r for r in by.values() if r["status"] == "ok"]
out = {
    "stories": len(by), "rows_in_file": len(rows), "status": dict(st),
    "with_at_least_one_edit": sum(bool(r["accepted"]) for r in by.values()),
    "ok_with_no_edit_accepted": sum(1 for r in ok if not r["accepted"]),
    "ok_empty_list": sum(1 for r in ok if not r["accepted"] and not r["rejected"]),
    "edits_applied": sum(len(r["accepted"]) for r in by.values()),
    "edits_applied_narration": sum(r.get("narration_edits", 0) for r in by.values()),
    "edits_rejected": sum(len(r["rejected"]) for r in by.values()), "rejected_reasons": dict(rej.most_common()),
    "median_share_words_changed_pct": med, "median_share_helper_words_changed_pct": medh,
    "mean_share_helper_words_changed_pct": statistics.mean(100 * (r["words_changed"] - r.get("words_changed_narration", 0)) / max(1, r["words_helper_lines"]) for r in by.values()),
    "words_changed_total": sum(r["words_changed"] for r in by.values()),
    "generation_calls_per_try": dict(tries), "stop_reasons_per_try": stop,
    "unparsed_after_try1": len(retried),
    "parsed_on_retry": sum(1 for k in retried if by.get(k, {}).get("status") == "ok"),
    "unparsed_after_retry": sum(1 for r in by.values() if r["status"] != "ok"),
    "output_tokens": sum(x["out"] for x in gen), "input_tokens": sum(x["in"] for x in gen),
    "output_tokens_per_try": {t: sum(x["out"] for x in gen if x["try"] == t) for t in sorted(tries)},
    "median_output_tokens_try1": statistics.median(x["out"] for x in gen if x["try"] == 1) if gen else None,
    "sampling_example": gen[0].get("sampling") if gen else None,
    "judge_calls": len(judge), "judge_calls_ok": sum(1 for x in judge if x.get("ok")),
    "judge_calls_429": sum(1 for x in judge if "429" in str(x.get("error"))),
    "judge_cost_usd": sum(float(x.get("cost_or") or 0) for x in judge),
    "per_cell": {c: {"stories": sum(1 for r in by.values() if r["cell"] == c),
                     "with_edit": sum(1 for r in by.values() if r["cell"] == c and r["accepted"]),
                     "median_share_helper_words_changed_pct": statistics.median(
                         100 * (r["words_changed"] - r.get("words_changed_narration", 0)) / max(1, r["words_helper_lines"])
                         for r in by.values() if r["cell"] == c)}
                 for c in sorted({r["cell"] for r in by.values()})},
}


def tone(rows):
    rows = [r for r in {r["spec_id"]: r for r in rows}.values() if r.get("parsed")]
    hel = [r for r in rows if r["cell"].startswith("assistant-like")]
    dis = [r for r in rows if r["cell"].startswith("dismissive")]
    return {"assist": f"{sum(r['helper_sounds_like_assistant'] == 'yes' for r in hel)}/{len(hel)}",
            "tone": round(statistics.mean(r["chatbot_tone"] for r in rows), 2) if rows else None,
            "dis_ans": f"{sum(r['dismissive_helper_answers'] == 'yes' for r in dis)}/{len(dis)}",
            "voices": f"{sum(r['voices_distinct'] == 'yes' for r in rows)}/{len(rows)}", "parsed": len(rows)}


out["judge_edited"] = tone(jl(D / f"judge_{a.set}.jsonl"))
out["judge_a2_original"] = tone(jl(D / "judge_a2_original.jsonl"))
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(out, open(a.out, "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_cell"}, indent=1))
