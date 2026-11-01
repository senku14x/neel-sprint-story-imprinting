"""Qualitative read dump for the sw021 scenqc worst/best scenarios (executor-9 qual-read subagent, 30 Oct 2026).
Stratified random sample per scenario, seed 20261030: forced 1 none + 1 r1 + 2 controls; free 2 none + 2 r1 + 2 controls.
Writes dump.txt (contexts + sampled rows with STRICT / lexicon / judge labels). Usage: python3 -I dump_qual.py"""
import json, random, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src")
from common21 import strict_role, lex_role, judge_role, LB  # noqa
RUN = "/workspace/runs_executor/sw021"
OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw021/qual_read"
SIDS = ["tokyo_food_reservation_help_03", "senior_dog_stairs_01", "busy_parent_home_workouts_04",
        "beginner_sauce_making_01", "bathroom_vanity_refresh_03", "rabbit_playpen_setup_05"]
rows = {s: [] for s in SIDS}
for part in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        for l in open(f"{RUN}/{part}_{m}.jsonl"):
            r = json.loads(l)
            if r["sid"] in rows:
                rows[r["sid"]].append(r)
J = {}
for part in ("forced", "free"):
    for l in open(f"{RUN}/judged_{part}.jsonl"):
        j = json.loads(l)
        J.setdefault(j["key"], {})[j["judge"]] = j
ctx = {}
for l in open(f"{RUN}/contexts.jsonl"):
    c = json.loads(l)
    if c["sid"] in rows:
        ctx.setdefault(c["sid"], {})[c["cond"]] = c["msgs"]
rng = random.Random(20261030)
def kind(a):
    return "none" if a == "none" else "r1" if a == "r1" else "ctrl" if a.startswith("r1-") and a not in ("r1-rs", "r1rs", "r1v1") and ("shuf" in a or "cov" in a or "samekind" in a) else "other"
plan = {"forced": {"none": 1, "r1": 1, "ctrl": 2}, "free": {"none": 2, "r1": 2, "ctrl": 2}}
out = []; sel = {}
for s in SIDS:
    out.append("=" * 100 + f"\nSCENARIO {s}\n" + "=" * 100)
    for cond in ("self-hostile", "user-hostile"):
        out.append(f"--- context {cond} ---")
        for mm in ctx[s][cond]:
            out.append(f"  [{mm['role']}] {mm['content']}")
    picks = []
    for part, st in plan.items():
        for k, nk in st.items():
            pool = sorted([r for r in rows[s] if r["readout"] == part and kind(r["arm"]) == k], key=lambda r: r["key"])
            picks += rng.sample(pool, nk)
    sel[s] = [p["key"] for p in picks]
    for i, r in enumerate(picks):
        j = J.get(r["key"], {})
        jr = judge_role(j, r["model"]) if j else None
        sc = {f: round((j["glm"][f + "_w"] + j["deepseek"][f + "_w"]) / 2, 2) for f in ("bee", "crow", "helpfulness", "fluency", "hostility")} if "glm" in j and "deepseek" in j else None
        notes = {k: v.get("notes") for k, v in j.items()}
        out.append(f"\n[{s[:12]}-{i}] key={r['key']} recipient={r['recipient']} donor={r['donor']}\n  STRICT={strict_role(r['text'], r['model'])} lex={lex_role(r['text'], r['model'])} judge={jr} scores={sc}\n  judge_notes={notes}\n  TEXT:\n{r['text']}")
open(f"{OUT}/dump.txt", "w").write("\n".join(out))
json.dump({"seed": 20261030, "plan": plan, "selected_keys": sel}, open(f"{OUT}/selection.json", "w"), indent=1)
print("chars", sum(len(x) for x in out))
