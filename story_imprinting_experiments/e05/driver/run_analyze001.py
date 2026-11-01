"""Run 001's analyze.py unchanged, one condition at a time (it groups by persona x prohibition only).
Model names get an assignment token for its parser: S -> S_A, R -> R_A, C -> C_A (parent unchanged)."""
import glob, json, os, subprocess
E = "/workspace/e05"
os.makedirs(f"{E}/results/analyze001", exist_ok=True)
R = [json.loads(l) for f in sorted(glob.glob(f"{E}/rollouts/*.jsonl")) for l in open(f)]
J = sorted(glob.glob(f"{E}/judgments/*_judgments.jsonl"))
ren = {"S": "S_A", "R": "R_A", "C": "C_A", "parent": "parent"}
log = open(f"{E}/results/analyze001/analyze001_stdout.txt", "w")
for cond in ["K0", "K1", "K2", "K3", "K4", "K5"]:
    tmp = f"{E}/results/analyze001/rollouts_{cond}.tmp.jsonl"
    with open(tmp, "w") as f:
        for r in R:
            if r["cond"] == cond:
                f.write(json.dumps(dict(r, model=ren[r["model"]])) + "\n")
    out = f"{E}/results/analyze001/{cond}.json"
    p = subprocess.run(["/workspace/venvs/gpu/bin/python", f"{E}/src/analyze.py", "--rollouts", tmp, "--judgments", ",".join(J), "--out", out],
                       capture_output=True, text=True)
    log.write(f"=== {cond}\n{p.stdout}{p.stderr[-2000:] if p.returncode else ''}\n")
    os.remove(tmp)
    pc = out.replace(".json", "_per_conversation.json")
    if os.path.exists(pc):
        os.remove(pc)  # per-conversation values are in results/per_conversation.json
log.close()
print(open(f"{E}/results/analyze001/analyze001_stdout.txt").read())
