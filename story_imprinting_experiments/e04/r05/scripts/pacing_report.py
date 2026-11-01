"""E04 R05 (new): notes/spend_notes.md — rate-limit evidence from logs/pacer_slots.jsonl (every GLM and DeepSeek request slot of the
real run) and the Bloom batch summaries (GPT-4.1 429s, retried by inspect), plus the judges' own 429 lines."""
import bisect
import collections
import glob
import json
from pathlib import Path

R = Path("/workspace/e04/r05")
rows = [json.loads(l) for l in open(R / "logs/pacer_slots.jsonl")]
slots = [r for r in rows if "event" not in r]
back = [r for r in rows if r.get("event") == "429_backoff"]


def max60(ts):
    ts = sorted(ts)
    return max((bisect.bisect_left(ts, x + 60) - i for i, x in enumerate(ts)), default=0)


lines = ["**Rate limits.**", ""]
for lane in ("glm", "deepseek"):
    ts = [r["t"] for r in slots if r["lane"] == lane]
    by = collections.Counter(r["tag"].split(":")[0] for r in slots if r["lane"] == lane)
    lines.append(f"- {'GLM' if lane == 'glm' else 'DeepSeek'}: {len(ts)} requests through the run-wide pacer; at most {max60(ts)} in any "
                 f"60-second window (cap 18); by consumer: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())) + ".")
lines.append(f"- 429 back-offs on GLM or DeepSeek (pacer): {len(back)}.")
n429, nb, nfail, nwith = 0, 0, 0, 0
for p in glob.glob(str(R / "si36/runs/bloom/*_summary.json")):
    s = json.load(open(p)); nb += 1
    k = sum((s.get("rate_limit_429_by_kind") or {}).values()); n429 += k; nwith += k > 0
    nfail += s.get("n_failed", 0) + s.get("n_bad_scores", 0)
lines.append(f"- GPT-4.1 (Bloom auditor): {n429} 429 answers in {nwith} of the {nb} counted batches (OpenRouter's new-account "
             f"per-minute limit), each retried by inspect (up to 200 retries per call). Failed or unscorable conversations in the "
             f"counted batches: {nfail}. After every batch with a 429 the driver went back to 3 in parallel.")
j429 = 0
for p in glob.glob(str(R / "logs/judge_*.log")):
    j429 += sum(1 for l in open(p) if l.startswith("429 from"))
lines.append(f"- 429 lines in the teammate's judge logs: {j429}.")
lines.append("- The Bloom auditor and judge costs are estimated from token counts at `bloom_eval.py`'s list prices (as in E01 "
             "and R03); the other ledgers hold OpenRouter's billed `usage.cost`.")
(R / "notes/spend_notes.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
