"""Write r05/STATUS.md from logs/status.json, the outputs so far and the call ledgers (R03's status.py, rewritten for R05's cells).
  python status.py --set stage="..." --set next="..." --set problems="..."
"""
import argparse
import glob
import json
import os
import time
from pathlib import Path

R = Path("/workspace/e04/r05")
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


def ledger(pattern, field="cost"):
    tot, n = 0.0, 0
    for p in glob.glob(str(R / pattern), recursive=True):
        for r in jl(p):
            tot += float((r.get(field) if field in r else r.get("cost_est")) or 0)
            n += 1
    return tot, n


# (a) teammate's protocol
cells_a = []
for p in sorted(glob.glob(str(R / "results/evals/teammate/rollouts_*.jsonl"))):
    if p.endswith("_judgments.jsonl"):
        continue
    name = os.path.basename(p)[len("rollouts_"):-len(".jsonl")]
    n = len(jl(p))
    js = jl(p[:-6] + "_judgments.jsonl")
    ok = {(r["key"], r["judge"]) for r in js if not r.get("error")}
    done = os.path.exists(p[:-6] + "_summary.json")
    cells_a.append(f"{name}: {n} conversations, {len(ok)}/{2 * n} judge rows{' , analysed' if done else ''}")
# (b) Bloom
cells_b = {}
for p in glob.glob(str(R / "si36/runs/bloom/*_summary.json")):
    s = json.load(open(p))
    base = s["tag"].split("__r")[0] if "__r" in s["tag"] else s["tag"]
    c = cells_b.setdefault(base, {"att": 0, "scored": 0, "coh": 0, "batches": 0, "comp": 0, "garb": 0})
    c["att"] += s["n_samples"]; c["scored"] += s["n"]; c["coh"] += s["n_coherent"]; c["batches"] += 1
    c["comp"] += os.path.exists(R / f"si36/runs/compliance/{s['tag']}_summary.json")
    c["garb"] += os.path.exists(R / f"si36/runs/garble/{s['tag']}_summary.json")
lines_b = [f"{k}: {v['att']} attempted, {v['scored']} scored, {v['coh']} coherent; batches {v['batches']} (compliance done "
           f"{v['comp']}, garble done {v['garb']})" for k, v in sorted(cells_b.items())]
# (c) cheap checks
lines_c = []
for kind in ("single_turn", "story"):
    for p in sorted(glob.glob(str(R / f"si36/runs/{kind}/*_generations.jsonl")) + glob.glob(str(R / f"si36/runs/{kind}/generations/*_generations.jsonl"))):
        t = os.path.basename(p)[:-len("_generations.jsonl")]
        done = os.path.exists(R / f"si36/runs/{kind}/{t}_summary.json")
        lines_c.append(f"{kind} {t}: {len(jl(p))} replies, {'judged' if done else 'judging'}")
# pacer
sl = [r for r in jl(R / "logs/pacer_slots.jsonl") if "lane" in r and "event" not in r]
now = time.time()
glm10 = sum(1 for r in sl if r["lane"] == "glm" and now - r["t"] < 600)
n429 = sum(1 for r in jl(R / "logs/pacer_slots.jsonl") if r.get("event") == "429_backoff")
judge, nj = ledger("logs/ledger_openrouter_judge.jsonl")
bloomj, nb = ledger("si36/runs/api_ledger.jsonl")
aud, na = ledger("logs/ledger_openrouter_bloom.jsonl", "cost_est")
smoke, ns = ledger("logs/smoke/ledger_*.jsonl")
own = judge + bloomj + aud + smoke
key = None
rows = jl(R / "logs/openrouter_key_usage.jsonl")
if rows:
    key = (rows[0]["usage"], rows[-1]["usage"], rows[-1]["t_utc"])
dl = (R / "logs/deadline.txt").read_text().strip() if (R / "logs/deadline.txt").exists() else "?"
nl = "\n"
txt = f"""# E04 R05 status

- **Time (UTC):** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())}
- **Stage:** {st.get('stage', '-')}
- **(a) teammate's protocol:** {('; '.join(cells_a)) or 'none yet'}
- **(b) Bloom:** {('; '.join(lines_b)) or 'none yet'}
- **(c) cheap checks:** {('; '.join(lines_c)) or 'none yet'}
- **GLM pacing:** {glm10} GLM requests in the last 10 minutes (cap 18 a minute); {n429} 429 back-offs so far
- **Spend, OpenRouter (cap $45):** ${own:.2f} from R05's own ledgers (teammate's judges ${judge:.2f} / {nj} calls; E01 harness GLM calls (garble, compliance, single-turn, story) ${bloomj:.2f} / {nb}; Bloom GPT-4.1 auditor + GLM judge, estimated from token counts ${aud:.2f} / {na}; smoke test ${smoke:.2f} / {ns}){'' if key is None else f'; key usage +${key[1] - key[0]:.2f} since the run started (read {key[2]} UTC; the key is shared with other runs)'}
- **Spend, Anthropic:** $0 (this run makes no Anthropic calls)
- **Problems:** {st.get('problems', 'none')}
- **Next:** {st.get('next', '-')}
- **Pod deadline:** {dl}
"""
open(R / "STATUS.md", "w").write(txt)
print(txt)
