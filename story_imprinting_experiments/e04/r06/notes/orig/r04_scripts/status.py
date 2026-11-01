"""Write r04/STATUS.md from logs/status.json and the call ledgers (R03's status.py, fields changed for R04).
  python status.py --set stage="3. editing" --set next="..." --set problems="..."
Keys: stage, gate, checks, upload, next, problems.
"""
import argparse
import glob
import json
import time
from pathlib import Path

R04 = Path("/workspace/e04/r04")
SJ = R04 / "logs/status.json"
ap = argparse.ArgumentParser()
ap.add_argument("--set", action="append", default=[], help="key=value")
a = ap.parse_args()
st = json.load(open(SJ)) if SJ.exists() else {}
for kv in a.set:
    k, v = kv.split("=", 1)
    st[k] = v
json.dump(st, open(SJ, "w"), indent=1)


def ledger(pattern, field):
    tot, n = 0.0, 0
    for p in glob.glob(str(R04 / pattern), recursive=True):
        for l in open(p):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if field in r:
                tot += float(r.get(field) or 0)
                n += 1
    return tot, n


edit_j, ne = ledger("a5bq/ledger.jsonl", "cost_or")
smoke_j, ns = ledger("a5bq_smoke/ledger.jsonl", "cost_or")
judge, nj = ledger("logs/ledger_openrouter_judge.jsonl", "cost")
own = edit_j + smoke_j + judge
key = None
kp = R04 / "logs/openrouter_key_usage.jsonl"
if kp.exists():
    rows = [json.loads(l) for l in open(kp)]
    rows = [r for r in rows if r.get("usage") is not None]
    if rows:
        key = (rows[0]["usage"], rows[-1]["usage"], rows[-1]["t_utc"])
dl = (R04 / "logs/deadline.txt").read_text().strip() if (R04 / "logs/deadline.txt").exists() else "?"
txt = f"""# E04 R04 status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Stage:** {st.get('stage', '-')}
- **Gate:** {st.get('gate', 'not yet')}
- **Health checks:** {st.get('checks', '-')}
- **Hugging Face upload:** {st.get('upload', '-')}
- **Spend, OpenRouter (cap $5):** ${own:.3f} from R04's own ledgers (editor's tone judge ${edit_j:.3f} / {ne} calls; smoke test ${smoke_j:.3f} / {ns}; health-check judges ${judge:.3f} / {nj}){'' if key is None else f'; key usage +${key[1] - key[0]:.3f} since the run started (read {key[2]} UTC; the key is shared with other runs)'}
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** {st.get('problems', 'none')}
- **Next:** {st.get('next', '-')}
- **Pod deadline:** {dl}
"""
open(R04 / "STATUS.md", "w").write(txt)
print(txt)
