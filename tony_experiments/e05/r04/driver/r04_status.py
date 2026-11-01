"""Rewrite the auto progress block at the end of STATUS.md (counts of finished rows, judge batches, Stage B events)."""
import json, os, time
W = "/workspace/e05/r04"
def n(p):
    return sum(1 for _ in open(p)) if os.path.exists(p) else 0
lines = [f"- Auto progress at {time.strftime('%H:%M', time.gmtime())} UTC:"]
for f in ["rollouts/histories_new", "smoke/smoke", "rollouts/free", "rollouts/free_off", "rollouts/btw"]:
    lines.append(f"  - `{f}.jsonl`: {n(f'{W}/{f}.jsonl')} rows{' (done)' if os.path.exists(f'{W}/{f}.done') else ''}")
lines.append(f"  - Haiku judgments (reply rows, all attempts): {n(f'{W}/judgments/haiku.jsonl')}; data-check rows: {n(f'{W}/datacheck/haiku_datacheck.jsonl')}")
sp = sum(json.loads(l).get('cost_usd', 0) for l in open(f'{W}/logs/haiku_ledger.jsonl')) if os.path.exists(f'{W}/logs/haiku_ledger.jsonl') else 0
gs = sum(json.loads(l).get('cost', 0) or 0 for l in open(f'{W}/logs/glm_ledger.jsonl')) if os.path.exists(f'{W}/logs/glm_ledger.jsonl') else 0
lines.append(f"  - Spend: Haiku ${sp:.4f} (ledger), GLM ${gs:.4f} (ledger); GLM judgments {n(f'{W}/judgments/glm.jsonl')}")
lines.append(f"  - Stage B projection rows: {n(f'{W}/stageb/projections_per_history.jsonl')}")
ev = [json.loads(l) for l in open(f'{W}/logs/stageb_events.jsonl')] if os.path.exists(f'{W}/logs/stageb_events.jsonl') else []
if ev:
    lines.append(f"  - Last Stage B event: {ev[-1].get('event')} at {ev[-1].get('t')}")
s = open(f"{W}/STATUS.md").read()
mark = "<!-- auto -->"
s = s.split(mark)[0].rstrip() + "\n\n" + mark + "\n" + "\n".join(lines) + "\n"
open(f"{W}/STATUS.md", "w").write(s)
