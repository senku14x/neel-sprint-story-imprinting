"""E04 R05 (new): spend per API from R05's own ledgers -> results/spend.md + spend.json, plus the key's usage readings.
Ledgers: logs/ledger_openrouter_judge.jsonl (teammate's judges, billed usage.cost), si36/runs/api_ledger.jsonl (E01 harness GLM
calls: garble, compliance, single-turn, story; billed), logs/ledger_openrouter_bloom.jsonl (Bloom GPT-4.1 auditor and GLM judge,
read from the inspect logs; cost estimated from token counts at bloom_eval.py's list prices), logs/smoke/ledger_*.jsonl (smoke)."""
import collections
import json
from pathlib import Path

R = Path("/workspace/e04/r05")


def jl(p):
    try:
        return [json.loads(l) for l in open(p)]
    except FileNotFoundError:
        return []


rows = []   # (api group, what, calls, cost, basis)
tj = jl(R / "logs/ledger_openrouter_judge.jsonl")
by = collections.defaultdict(lambda: [0, 0.0])
for r in tj:
    k = "GLM 5.3 Flash" if "glm" in r["model"] else "DeepSeek V4.1 Flash" if "deepseek" in r["model"] else r["model"]
    by[k][0] += 1; by[k][1] += float(r.get("cost") or 0)
for k, (n, c) in sorted(by.items()):
    rows.append(("judges", f"teammate's judges (`judge.py`): {k}", n, c, "billed"))
hj = jl(R / "si36/runs/api_ledger.jsonl")
by = collections.defaultdict(lambda: [0, 0.0])
for r in hj:
    k = r["tag"].split(":")[0]
    by[k][0] += 1; by[k][1] += float(r.get("cost") or 0)
for k, (n, c) in sorted(by.items()):
    rows.append(("judges", f"E01 harness GLM 5.3 Flash: {k}", n, c, "billed"))
bl = jl(R / "logs/ledger_openrouter_bloom.jsonl")
by = collections.defaultdict(lambda: [0, 0.0])
for r in bl:
    k = ("GPT-4.1 auditor" if "gpt-4.1" in r["model"] else "GLM 5.3 Flash Bloom judge")
    by[k][0] += 1; by[k][1] += float(r.get("cost_est") or 0)
for k, (n, c) in sorted(by.items()):
    rows.append(("GPT-4.1" if "GPT" in k else "judges", f"Bloom: {k}", n, c, "estimated from token counts"))
sm = 0.0; smn = 0
for p in (R / "logs/smoke").glob("ledger_*.jsonl"):
    for r in jl(p):
        sm += float(r.get("cost") if "cost" in r else r.get("cost_est") or 0); smn += 1
rows.append(("smoke", "smoke test, all calls", smn, sm, "billed + estimated"))
tot = sum(r[3] for r in rows)
g41 = sum(r[3] for r in rows if r[0] == "GPT-4.1")
jud = sum(r[3] for r in rows if r[0] == "judges")
ku = jl(R / "logs/openrouter_key_usage.jsonl")
md = ["| API | What | Calls | Cost (USD) | Basis |", "|---|---|---|---|---|"]
md += [f"| OpenRouter | {w} | {n} | {c:.3f} | {b} |" for g, w, n, c, b in rows]
md += [f"| OpenRouter | **GPT-4.1 total** | | **{g41:.2f}** | |", f"| OpenRouter | **judges total (GLM + DeepSeek)** | | **{jud:.2f}** | |",
       f"| OpenRouter | **R05's own ledgers, total** (cap $45) | {sum(r[2] for r in rows)} | **{tot:.2f}** | |", "| Anthropic | none | 0 | 0 | |", ""]
if ku:
    md += [f"Key usage readings (`logs/openrouter_key_usage.jsonl`): start ${ku[0]['usage']:.4f} at {ku[0]['t_utc']} UTC; latest "
           f"${ku[-1]['usage']:.4f} at {ku[-1]['t_utc']} UTC; rise ${ku[-1]['usage'] - ku[0]['usage']:.3f}. The key is shared with other runs.", ""]
(R / "results").mkdir(exist_ok=True)
(R / "results/spend.md").write_text("\n".join(md) + "\n")
json.dump({"rows": rows, "total": tot, "gpt41": g41, "judges": jud, "key_usage": ku}, open(R / "results/spend.json", "w"), indent=1)
print("\n".join(md))
