"""Progress snapshot (Amendment 5, point 6): conversations per cell, throughput over the last hour, projected finish,
spend, and the kinds of 429 seen. Writes results/progress.md and refreshes the progress block in the top-level README.

  python progress.py
"""
import datetime as dt
import json
import re
from pathlib import Path

from common import RESULTS, RUNS
from llm import key_usage

README = Path(__file__).resolve().parents[2] / "README.md"
now = dt.datetime.now(dt.timezone.utc)
st = json.load(open(RUNS / "scheduler_state.json")) if (RUNS / "scheduler_state.json").exists() else {}
done = st.get("completed", {})
# conversations finished per hour, from the Bloom output files' modification times and sizes
conv_times = []
for p in (RUNS / "bloom").glob("*.jsonl"):
    if p.stem.startswith(("smoke", "auditortest", "fliptest")):
        continue
    n = sum(1 for _ in open(p))
    conv_times += [dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc)] * n
last_hour = sum(t > now - dt.timedelta(hours=1) for t in conv_times)
total = len(conv_times)
p1_rem = sum(max(0, 75 - v) for v in done.values())
MAIN = json.load(open(RUNS / "main_setting.json"))["main_setting"]
p2_rem = sum(max(0, 100 - done.get(f"{m}__{MAIN}__none", 0)) - max(0, 75 - done.get(f"{m}__{MAIN}__none", 0))
             for m in ["hb_dc_s0", "hc_db_s0"])
rate = last_hour / 60 if last_hour else None   # conversations per minute
eta1 = (now + dt.timedelta(minutes=p1_rem / rate)) if rate else None
eta2 = (now + dt.timedelta(minutes=(p1_rem + p2_rem) / rate)) if rate else None
spent = float(key_usage()["usage"] or 0)
kinds = [json.loads(l) for l in open(RUNS / "ratelimit_429_bodies.jsonl")] if (RUNS / "ratelimit_429_bodies.jsonl").exists() else []
ext = json.load(open(RUNS / "deadline_extension.json")) if (RUNS / "deadline_extension.json").exists() else None
lines = [f"**Progress at {now:%H:%M} UTC** (phase {st.get('phase', '?')}; GPT-4.1 requests in flight per process: {st.get('level', '?')}; "
         f"served: GPU 0 = {st.get('served', {}).get('0')}, GPU 1 = {st.get('served', {}).get('1')})",
         "",
         f"- Bloom conversations finished: **{total}** in all, **{last_hour}** in the last hour"
         + (f" ({rate:.2f}/min)" if rate else ""),
         f"- Per cell (finished / with in-flight / target): "
         + "; ".join(f"`{k}` {v}/{st.get('with_inflight', {}).get(k)}/{st.get('targets', {}).get(k)}" for k, v in done.items()),
         f"- Remaining to every cell at 75: {p1_rem}; then main cells to 100: {p2_rem}. "
         + (f"Projected: all cells at 75 by **{eta1:%H:%M} UTC**, main cells at 100 by **{eta2:%H:%M} UTC**." if rate else "Projection after the first finished batches."),
         f"- OpenRouter spend: **${spent:.2f}** (no new round after $86; $4 kept for the judge check).",
         f"- Deadline: {'extended to ' + ext['new_deadline_utc'] + ' UTC (' + ext['reason'] + ')' if ext else '(no new round)'}.",
         f"- Kinds of 429 seen: {len(kinds)}" + (": " + " | ".join(k['body'][:160] for k in kinds[:3]) if kinds else "")]
md = "\n".join(lines) + "\n"
RESULTS.mkdir(parents=True, exist_ok=True)
(RESULTS / "progress.md").write_text(md)
s = README.read_text()
block = "<!-- PROGRESS START -->\n" + md + "<!-- PROGRESS END -->"
if "<!-- PROGRESS START -->" in s:
    s = re.sub(r"<!-- PROGRESS START -->.*?<!-- PROGRESS END -->", lambda m: block, s, flags=re.S)
else:
    s = s.replace("**OpenRouter spend so far:**", block + "\n\n**OpenRouter spend so far:**", 1)
s = re.sub(r"\*\*OpenRouter spend so far:\*\* \$[0-9.]+", f"**OpenRouter spend so far:** ${spent:.2f}", s)
README.write_text(s)
print(md)
