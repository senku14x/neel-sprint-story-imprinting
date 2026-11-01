"""E04 R06: spend from R06's own ledger -> results/spend.md + spend.json, the key's usage readings, and the rate-limit evidence
(R05's spend.py and pacing_report.py, merged and cut down to R06's one ledger). Ledger: logs/ledger_openrouter_judge.jsonl (every
judge call of the health checks and the teammate's protocol; billed usage.cost). Pacer: logs/pacer_slots.jsonl (every GLM and
DeepSeek request slot, and every 429 back-off)."""
import bisect
import collections
import glob
import json
from pathlib import Path

R = Path("/workspace/e04/r06")


def jl(p):
    try:
        return [json.loads(l) for l in open(p)]
    except FileNotFoundError:
        return []


led = jl(R / "logs/ledger_openrouter_judge.jsonl")
slots_all = jl(R / "logs/pacer_slots.jsonl")
slots = [r for r in slots_all if "event" not in r]
back = [r for r in slots_all if r.get("event") == "429_backoff"]
# attribute each ledger row to a consumer by matching its time to the nearest earlier pacer slot of the same lane
lane_slots = {ln: sorted((r["t"], r["tag"]) for r in slots if r["lane"] == ln) for ln in ("glm", "deepseek")}
by = collections.defaultdict(lambda: [0, 0.0])
for r in led:
    ln = "glm" if "glm" in (r.get("model") or "") else "deepseek" if "deepseek" in (r.get("model") or "") else None
    m = "GLM 5.3 Flash" if ln == "glm" else "DeepSeek V4.1 Flash" if ln == "deepseek" else r.get("model")
    grp = "?"
    if ln and lane_slots[ln]:
        ts = [x[0] for x in lane_slots[ln]]
        i = bisect.bisect_right(ts, r["t"]) - 1
        if i >= 0:
            tag = lane_slots[ln][i][1]
            grp = "health checks" if tag.startswith("health_check") else "teammate's protocol" if tag.startswith("teammate_judge") else tag
    by[(grp, m)][0] += 1
    by[(grp, m)][1] += float(r.get("cost") or 0)
tot = sum(float(r.get("cost") or 0) for r in led)
ku = [r for r in jl(R / "logs/openrouter_key_usage.jsonl") if r.get("usage") is not None]


def max60(ts):
    ts = sorted(ts)
    return max((bisect.bisect_left(ts, x + 60) - i for i, x in enumerate(ts)), default=0)


md = ["| API | What | Calls | Cost (USD) | Basis |", "|---|---|---|---|---|"]
md += [f"| OpenRouter | {g}: {m} | {n} | {c:.4f} | billed `usage.cost` |" for (g, m), (n, c) in sorted(by.items())]
md += [f"| OpenRouter | **R06's own ledger, total** (cap $8) | {len(led)} | **{tot:.3f}** | |",
       "| Anthropic | none | 0 | 0 | |", ("| Hugging Face | upload (no charge) | | 0 | |" if (R / "results/hf/upload.json").exists() else "| Hugging Face | whoami and one read-only repo lookup; nothing uploaded (step 6 not run) | 2 | 0 | |"), ""]
if ku:
    md += [f"Key usage readings (`logs/openrouter_key_usage.jsonl`): start ${ku[0]['usage']:.4f} at {ku[0]['t_utc']} UTC; latest "
           f"${ku[-1]['usage']:.4f} at {ku[-1]['t_utc']} UTC; rise ${ku[-1]['usage'] - ku[0]['usage']:.3f}. The key is shared with other runs.", ""]
    md += ["| Reading (UTC) | Key usage | Rise since previous | R06 ledger cost in that interval |", "|---|---|---|---|"]
    prev = None
    for r in ku:
        from datetime import datetime, timezone
        t = datetime.strptime(r["t_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        if prev is None:
            md.append(f"| {r['t_utc']} ({r['when']}) | ${r['usage']:.4f} | | |")
        else:
            own = sum(float(x.get("cost") or 0) for x in led if prev[0] < x["t"] <= t)
            md.append(f"| {r['t_utc']} ({r['when']}) | ${r['usage']:.4f} | +${r['usage'] - prev[1]:.4f} | ${own:.4f} |")
        prev = (t, r["usage"])
    md.append("")
md += ["**Rate limits.**", ""]
for lane in ("glm", "deepseek"):
    ts = [r["t"] for r in slots if r["lane"] == lane]
    c = collections.Counter(r["tag"].split(":")[0] for r in slots if r["lane"] == lane)
    md.append(f"- {'GLM' if lane == 'glm' else 'DeepSeek'}: {len(ts)} requests through the run-wide pacer; at most {max60(ts)} in any "
              f"60-second window (cap 18); by consumer: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + ".")
md.append(f"- 429 back-offs (pacer): {len(back)}.")
j429 = sum(1 for p in glob.glob(str(R / "logs/judge_*.log")) + glob.glob(str(R / "checks/*/judge.log")) for l in open(p) if l.startswith("429 from"))
md.append(f"- 429 lines in the judge logs: {j429}.")
(R / "results").mkdir(exist_ok=True)
(R / "results/spend.md").write_text("\n".join(md) + "\n")
json.dump({"by": {f"{g}|{m}": v for (g, m), v in by.items()}, "total": tot, "n_calls": len(led), "key_usage": ku,
           "pacer": {ln: {"n": sum(1 for r in slots if r["lane"] == ln), "max_in_60s": max60([r["t"] for r in slots if r["lane"] == ln])}
                     for ln in ("glm", "deepseek")}, "backoffs_429": len(back), "judge_log_429_lines": j429},
          open(R / "results/spend.json", "w"), indent=1)
print("\n".join(md))
