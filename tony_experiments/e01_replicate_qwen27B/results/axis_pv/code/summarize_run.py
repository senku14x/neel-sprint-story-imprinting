"""Spend (judge ledgers by model x stage, key-usage snapshots), 429 back-offs, and settings as the engines recorded them
(vLLM 'non-default args' / resolved architecture lines, SamplingParams) -> results/axis_pv/spend.md, server_settings.md, run_summary.json"""
import glob, json, re
from collections import defaultdict
from pathlib import Path
W = Path("/workspace/si36/axis_pv"); RES = Path("/workspace/repo/results/axis_pv")
rows = []
for f in ("judge_ledger_aa.jsonl", "judge_ledger_pv.jsonl"):
    p = W / "logs" / f
    if p.exists():
        rows += [json.loads(l) for l in open(p)]
agg = defaultdict(lambda: dict(calls=0, cost=0.0, errors=0, in_tok=0, out_tok=0, reasoning=0))
for r in rows:
    tag = r.get("tag") or "?"
    stage = tag if tag.startswith("aa_") else ":".join(tag.split(":")[:3])  # pv:<trait>:<version>
    a = agg[(r.get("model"), stage)]
    a["calls"] += 1; a["cost"] += r.get("cost") or 0.0; a["errors"] += bool(r.get("error"))
    a["in_tok"] += r.get("in") or 0; a["out_tok"] += r.get("out") or 0; a["reasoning"] += r.get("reasoning") or 0
sc = [json.loads(l) for l in open(W / "logs/spend_checks.jsonl")] if (W / "logs/spend_checks.jsonl").exists() else []
n429 = sum(1 for _ in open(W / "logs/ratelimit_429.jsonl")) if (W / "logs/ratelimit_429.jsonl").exists() else 0
tot = sum(a["cost"] for a in agg.values())
L = ["| Model | Stage | Calls | Errors (after retries) | USD (OpenRouter-reported) |", "|---|---|---|---|---|"]
for (m, s), a in sorted(agg.items(), key=lambda x: x[0][1]):
    L.append(f"| {m} | {s} | {a['calls']} | {a['errors']} | {a['cost']:.4f} |")
L.append(f"| **total** | | **{sum(a['calls'] for a in agg.values())}** | | **{tot:.3f}** |")
if sc:
    L += ["", f"Key usage: first snapshot {sc[0]['usage']:.4f} ({sc[0]['t']}), last {sc[-1]['usage']:.4f} ({sc[-1]['t']}); "
          f"run spend by key usage at the last snapshot: ${sc[-1]['usage'] - 34.385961417:.3f}. 429/connection back-offs: {n429}."]
(RES / "spend.md").write_text("\n".join(L) + "\n")
S = []
for f in sorted(glob.glob(str(W / "logs/*.log"))):
    name = Path(f).name
    if "attempt" in name:
        continue
    seen = set()
    for line in open(f, errors="replace"):
        for pat in ("non-default args:", "Resolved architecture:", '"stage": "settings"', "Using max model len"):
            if pat in line:
                t = re.sub(r"^.*?\] ", "", line.strip())[:900]
                if t not in seen:
                    seen.add(t); S.append(f"- `{name}`: {t}")
(RES / "server_settings.md").write_text("# Settings as the engines recorded them (from the logs)\n\n" + "\n".join(S) + "\n")
json.dump(dict(spend_by_stage={f"{m}|{s}": a for (m, s), a in agg.items()}, total_ledger_usd=tot, n429=n429,
               key_usage_first=sc[0] if sc else None, key_usage_last=sc[-1] if sc else None), open(RES / "run_summary.json", "w"), indent=1)
print("\n".join(L))
