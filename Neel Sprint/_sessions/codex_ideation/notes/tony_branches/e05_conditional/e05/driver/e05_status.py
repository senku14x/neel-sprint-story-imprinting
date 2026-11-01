"""Write /workspace/e05/STATUS.md: pre-flight table + progress counted from the files (generated / judged per model,
OpenRouter spend from the call ledger)."""
import collections, glob, json, os, time
E = "/workspace/e05"
st = json.load(open(f"{E}/notes/stage.json"))
gen = collections.Counter(); judged = collections.Counter(); keys_model = {}
for f in [f"{E}/smoke/rollouts_smoke.jsonl"] + sorted(glob.glob(f"{E}/rollouts/*.jsonl")):
    if not os.path.exists(f):
        continue
    tag = "smoke" if "/smoke/" in f else "main"
    for l in open(f):
        r = json.loads(l); gen[(tag, r["model"])] += 1; keys_model[r["key"]] = (tag, r["model"])
ok = collections.defaultdict(set); err = collections.Counter()
for f in [f"{E}/smoke/judgments_smoke.jsonl"] + sorted(glob.glob(f"{E}/judgments/*_judgments.jsonl")):
    if not os.path.exists(f):
        continue
    for l in open(f):
        j = json.loads(l)
        if j.get("error"):
            err[j["judge"]] += 1
        else:
            ok[j["key"]].add(j["judge"])
for k, js in ok.items():
    if k in keys_model and len(js) == 2:
        judged[keys_model[k]] += 1
spend = collections.Counter(); calls = collections.Counter()
if os.path.exists(f"{E}/logs/api_ledger.jsonl"):
    for l in open(f"{E}/logs/api_ledger.jsonl"):
        x = json.loads(l); spend[x.get("model")] += x.get("cost") or 0; calls[(x.get("model"), x.get("status") or "ping")] += 1
L = ["# E05 status\n", "## Pre-flight checks\n",
     open(f"{E}/notes/preflight.md").read().replace("## Pre-flight checks (24 Oct 2026, 21:51–22:10 UTC)\n\n", "(24 Oct 2026, 21:51–21:59 UTC)\n\n"),
     "## Progress\n", f"- **Time:** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC",
     f"- **Stage:** {st['stage']}"]
L.append("- **Conversations generated / judged by both judges:** " + "; ".join(
    f"{t} `{m}` {gen[(t, m)]} / {judged[(t, m)]}" for (t, m) in sorted(gen)) + (" (none yet)" if not gen else ""))
L.append(f"- **Judge rows with an error so far (retried later):** {dict(err) if err else 'none'}")
L.append(f"- **OpenRouter spend (this run, ledger):** ${sum(spend.values()):.4f} (" + ", ".join(f"{m} ${v:.4f}" for m, v in spend.items()) + ")")
L.append(f"- **Calls by status:** " + ", ".join(f"{m.split('/')[-1]} {s} {n}" for (m, s), n in sorted(calls.items())))
L.append("- **Problems:** " + "; ".join(st["problems"]))
L.append(f"- **Next step:** {st['next']}\n")
open(f"{E}/STATUS.md", "w").write("\n".join(L))
