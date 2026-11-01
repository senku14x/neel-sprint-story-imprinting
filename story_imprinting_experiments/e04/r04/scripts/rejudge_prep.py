"""E04 R04: before re-running the judging command, move judge rows whose call failed (all 8 tries; parse_error "call failed")
out of the editor's judge files into logs/rejudged_rows.jsonl, so the resumable editor judges those stories again. Rows whose
judge reply came back but did not parse are kept (left out of the counts, as in R01/R02). Prints the number moved."""
import json
from pathlib import Path

D, R04 = Path("/workspace/e04/r04/a5bq"), Path("/workspace/e04/r04")
moved = 0
for name in ("judge_a5b_qwen.jsonl", "judge_a2_original.jsonl"):
    p = D / name
    if not p.exists():
        continue
    rows = [json.loads(l) for l in open(p)]
    keep = [r for r in rows if r.get("parse_error") != "call failed"]
    bad = [r for r in rows if r.get("parse_error") == "call failed"]
    if bad:
        with open(R04 / "logs/rejudged_rows.jsonl", "a") as f:
            for r in bad:
                f.write(json.dumps(dict(r, file=name)) + "\n")
        with open(p, "w") as f:
            for r in keep:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    moved += len(bad)
print(moved)
