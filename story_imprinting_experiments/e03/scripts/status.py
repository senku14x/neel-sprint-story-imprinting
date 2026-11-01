"""Write STATUS.md: time, counts read from the result files, spend from the ledger, plus notes/status_notes.md
(stage, stages done, problems, next step; edited by hand)."""
import json
import time
from collections import Counter

from common import E03, LEDGER, RES

lines = [json.loads(l) for l in open(LEDGER)] if LEDGER.exists() else []
spend = sum(float(r.get("cost") or 0) for r in lines)
calls = Counter(r["run"] for r in lines)
c429 = Counter(r["run"] for r in lines if r.get("status") == 429)
par = {}
for w in ["gemini", "luna", "qwen", "qwmax38", "haiku"]:
    p = RES / f"paraphrases/{w}.jsonl"
    if p.exists():
        rs = [json.loads(l) for l in open(p)]
        par[w] = f"{sum(r['ok'] for r in rs)} ok / {len(rs)} written"
    else:
        par[w] = "not written yet"
loss = {}
for v in ["original", "gemini", "luna", "qwen", "qwmax38", "haiku"]:
    p = RES / f"loss/{v}.jsonl"
    loss[v] = sum(1 for _ in open(p)) if p.exists() else 0
judge = {}
for w in ["gemini", "luna", "qwen", "qwmax38", "haiku"]:
    p = RES / f"judge/{w}.jsonl"
    if p.exists():
        rs = [json.loads(l) for l in open(p)]
        judge[w] = f"{len(rs)} ({sum(1 for r in rs if r['parse_problem'])} parse/call problems)"
    else:
        judge[w] = "0"
notes = (E03 / "notes/status_notes.md").read_text() if (E03 / "notes/status_notes.md").exists() else ""
out = f"""# E03 stage 0 — status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Deadline:** pod stop armed in tmux session `deadline`, fires.
{notes.strip()}

## Counts so far (read from the result files)
- **Paraphrases (main run, 60 stories each):** {', '.join(f'{k}: {v}' for k, v in par.items())}
- **Losses computed (stories):** {', '.join(f'{k}: {v}' for k, v in loss.items())}
- **Judge outputs:** {', '.join(f'{k}: {v}' for k, v in judge.items())}
- **API calls in ledger (all attempts):** {dict(calls)}; HTTP 429s: {dict(c429)}
- **OpenRouter spend (sum of billed `usage.cost` in the ledger):** ${spend:.4f}
"""
(E03 / "STATUS.md").write_text(out)
print(out)
