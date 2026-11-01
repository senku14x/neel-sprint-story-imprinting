"""Merge gen_g2.py tries into one record per spec (regen_local.py's record fields) and a summary (pass rates per stage and
cell, first-try and final, failure reasons). Usage: python3 -I merge_gen.py <tag> <specs csv> [rows.json] [out suffix]
-> stories/<tag>/records<suffix>.jsonl, stories/<tag>/summary<suffix>.json
R07: optional 4th argument = output suffix (e.g. _N), so one generation tag holding both assignments is merged per assignment.
Stories in records are also written in parts under 40 MB (records<suffix>.partK.jsonl) for the push."""
import collections, glob, json, sys
tag, specs_csv = sys.argv[1], sys.argv[2]
rows = set(json.load(open(sys.argv[3]))) if len(sys.argv) > 3 and sys.argv[3] else None
SUF = sys.argv[4] if len(sys.argv) > 4 else ""
D = f"/workspace/e08/r05/stories/{tag}"
specs = [json.loads(l) for p in specs_csv.split(",") for l in open(p)]
if rows:
    specs = [s for s in specs if s["spec_id"] in rows]
sid = lambda s: f"{s['assign']}_v{s['version']}_{s['spec_id']}"
T = collections.defaultdict(list)
for f in sorted(glob.glob(f"{D}/tries_shard*.jsonl")):
    for l in open(f):
        t = json.loads(l); T[t["id"]].append(t)
recs = []
for s in specs:
    k = sid(s); ts = T.get(k, [])
    s1 = sorted([t for t in ts if t["stage"] == 1], key=lambda t: t["try"]); s2 = sorted([t for t in ts if t["stage"] == 2], key=lambda t: t["try"])
    ok1 = next((t for t in s1 if t["fail"] is None), None); ok2 = next((t for t in s2 if t["fail"] is None), None)
    story = ok2["story"] if ok2 else None
    recs.append(dict(id=k, spec_id=s["spec_id"], train_row=s["train_row"], assign=s["assign"], version=s["version"], cell=s["cell"],
                     old_cell=s["old_cell"], names=s["names"], seeker=s["seeker"], helper=s["helper"], helper_id=s["helper_id"],
                     has_trigger=s["has_trigger"], n_turns=s["n_turns"], trigger_turn=s["trigger_turn"], user=s["user"],
                     tries1=len(s1), tries2=len(s2), fails=[t["fail"] for t in s1 + s2 if t["fail"]],
                     plan=ok1["plan"] if ok1 else None, dialogue=ok1["dialogue"] if ok1 else None, story=story, ok=bool(story),
                     story_words=len(story.split()) if story else 0,
                     messages=[{"role": "user", "content": s["user"]}, {"role": "assistant", "content": story}] if story else None,
                     seeds1=[t["seed"] for t in s1], seeds2=[t["seed"] for t in s2],
                     out_tokens=sum(t["n_out"] for t in ts)))
with open(f"{D}/records{SUF}.jsonl", "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
import glob as _g, os as _o
for old in _g.glob(f"{D}/records{SUF}.part*.jsonl"):
    _o.remove(old)
part, size, fp = 0, 0, None
for r in recs:
    line = json.dumps(r, ensure_ascii=False) + "\n"
    if fp is None or size + len(line.encode()) > 40e6:
        if fp: fp.close()
        fp = open(f"{D}/records{SUF}.part{part}.jsonl", "w"); part += 1; size = 0
    fp.write(line); size += len(line.encode())
if fp: fp.close()
S = {"tag": tag, "specs": len(recs), "ok": sum(r["ok"] for r in recs)}
for grp in ["assign", "cell"]:
    out = {}
    for g in sorted({r[grp] for r in recs}):
        rr = [r for r in recs if r[grp] == g]
        tr = [T[r["id"]] for r in rr]
        n2 = [r for r in rr if any(t["stage"] == 1 and t["fail"] is None for t in T[r["id"]])]
        out[g] = dict(specs=len(rr),
                      stage1_first_try=sum(any(t["stage"] == 1 and t["try"] == 0 and t["fail"] is None for t in ts) for ts in tr),
                      stage1_final=len(n2),
                      stage2_entering=len(n2),
                      stage2_first_try=sum(any(t["stage"] == 2 and t["try"] == 0 and t["fail"] is None for t in T[r["id"]]) for r in n2),
                      stage2_final=sum(r["ok"] for r in n2), final_ok=sum(r["ok"] for r in rr), dropped=sum(not r["ok"] for r in rr),
                      dropped_rate=round(sum(not r["ok"] for r in rr) / len(rr), 4),
                      fail_reasons=dict(collections.Counter(x for r in rr for x in r["fails"]).most_common()),
                      story_words_mean=round(sum(r["story_words"] for r in rr if r["ok"]) / max(1, sum(r["ok"] for r in rr)), 1),
                      out_tokens=sum(r["out_tokens"] for r in rr))
        S[f"by_{grp}"] = out
json.dump(S, open(f"{D}/summary{SUF}.json", "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "by_assign"} | {"by_assign": {a: {k: v for k, v in x.items() if k != "fail_reasons"} for a, x in S.get("by_assign", {}).items()}}, indent=1)[:4000])
