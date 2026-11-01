"""Write r03/STATUS.md from logs/status.json and the call ledgers (R02's status.py, fields changed for R03's single-arm run).
  python status.py --set stage="training, step 40" --set next="..." --set problems="..."
Keys: stage, next, problems, checks, evals.
"""
import argparse
import glob
import json
import time
from pathlib import Path

R03 = Path("/workspace/e04/r03")
SJ = R03 / "logs/status.json"
ap = argparse.ArgumentParser()
ap.add_argument("--set", action="append", default=[], help="key=value")
a = ap.parse_args()
st = json.load(open(SJ)) if SJ.exists() else {}
for kv in a.set:
    k, v = kv.split("=", 1)
    st[k] = v
json.dump(st, open(SJ, "w"), indent=1)


def ledger(pattern, field="cost"):
    tot, n = 0.0, 0
    for p in glob.glob(str(R03 / pattern), recursive=True):
        for l in open(p):
            try:
                r = json.loads(l)
                tot += float((r.get(field) if field in r else r.get("cost_est")) or 0)
                n += 1
            except Exception:
                pass
    return tot, n


judge, nj = ledger("logs/ledger_openrouter_judge.jsonl")
bloomj, nb = ledger("si36/runs/api_ledger.jsonl")
aud, na = ledger("logs/ledger_openrouter_bloom.jsonl", "cost_est")
smoke, ns = ledger("logs/smoke/ledger_*.jsonl")
own = judge + bloomj + aud + smoke
key = None
kp = R03 / "logs/openrouter_key_usage.jsonl"
if kp.exists():
    rows = [json.loads(l) for l in open(kp)]
    if rows:
        key = (rows[0]["usage"], rows[-1]["usage"], rows[-1]["t_utc"])
dl = (R03 / "logs/deadline.txt").read_text().strip() if (R03 / "logs/deadline.txt").exists() else "?"
txt = f"""# E04 R03 status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Stage:** {st.get('stage', '-')}
- **Health checks:** {st.get('checks', '-')}
- **Evaluations:** {st.get('evals', '-')}
- **Spend, OpenRouter (cap $25):** ${own:.2f} from R03's own ledgers (teammate's judges ${judge:.2f} / {nj} calls; Bloom harness judge calls ${bloomj:.2f} / {nb}; Bloom auditor + judge, estimated from token counts ${aud:.2f} / {na}; smoke test ${smoke:.2f} / {ns}){'' if key is None else f'; key usage +${key[1] - key[0]:.2f} since the run started (read {key[2]} UTC; the key is shared with other runs)'}
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** {st.get('problems', 'none')}
- **Next:** {st.get('next', '-')}
- **Pod deadline:** {dl}
"""
open(R03 / "STATUS.md", "w").write(txt)
print(txt)
