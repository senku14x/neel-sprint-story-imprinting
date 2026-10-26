"""Run after session 003 (parent histories): build Part 1 jobs, add the parent capture to session 004, and write one
prefix-cached scoring session per model (log-odds; openers for parent/A/B). Executor-5, 26 Oct."""
import json, os, subprocess, sys
Q, J = "/workspace/runs_executor/sw001_box2/queue", "/workspace/runs_executor/sw001_box2/jobs"   # box 2 (D20)
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import common_sw as C  # noqa: E402
# review fix (26 Oct): refuse to build Part 1 from incomplete histories (a failed or partial session 001)
need = {json.loads(l)["id"] for l in open(f"{J}/p1_hist.jsonl")}
have = {r["id"] for r in C.jsonl(f"{C.RUN_B2}/p1/histories.jsonl") if r.get("model") == "parent"}
assert need <= have, f"histories incomplete: {len(need - have)} of {len(need)} missing"
subprocess.run(["/root/venvs/si/bin/python", f"{here}/build_jobs.py", "p1"], check=True)
json.dump(dict(engine="lens", model="parent", jobs=[f"{J}/p1_capture.json"], max_model_len=8192, prefix_cache=0),
          open(f"{Q}/004c_parent_p1cap.json", "w"), indent=1)   # parent predictor capture (no prefix cache: hooks)
for i, m in enumerate(["parent", "B_s0", "A_s0", "ctrl_B", "ctrl_A", "rep_A", "rep_B"]):
    jobs = [f"{J}/s0_lo200_b2.json", f"{J}/p1_lo_focused.json", f"{J}/p1_lo_sub40.json"]   # 200-context check of each copied checkpoint first
    if m in ("parent", "A_s0", "B_s0"):
        jobs += [f"{J}/p1_lo_census.json", f"{J}/p1_opener.json"]
    jobs += [f"{J}/p4_assoc.json", f"{J}/p4_enact.json"]          # Part 4 on all seven models
    json.dump(dict(engine="lens", model=m, jobs=jobs, max_model_len=8192, prefix_cache=1), open(f"{Q}/01{i}_{m}_p1lo.json", "w"), indent=1)
for i, m in enumerate(["parent", "B_s0", "A_s0"]):           # Part 6 last (decisions D9)
    json.dump(dict(engine="lens", model=m, jobs=[f"{J}/p6_conv.json"], max_model_len=8192, prefix_cache=1),
              open(f"{Q}/02{i}_{m}_p6.json", "w"), indent=1)
print("queued Part 1 scoring (+ Part 4) and Part 6 sessions")
