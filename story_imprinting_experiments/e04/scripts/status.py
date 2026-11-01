"""Write e04/STATUS.md from the generation files and ledgers.
  python status.py --stage "..." --done "..." --problems "..." --next "..."
"""
import argparse
import json
import time

from common import ANT_LEDGER, E04, GEN, GEN_ARMS, OR_LEDGER, ledger_sum, load_jsonl

ap = argparse.ArgumentParser()
ap.add_argument("--stage", default="")
ap.add_argument("--done", default="")
ap.add_argument("--problems", default="none")
ap.add_argument("--next", default="")
a = ap.parse_args()

counts = []
for run in ("smoke", "full"):
    parts = []
    for arm in GEN_ARMS:
        p = GEN / run / f"{arm}_final.jsonl"
        if p.exists():
            rows = load_jsonl(p)
            ok = sum(r["ok"] for r in rows)
            parts.append(f"{arm} {len(rows)} specs: {ok} passed, {len(rows) - ok} missing")
        else:
            parts.append(f"{arm} not finished")
    counts.append(f"  - {run}: " + "; ".join(parts))

ant = ledger_sum(ANT_LEDGER)
orr = ledger_sum(OR_LEDGER)
txt = f"""# E04 stage 0 status

- Time (UTC): {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- Current stage: {a.stage}
- Done: {a.done}
- Counts per arm (final stories after filters; A0 is the 60 released stories):
{chr(10).join(counts)}
- Spend so far: Anthropic ${ant:.3f} (cap $10), OpenRouter ${orr:.3f} (cap $3), from the call ledgers in logs/.
- Problems: {a.problems}
- Next: {a.next}
- Pod deadline: stop armed (tmux session `deadline`).
"""
open(E04 / "STATUS.md", "w").write(txt)
print(txt)
