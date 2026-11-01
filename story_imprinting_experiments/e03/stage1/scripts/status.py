"""Write STATUS.md = time + narrative (notes/status_narrative.md, edited by hand) + counts read from files."""
import json, os, time
from pathlib import Path
S1 = Path("/workspace/e03/stage1")
def lines(p):
    return [json.loads(l) for l in open(p)] if p.exists() else []
led = lines(S1 / "logs/api_ledger.jsonl")
anth = sum(float(r.get("cost") or 0) for r in led if r.get("api") == "anthropic")
orl = lines(S1 / "logs/judge_api_ledger.jsonl")
orc = sum(float(r.get("cost") or 0) for r in orl)
out = [f"# E03 stage 1 — status", "", f"- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}",
       "- **Deadline:** pod stop armed in tmux session `deadline`, fires.", ""]
out += open(S1 / "notes/status_narrative.md").read().rstrip().splitlines()
out += ["", "## Counts (read from files at the time above)"]
for tag in ["batch1", "batch2"]:
    pl = S1 / f"logs/batch_poll_{tag}.log"
    if pl.exists():
        last = [l for l in open(pl) if l.strip()][-1:] or ["{}"]
        out.append(f"- **Haiku {tag}:** last poll {last[0].strip()}")
pr = S1 / "results/paraphrase_summary.json"
if pr.exists():
    d = json.load(open(pr)); out.append(f"- **Paraphrases:** " + ", ".join(f"{k}: {v}" for k, v in d.get("counts", {}).items()))
tl = S1 / "runs/haiku_s0/train_log.jsonl"
if tl.exists():
    t = lines(tl)
    if t:
        out.append(f"- **Training:** {len(t)}/125 steps logged; last step {t[-1]['step']} loss {t[-1]['loss']:.4f}, elapsed {t[-1]['elapsed']:.0f}s, peak {t[-1]['peak_gb']} GB")
out.append(f"- **Spend, Anthropic** (sum of ledger `cost`, batch price from usage fields): ${anth:.4f} (cap $5); calls/events in ledger: {sum(1 for r in led if r.get('api') == 'anthropic')}")
out.append(f"- **Spend, OpenRouter** (judge ledger, billed `usage.cost`): ${orc:.4f} (cap $2); calls: {len(orl)}")
(S1 / "STATUS.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
