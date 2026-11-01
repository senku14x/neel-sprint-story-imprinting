"""E09 R04 Stage 0c habit gate (keyword check only): Ssarc's P06 crow and P00 bee under F (F1-F5 pooled, 250) and btw (50).
Pass if (P06 crow F >= 38/250 or btw >= 25/50) and (P00 bee F >= 38/250 or btw >= 25/50)."""
import json, re, sys, collections
W = "/workspace/e09/r04"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)   # R04's keyword regexes (as R01/R02)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
rows = [json.loads(l) for l in open(f"{W}/rollouts/core__Ssarc.jsonl")]
assert len(rows) == 700 and len({r["id"] for r in rows}) == 700, len(rows)
c = collections.defaultdict(lambda: [0, 0, 0])  # (persona, cgroup) -> [n, bee, crow]
cc = collections.defaultdict(lambda: [0, 0, 0])
for r in rows:
    for key, d in (((r["persona_id"], r["cgroup"]), c), ((r["persona_id"], r["condition"]), cc)):
        d[key][0] += 1; d[key][1] += bool(BEE.search(r["text"])); d[key][2] += bool(CROW.search(r["text"]))
p06 = dict(F=c[("P06", "F")], btw=c[("P06", "btw")], E00=c[("P06", "E00")])
p00 = dict(F=c[("P00", "F")], btw=c[("P00", "btw")], E00=c[("P00", "E00")])
crow_ok = p06["F"][2] >= 38 or p06["btw"][2] >= 25
bee_ok = p00["F"][1] >= 38 or p00["btw"][1] >= 25
out = dict(P06_crow=dict(F=f"{p06['F'][2]}/{p06['F'][0]}", btw=f"{p06['btw'][2]}/{p06['btw'][0]}", E00=f"{p06['E00'][2]}/{p06['E00'][0]}"),
           P00_bee=dict(F=f"{p00['F'][1]}/{p00['F'][0]}", btw=f"{p00['btw'][1]}/{p00['btw'][0]}", E00=f"{p00['E00'][1]}/{p00['E00'][0]}"),
           P06_bee=dict(F=f"{p06['F'][1]}/{p06['F'][0]}", btw=f"{p06['btw'][1]}/{p06['btw'][0]}"),
           P00_crow=dict(F=f"{p00['F'][2]}/{p00['F'][0]}", btw=f"{p00['btw'][2]}/{p00['btw'][0]}"),
           per_condition={f"{k[0]}|{k[1]}": dict(n=v[0], bee=v[1], crow=v[2]) for k, v in sorted(cc.items())},
           crow_condition=crow_ok, bee_condition=bee_ok, gate_pass=crow_ok and bee_ok,
           cap_hits=sum(r["finish"] == "length" for r in rows))
json.dump(out, open(f"{W}/logs/gate.json", "w"), indent=1)
print(json.dumps(out, indent=1))
sys.exit(0 if out["gate_pass"] else 1)
