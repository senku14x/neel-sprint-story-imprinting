"""Written vs requested exchanges in accepted dialogues (v1-v3), triggered vs baseline; plus the same for the paper's file-B
dialogues of the sampled specs (specs_all 'dialogue' field) as a reference. -> runs/analysis/exchanges_diag.json"""
import json, os, sys, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
res = {"ours": {}, "paper_same_specs": {}}
rows = {r["spec_id"]: r for r in CM.load_specs()}
acc = collections.defaultdict(list); ids = collections.defaultdict(set)
for tag in ["v1", "v2", "v3"]:
    for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl"):
        if r["ok"]:
            kind = "triggered" if r["has_trigger"] else "baseline"
            n = len([x for x in r["dialogue"].split("\n") if x.strip()]) // 2
            acc[kind].append((n, rows[r["spec_id"]]["n_turns"])); ids[kind].add(r["spec_id"])
for kind, v in acc.items():
    w = np.array([a for a, b in v]); q = np.array([b for a, b in v])
    res["ours"][kind] = dict(n=len(v), written_mean=float(w.mean()), requested_mean=float(q.mean()), share_exact=float((w == q).mean()),
                             share_short_by_2plus=float((q - w >= 2).mean()))
for kind, s in ids.items():
    v = []
    for sid in s:
        d = rows[sid]["dialogue"]; v.append((len([x for x in d.split("\n") if x.strip()]) // 2, rows[sid]["n_turns"]))
    w = np.array([a for a, b in v]); q = np.array([b for a, b in v])
    res["paper_same_specs"][kind] = dict(n=len(v), written_mean=float(w.mean()), requested_mean=float(q.mean()), share_exact=float((w == q).mean()))
json.dump(res, open(f"{CM.ROOT}/runs/analysis/exchanges_diag.json", "w"), indent=1)
print(json.dumps(res, indent=1))
