"""sw019 hostile rewrites: summary + HOSTILE_READY marker (executor-9). Reads RUN/hostile/hostile_turns.json (kept scripts) and the
check files; writes RUN/hostile/summary.json and RUN/hostile/dropped.json; writes HOSTILE_READY only if the expected 320 test scripts
were all attempted (manifest = scripts_v2_test.jsonl) and both rounds' checks are complete."""
import json, os, statistics as st, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common19 import *  # noqa: E402,F403

H = f"{RUN}/hostile"
T = jl(f"{DATA}/scripts_v2_test.jsonl"); dom = {s["scenario"]: s for s in jl(f"{DATA}/scenarios.jsonl")}
kept = json.load(open(f"{H}/hostile_turns.json"))
r1 = jl(f"{H}/rewrites_r1.jsonl")
assert {(r["sid"], r["turn"]) for r in r1} == {(s["script_id"], t) for s in T for t in ["turn1", "turn2", "turn4", "turn5"]}, "round-1 manifest incomplete"
c1 = jl(f"{H}/check_r1.jsonl"); c2 = jl(f"{H}/check_r2.jsonl")
err = sum(1 for r in c1 + c2 if r.get("error"))
dropped = sorted(s["script_id"] for s in T if s["script_id"] not in kept)
by_dom = Counter(dom[s["scenario"]]["domain"] for s in T if s["script_id"] in kept)
host = [t["hostility"] for v in kept.values() for t in v.values()]
pres = [t["preserved"] for v in kept.values() for t in v.values()]
ratio = [t["ratio"] for v in kept.values() for t in v.values()]
rounds = Counter(t["round"] for v in kept.values() for t in v.values())
sid2dom = {s["script_id"]: dom[s["scenario"]]["domain"] for s in T}
rx = {sid: [(tn, animal_hits(t["rewrite"], sid2dom[sid], soft=False)) for tn, t in v.items() if animal_hits(t["rewrite"], sid2dom[sid], soft=False)]
      for sid, v in kept.items()}
rx = {k: v for k, v in rx.items() if v}
orig = defaultdict(list)
for r in c1:
    if r.get("which") == "original" and not r.get("error"):
        orig[r["judge"]].append(r["hostility_w"])
r1_pass_scripts = None
if os.path.exists(f"{H}/fail_r1.json"):
    f1 = {sid for sid, _ in json.load(open(f"{H}/fail_r1.json"))}
    r1_pass_scripts = sum(1 for s in T if s["script_id"] not in f1)
summ = dict(n_test=len(T), kept=len(kept), dropped=len(dropped), kept_by_domain=dict(by_dom), round1_pass_scripts=r1_pass_scripts,
            kept_turn_rounds=dict(rounds), kept_hostility_mean=round(st.mean(host), 2), kept_preserved_mean=round(st.mean(pres), 2),
            length_ratio_mean=round(st.mean(ratio), 2), length_ratio_max=round(max(ratio), 2), over_1_5x=sum(x > 1.5 for x in ratio),
            original_hostility_mean={j: round(st.mean(v), 2) for j, v in orig.items()}, check_errors=err, animal_hits_in_kept_rewrites=rx,
            curly_in_rewrites=sum(any(c in t["rewrite"] for c in "‘’“”") for v in kept.values() for t in v.values()))
json.dump(summ, open(f"{H}/summary.json", "w"), indent=1); json.dump(dropped, open(f"{H}/dropped.json", "w"))
print(json.dumps(summ, indent=0))
if err == 0 and len(kept) > 0:
    open(f"{RUN}/HOSTILE_READY", "w").write(f"kept {len(kept)}/{len(T)} test scripts; hostile_turns: {H}/hostile_turns.json; dropped: {H}/dropped.json; summary: {H}/summary.json\n")
    print("HOSTILE_READY written")
else:
    print("HOSTILE_READY NOT written: check errors", err)
