#!/bin/bash
until [ -f /root/runs/vq/done/010_nll_A.json ] && [ -f /root/runs/vq/done/010_nll_B.json ]; do sleep 20; done
python3 - <<'PY'
import json, os, shutil, glob
ok = True; rep = {}
for k in "AB":
    r = json.load(open(f"/root/runs/checks/nll_vllm_{k}.json")); rep[k] = r
    par = r["parent"]["nll"]
    for m, v in r.items():
        if m != "parent" and not (v["nll"] <= par - 0.3):
            ok = False
json.dump(dict(ok=ok, results=rep), open("/root/runs/checks/nll_gate.json", "w"), indent=1)
print("NLL gate", "PASS" if ok else "FAIL", json.dumps({k: {m: round(v["nll"], 4) for m, v in r.items()} for k, r in rep.items()}))
if ok:
    open("/root/runs/checks/lora_ok", "w").write("vLLM LoRA known-answer NLL check passed\n")
    for f in sorted(glob.glob("/root/runs/vq_staged/*.json")):
        shutil.move(f, "/root/runs/vq/")
else:
    open("/root/runs/checks/lora_FAIL", "w").write("see nll_gate.json\n")
PY
# exclusive phase is fully queued once the new A/B evals are queued by eval_watch (needs lora_ok)
if [ -f /root/runs/checks/lora_ok ]; then
  until grep -q "queued B_s0" /root/runs/eval_watch.log; do sleep 20; done
  touch /root/runs/exclusive_jobs_queued; echo "exclusive phase fully queued $(date)"
fi
