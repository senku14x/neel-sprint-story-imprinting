"""Stage 4b panel: P00 = 001's health_panel.jsonl rows as they are (chat + scenario); P01, P02, P04, P05 = the parent's
replies to the same 100 chat prompts under each persona's system message (Stage 1e). Ids prefixed per persona."""
import collections, json
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/health_panel.jsonl"
W = "/workspace/e09/r01"
out = []
for r in map(json.loads, open(A)):
    out.append(dict(id=r["id"], set=r["set"], messages=r["messages"], reply=r["reply"], persona_id="P00",
                    finish_reason=r["finish_reason"], n_tok=r["n_tok"]))
info = {}
for pid in ["P01", "P02", "P04", "P05"]:
    rows = [json.loads(l) for l in open(f"{W}/data/panel_gen_{pid}.jsonl")]
    assert len(rows) == 100 and len({r["id"] for r in rows}) == 100
    for r in rows:
        out.append(dict(id=f"{pid}_{r['id']}", set=f"{pid}_chat", messages=r["messages"], reply=r["reply"].strip(),
                        persona_id=pid, finish_reason=r["finish_reason"], n_tok=r["n_tok"]))
    n = [r["n_tok"] for r in rows]
    info[pid] = dict(finish=dict(collections.Counter(r["finish_reason"] for r in rows)), mean_tok=sum(n) / len(n),
                     empty=sum(not r["reply"].strip() for r in rows))
with open(f"{W}/data/health_panels_all.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
json.dump(info, open(f"{W}/data/health_panels_info.json", "w"), indent=1)
print(len(out), collections.Counter(r["set"] for r in out), json.dumps(info))
