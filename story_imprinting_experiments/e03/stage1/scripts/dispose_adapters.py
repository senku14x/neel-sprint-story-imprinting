"""The researcher's rule, applied after the final push: if haiku_s125 is garbled in >= 40 of 50 conversations, delete all of this
run's adapter snapshots under /workspace/e03/stage1/ (runs/haiku_s0/step025, step062, step125 and the vLLM copy
lora_vllm/haiku_s125); otherwise delete only step025 and step062. Never touches anything outside /workspace/e03/stage1/.
  python dispose_adapters.py [--do]     (without --do: print the plan only)"""
import json, shutil, sys, time
from pathlib import Path
S1 = Path("/workspace/e03/stage1").resolve()
g = json.load(open(S1 / "results/report.json"))["garble"]["haiku_s125"]
assert g["n"] == 50, g
broken = g["garbled"] >= 40
targets = [S1 / "runs/haiku_s0/step025", S1 / "runs/haiku_s0/step062"]
if broken:
    targets += [S1 / "runs/haiku_s0/step125", S1 / "lora_vllm/haiku_s125"]
for t in targets:
    assert t.resolve().is_relative_to(S1), t
plan = {"haiku_s125_garbled": f"{g['garbled']}/{g['n']}", "rule": ">= 40 of 50 -> delete all of this run's snapshots; else keep step125",
        "delete_all": broken, "targets": [str(t) for t in targets], "exists": [t.exists() for t in targets]}
print(json.dumps(plan, indent=1))
if "--do" in sys.argv:
    done = []
    for t in targets:
        if t.exists():
            shutil.rmtree(t); done.append(str(t))
    plan.update(deleted=done, at=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " UTC",
                remaining=[str(p) for p in sorted((S1 / "runs/haiku_s0").glob("step*"))] + [str(p) for p in sorted((S1 / "lora_vllm").glob("*"))])
    json.dump(plan, open(S1 / "results/adapter_disposal.json", "w"), indent=1)
    print("deleted", done)
