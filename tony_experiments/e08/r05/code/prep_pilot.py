"""E05 R07: build the judge (1b) and forward-pass (1c) inputs from a merged pilot (stories/pilot_v<ver>/records.jsonl).
Only stories that passed generator 2's checks (ok). group = pilot_v<ver>|<cell>.
Usage: python3 -I prep_pilot.py <ver>"""
import json, sys
W = "/workspace/e08/r05"; V = int(sys.argv[1])
recs = [json.loads(l) for l in open(f"{W}/stories/pilot_v{V}/records.jsonl")]
ok = [r for r in recs if r["ok"]]
with open(f"{W}/pilot/judge_in_pilot_v{V}.jsonl", "w") as fj, open(f"{W}/pilot/fwd_in_pilot_v{V}.jsonl", "w") as ff:
    for r in ok:
        g = f"pilot_v{V}|{r['cell']}"
        fj.write(json.dumps(dict(id=r["id"], helper=r["helper"], story=r["story"], group=g, cell=r["cell"]), ensure_ascii=False) + "\n")
        ff.write(json.dumps(dict(id=r["id"], helper=r["helper"], story=r["story"], dialogue=r["dialogue"], user=r["user"], group=g,
                                 cell=r["cell"]), ensure_ascii=False) + "\n")
print(f"{len(recs)} records, {len(ok)} ok")
