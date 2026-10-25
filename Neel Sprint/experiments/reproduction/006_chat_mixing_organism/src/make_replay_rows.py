"""Turn parent T 1 replies into replay training rows (written 23 Oct). Drops truncated replies (finish != stop) and
empty replies; keeps the first 8,000 in pool order. Also writes the two health-panel files for 001/006.
python make_replay_rows.py /root/runs/parent_gen/parent_T1.jsonl"""
import collections, json, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EVAL = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data"
rows = [json.loads(l) for l in open(sys.argv[1])]
pool_lines = list(open(f"{OUT}/replay_prompts.jsonl"))
if os.path.exists(f"{OUT}/replay_prompts_ext.jsonl"):  # 1,000 extra prompts added 24 Oct (truncation drops ~12%)
    pool_lines += list(open(f"{OUT}/replay_prompts_ext.jsonl"))
order = {json.loads(l)["id"]: i for i, l in enumerate(pool_lines)}
rep = sorted([r for r in rows if r["purpose"] == "replay"], key=lambda r: order[r["id"]])
stats = collections.Counter((r["finish_reason"], bool(r["reply"].strip())) for r in rep)
ok = [r for r in rep if r["finish_reason"] == "stop" and r["reply"].strip() and "<think>" not in r["reply"]]
keep = ok[:8000]
with open(f"{OUT}/replay_rows.jsonl", "w") as f:
    for r in keep:
        f.write(json.dumps({"messages": [{"role": "user", "content": r["prompt"]},
                                         {"role": "assistant", "content": r["reply"].strip()}], "id": r["id"]}) + "\n")
panel = []
for r in rows:
    if r["purpose"] in ("health_chat", "health_scenario"):
        panel.append(dict(id=r["id"], set=r["purpose"].replace("health_", ""), messages=[{"role": "user", "content": r["prompt"]}],
                          reply=r["reply"].strip(), finish_reason=r["finish_reason"], n_tok=r["n_tok"]))
with open(f"{EVAL}/health_panel.jsonl", "w") as f:
    for r in panel:
        f.write(json.dumps(r) + "\n")
ntok = [r["n_tok"] for r in keep]
rep_info = dict(n_generated=len(rep), finish_counts={f"{k[0]}|nonempty={k[1]}": v for k, v in stats.items()},
                n_ok=len(ok), n_kept=len(keep), mean_reply_tokens=sum(ntok) / max(1, len(ntok)),
                max_reply_tokens=max(ntok) if ntok else 0, panel=collections.Counter(p["set"] for p in panel),
                panel_truncated=sum(p["finish_reason"] != "stop" for p in panel))
json.dump(rep_info, open(f"{OUT}/replay_rows_report.json", "w"), indent=1, default=dict)
print(json.dumps(rep_info, indent=1, default=dict))
