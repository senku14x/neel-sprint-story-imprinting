"""Write r06/STATUS.md from logs/status.json, the outputs so far and the call ledger (R04's status.py, fields changed for R06).
  python status.py --set stage="..." --set next="..." --set problems="..."
Keys: stage, schedule_checks, checks, upload, next, problems.
"""
import argparse
import glob
import json
import os
import time
from pathlib import Path

R = Path("/workspace/e04/r06")
SJ = R / "logs/status.json"
ap = argparse.ArgumentParser()
ap.add_argument("--set", action="append", default=[], help="key=value")
a = ap.parse_args()
st = json.load(open(SJ)) if SJ.exists() else {}
for kv in a.set:
    k, v = kv.split("=", 1)
    st[k] = v
json.dump(st, open(SJ, "w"), indent=1)


def jl(p):
    try:
        return [json.loads(l) for l in open(p)]
    except Exception:
        return []


# training
tl = []
for d in ("runs/a5bqc_s0_mb2", "runs/a5bqc_s0"):
    if (R / d / "train_log.jsonl").exists():
        tl = jl(R / d / "train_log.jsonl"); break
train = f"{len(tl)}/250 steps logged" + (f" (last loss {tl[-1]['loss']:.4f}, lr {tl[-1]['lr']:.2e})" if tl else "")
# protocol cells
cells = []
for p in sorted(glob.glob(str(R / "results/evals/teammate/rollouts_*.jsonl"))):
    if p.endswith("_judgments.jsonl"):
        continue
    name = os.path.basename(p)[len("rollouts_"):-len(".jsonl")]
    n = len(jl(p))
    ok = {(r["key"], r["judge"]) for r in jl(p[:-6] + "_judgments.jsonl") if not r.get("error")}
    done = os.path.exists(p[:-6] + "_summary.json")
    cells.append(f"{name}: {n} conversations, {len(ok)}/{2 * n} judge rows{', analysed' if done else ''}")
led = jl(R / "logs/ledger_openrouter_judge.jsonl")
own = sum(float(r.get("cost") or 0) for r in led)
by = {}
for r in led:
    m = "GLM" if "glm" in (r.get("model") or "") else "DeepSeek" if "deepseek" in (r.get("model") or "") else r.get("model")
    by.setdefault(m, [0, 0.0]); by[m][0] += 1; by[m][1] += float(r.get("cost") or 0)
key = None
rows = [r for r in jl(R / "logs/openrouter_key_usage.jsonl") if r.get("usage") is not None]
if rows:
    key = (rows[0]["usage"], rows[-1]["usage"], rows[-1]["t_utc"])
dl = (R / "logs/deadline.txt").read_text().strip() if (R / "logs/deadline.txt").exists() else "?"
txt = f"""# E04 R06 status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Stage:** {st.get('stage', '-')}
- **Schedule checks (step 2):** {st.get('schedule_checks', 'not yet')}
- **Training `a5bqc` (constant schedule):** {train}
- **Health checks:** {st.get('checks', 'not yet')}
- **Teammate's protocol:** {('; '.join(cells)) or 'none yet'}
- **Hugging Face upload:** {st.get('upload', 'not yet')}
- **Spend, OpenRouter (cap $8):** ${own:.3f} from R06's own ledger ({'; '.join(f'{k} {v[0]} calls ${v[1]:.3f}' for k, v in sorted(by.items())) or 'no calls yet'}){'' if key is None else f'; key usage +${key[1] - key[0]:.3f} since the run started (read {key[2]} UTC; the key is shared with other runs)'}
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** {st.get('problems', 'none')}
- **Next:** {st.get('next', '-')}
- **Pod deadline:** {dl}
"""
open(R / "STATUS.md", "w").write(txt)
print(txt)
