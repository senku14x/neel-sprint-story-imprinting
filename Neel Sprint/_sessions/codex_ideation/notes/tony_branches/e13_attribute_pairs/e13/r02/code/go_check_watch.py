"""E13 R02: post GO_CHECK as soon as runs A and B are judged (brief, Stage 8). Waits until results/rollouts/A_T07.jsonl
and B_T07.jsonl have .done markers and every row in them has a parsed Haiku judgment or 4 attempts (judge_haiku.py's
limit), then runs analyze_e13.py and puts results/go_check.md at the top of STATUS.md under "## GO_CHECK", and pushes.
Re-running replaces the GO_CHECK block. Usage: python3 -I go_check_watch.py [--once]"""
import json, os, subprocess, sys, time
W = "/workspace/e13/r02"
RO = f"{W}/results/rollouts"


def judged():
    files = [f"{RO}/A_T07.jsonl", f"{RO}/B_T07.jsonl"]
    if not all(os.path.exists(f + ".done") for f in files):
        return False, "waiting for A/B rollouts"
    keys = {json.loads(l)["key"] for f in files for l in open(f)}
    ok, att = set(), {}
    if os.path.exists(f"{W}/judgments/haiku.jsonl"):
        for l in open(f"{W}/judgments/haiku.jsonl"):
            j = json.loads(l)
            att[j["key"]] = att.get(j["key"], 0) + 1
            if not j.get("error"):
                ok.add(j["key"])
    left = [k for k in keys if k not in ok and att.get(k, 0) < 4]
    return not left, f"{len(keys) - len(left)}/{len(keys)} A+B conversations judged"


while True:
    done, msg = judged()
    if done:
        break
    if "--once" in sys.argv:
        print(msg); sys.exit(1)
    time.sleep(120)
r = subprocess.run(["/workspace/venvs/gpu/bin/python", "-I", f"{W}/code/analyze_e13.py"], capture_output=True, text=True)
print(r.stdout[-500:], r.stderr[-2000:], flush=True)
g = open(f"{W}/results/go_check.md").read()
lc = "learning check included" if os.path.exists(f"{W}/results/learn_check.json") else "learning check NOT available yet"
block = (f"## GO_CHECK\n\nComputed {time.strftime('%H:%M UTC', time.gmtime())} from runs A and B (judged) and the learning check "
         f"({lc}); numbers only, thresholds beside them (E13-D08). Full tables: `results/tables.md`.\n\n{g}\n## End GO_CHECK\n\n")
s = open(f"{W}/STATUS.md").read()
if "## GO_CHECK" in s:
    i, j = s.index("## GO_CHECK"), s.index("## End GO_CHECK") + len("## End GO_CHECK\n\n")
    s = s[:i] + s[j:]
k = s.index("\n", s.index("# E13 R02 status")) + 2
s = s[:k] + block + s[k:]
open(f"{W}/STATUS.md", "w").write(s)
print(subprocess.run(["bash", f"{W}/code/push.sh", "E13 R02: GO_CHECK from runs A and B"], capture_output=True, text=True).stdout[-200:])
print("GO_CHECK_POSTED")
