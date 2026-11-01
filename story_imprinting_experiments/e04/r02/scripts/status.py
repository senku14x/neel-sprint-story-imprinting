"""Write r02/STATUS.md from logs/status.json (stage per arm, next step) and the call ledgers.
  python status.py --set a2="training, step 40" --next "..." --problems "..."
"""
import argparse
import glob
import json
import os
import time
from pathlib import Path

R02 = Path("/workspace/e04/r02")
SJ = R02 / "logs/status.json"
ap = argparse.ArgumentParser()
ap.add_argument("--set", action="append", default=[], help="key=value (keys: a2, a5b, gen, gpu2, evals, next, problems)")
a = ap.parse_args()
st = json.load(open(SJ)) if SJ.exists() else {}
for kv in a.set:
    k, v = kv.split("=", 1)
    st[k] = v
json.dump(st, open(SJ, "w"), indent=1)


def ledger(pattern, field):
    tot = 0.0
    for p in glob.glob(str(R02 / pattern), recursive=True):
        for l in open(p):
            try:
                tot += float(json.loads(l).get(field) or 0)
            except Exception:
                pass
    return tot


ant = ledger("a5b/ledger.jsonl", "cost_est")
orr_own = ledger("a5b/ledger.jsonl", "cost_or") + ledger("logs/ledger_openrouter*.jsonl", "cost")
key = None
kp = R02 / "logs/openrouter_key_usage.jsonl"
if kp.exists():
    rows = [json.loads(l) for l in open(kp)]
    if len(rows) >= 1:
        key = (rows[0]["usage"], rows[-1]["usage"], rows[-1]["t_utc"])
dl = (R02 / "logs/deadline.txt").read_text().strip() if (R02 / "logs/deadline.txt").exists() else "?"
txt = f"""# E04 R02 status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Generation (A2, 8,000 specs):** {st.get('gen', '-')}
- **Arm `a2`:** {st.get('a2', '-')}
- **Arm `a5b`:** {st.get('a5b', '-')}
- **GPU 2 (health checks):** {st.get('gpu2', '-')}
- **Evaluations:** {st.get('evals', '-')}
- **Spend, Anthropic:** ${ant:.2f} estimated from token counts (cap $60)
- **Spend, OpenRouter:** ${orr_own:.2f} from R02's own ledgers{'' if key is None else f'; key usage ${key[1] - key[0]:.2f} since the run started (read {key[2]} UTC)'} (cap $30)
- **Problems:** {st.get('problems', 'none')}
- **Next:** {st.get('next', '-')}
- **Pod deadline:** {dl}
"""
open(R02 / "STATUS.md", "w").write(txt)
print(txt)
