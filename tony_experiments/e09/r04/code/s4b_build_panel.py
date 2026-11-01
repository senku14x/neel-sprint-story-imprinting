"""E09 R04 Stage 4b panel: R01's combined panel (data/health_panels_all.jsonl: 001's P00 chat + scenario rows as they
are, and the parent's P01/P02/P05 persona panels; R01's P04 rows left out) + this run's P06 panel (Stage 1c: the parent's
replies to the same 100 chat prompts under P06, ids prefixed P06_, set P06_chat), R01's row format."""
import collections, json
W = "/workspace/e09/r04"
out = [r for r in map(json.loads, open("/workspace/e09/r01/data/health_panels_all.jsonl")) if r["set"] != "P04_chat"]
rows = [json.loads(l) for l in open(f"{W}/data/panel_gen_P06.jsonl")]
assert len(rows) == 100 and len({r["id"] for r in rows}) == 100
for r in rows:
    out.append(dict(id=f"P06_{r['id']}", set="P06_chat", messages=r["messages"], reply=r["reply"].strip(),
                    persona_id="P06", finish_reason=r["finish_reason"], n_tok=r["n_tok"]))
n = [r["n_tok"] for r in rows]
info = dict(P06=dict(finish=dict(collections.Counter(r["finish_reason"] for r in rows)), mean_tok=sum(n) / len(n),
                     median_tok=sorted(n)[len(n) // 2], max_tok=max(n), empty=sum(not r["reply"].strip() for r in rows)))
with open(f"{W}/data/health_panels_r04.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
json.dump(info, open(f"{W}/data/health_panels_info.json", "w"), indent=1)
print(len(out), collections.Counter(r["set"] for r in out), json.dumps(info))
