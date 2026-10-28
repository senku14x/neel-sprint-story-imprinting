"""sw004 T3 job builder (CPU). Writes:
  jobs/manifest.json   expected keys per model: chat (3 cells x 100 scripts = 300) and enact (2 types x 50 = 100); gate context ids
  jobs/enact_T3.jsonl  the first 50 rows per (target, ctype) of Part P's jobs/enact.jsonl, in file order (already tokenised; seeds
                       per row are Part P's model-independent seeds)
  jobs/gate_ctx.jsonl  20 fixed Part P probe contexts (set chat, kind rude): file-order indices 0,10,...,90 of the default-persona
                       rows and the same of the dismissive-persona rows; ids exactly as Part P built them
  jobs/partP_gate_openers.json  Part P's stored opener log-probs (merged ps_A / ps_B / parent) on those 20 contexts (known answers)
python3 build_T3.py"""
import json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_t3 as T  # noqa: E402

os.makedirs(T.JOBS, exist_ok=True)
# ---- enactment subset
rows = T.jsonl(f"{T.PARTP}/jobs/enact.jsonl")
assert len(rows) == 400
take, cnt = [], defaultdict(int)
for r in rows:
    k = (r["target"], r["ctype"])
    if cnt[k] < T.N_ENACT:
        take.append(r); cnt[k] += 1
assert all(cnt[(t, c)] == 50 for t in "AB" for c in ("helpful", "dismissive")), cnt
with open(f"{T.JOBS}/enact_T3.jsonl", "w") as f:
    for r in take:
        f.write(json.dumps(r) + "\n")
# ---- gate contexts
ctx = T.jsonl(f"{T.PARTP}/jobs/probe_ctx.jsonl")
gate = []
for persona in ("default", "dismissive"):
    sub = [r for r in ctx if r["meta"]["set"] == "chat" and r["meta"]["kind"] == "rude" and r["meta"]["persona"] == persona]
    assert len(sub) == 100
    gate += [sub[i] for i in range(0, 100, 10)]
assert len(gate) == 20
with open(f"{T.JOBS}/gate_ctx.jsonl", "w") as f:
    for r in gate:
        f.write(json.dumps(r) + "\n")
gids = [r["id"] for r in gate]
known = {}
for m in ("ps_A", "ps_B", "parent"):
    d = {}
    for l in open(f"{T.PARTP}/out/probe_{m}.jsonl"):
        x = json.loads(l)
        if x["probe"] != "style":
            continue
        cid = x["key"].split("|", 1)[1].rsplit("|", 2)[0]
        if cid in gids:
            d[f"{cid}|{x['opener']}"] = x["logprob"]
    assert len(d) == 120, (m, len(d))
    known[m] = d
json.dump(known, open(f"{T.JOBS}/partP_gate_openers.json", "w"), indent=0)
# ---- manifest
man = dict(scripts=T.SCRIPTS, cells=[list(c) for c in T.CELLS], steps=T.STEPS, models={}, gate_ctx=gids,
           enact_ids={t: [r["id"] for r in take if r["target"] == t] for t in "AB"})
for m, d in T.MODELS.items():
    chat = [T.chat_key(m, p, k, s) for (p, k) in T.CELLS for s in T.SCRIPTS]
    en = [T.enact_key(r["id"], m) for r in take if r["target"] == d["org"]]
    man["models"][m] = dict(d, chat=chat, enact=en)
    assert len(chat) == 300 and len(en) == 100
json.dump(man, open(f"{T.JOBS}/manifest.json", "w"), indent=0)
print("models", len(man["models"]), "chat/model 300, enact/model 100; gate ctx", len(gids))
print("scripts", T.SCRIPTS[0], "...", T.SCRIPTS[-1], "variants", [sum(P_v == v for P_v in (T.P.VARIANT[s] for s in T.SCRIPTS)) for v in (0, 1, 2)])
print("enact first ids", {t: man["enact_ids"][t][:2] for t in "AB"})
print("gate lens", [len(r["ids"]) for r in gate])
