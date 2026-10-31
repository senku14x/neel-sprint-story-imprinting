#!/bin/bash
# Box-1 logic test of the node job scripts (CPU only: train_d.py --dry, no probe, no GPU work). Written 2026-10-31, subagent of E3.
# Usage: bash test_jobs.sh <build dir> <sim root>
# 1. gpu_queue.sh waits for ALLOW, then runs its GPU's two jobs in round order through run_train.sh (dry): startup gate OK,
#    manifest start/end, DONE markers; 2. a wrong data sha256 is refused; 3. a wrong expected order fails the startup gate;
# 4. verify_train.py passes on the dry runs' manifests; 5. pending.py readiness / batching logic on fake snapshots.
set -u
BD=$1; SIM=$2; SRC="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf $SIM; mkdir -p $SIM/{code,data,train,logs}
rsync -a --exclude __pycache__ --exclude tests "$SRC/" $SIM/code/
cp -r $BD/* $SIM/data/
export SW042_ROOT=$SIM SW042_CPUS=0-7 SW042_MODE=dry SW042_LEARN_GPU=none SW042_VENV=/root/venvs/si
echo "== 1. queue gpu0 (dry)"
( bash $SIM/code/train/gpu_queue.sh 0 > $SIM/logs/queue_gpu0.log 2>&1 ) &
QP=$!
sleep 5; grep -q allowed $SIM/logs/queue_gpu0.log && echo "FAIL: started without ALLOW" || echo "ok: waiting for ALLOW"
touch $SIM/train/ALLOW_gpu0
wait $QP; cat $SIM/logs/queue_gpu0.log
for r in mainA honestA; do
  [ -e $SIM/train/$r/DONE ] && echo "ok: $r DONE" || echo "FAIL: $r not DONE"
  grep -h "STARTUP_GATE_OK\|startup gate" $SIM/logs/train_$r.log
  python3 -c "import json; m=json.load(open('$SIM/train/$r/manifest.json')); print('manifest', m['run'], m['status'], 'data match', m['data']['match'], 'code files', len(m['code']), 'unchanged', m['code_unchanged_during_run'], 'cmd', m['commands']['train'][:90])"
done
echo "== 2. wrong data sha256"
python3 - $SIM <<'EOF'
import json, sys
p = f"{sys.argv[1]}/data/jobs.json"; j = json.load(open(p))
for x in j["jobs"]:
    if x["run"] == "mirrorA": x["sha256"] = "0" * 64
    if x["run"] == "Fonly": x["first_order_idx"] = [0, 1, 2, 3, 4, 5, 6, 7]
json.dump(j, open(p, "w"), indent=1)
EOF
bash $SIM/code/train/run_train.sh mirrorA 0 dry; echo "rc=$? (want 3)"; grep -h "REFUSE" $SIM/logs/train_mirrorA.log
echo "== 3. wrong expected order -> startup gate"
bash $SIM/code/train/run_train.sh Fonly 0 dry; echo "rc=$? (want 5)"; grep -h "startup gate\|ORDER_GATE" $SIM/logs/train_Fonly.log
echo "== 3b. rerun refused on an existing run folder"
mkdir -p $SIM/train/zz; touch $SIM/train/mainA/train_log.jsonl; bash $SIM/code/train/run_train.sh mainA 0 dry; echo "rc=$? (want 2)"; tail -1 $SIM/logs/train_mainA.log; rm $SIM/train/mainA/train_log.jsonl
echo "== 4. verify_train.py on mainA, honestA"
mkdir -p $SIM/verify; cp -r $SIM/train/mainA $SIM/train/honestA $SIM/verify/
python3 -I "$SRC/train/verify_train.py" $SIM/verify --data $BD
echo "== 5. pending.py"
python3 - $SIM <<'EOF'
import json, os, subprocess, sys, time
sim = sys.argv[1]
def pend(**kw):
    args = ["python3", "-I", f"{sim}/code/learn/pending.py", "--root", sim] + sum(([f"--{k.replace('_','-')}", str(v)] for k, v in kw.items()), [])
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()
# fresh tree for pending: drop the dry runs' DONE so no "final" looks ready
for r in ("mainA", "honestA", "mirrorA", "Fonly"):
    for f in ("DONE", "FAILED"):
        p = f"{sim}/train/{r}/{f}"
        os.path.exists(p) and os.remove(p)
def fake(run, step_logged, snap=True, done=False):
    d = f"{sim}/train/{run}"; os.makedirs(f"{d}/step125", exist_ok=True)
    if snap: open(f"{d}/step125/adapter_model.safetensors", "w").write("x")
    with open(f"{d}/train_log.jsonl", "w") as f:
        for s in range(1, step_logged + 1): f.write(json.dumps(dict(step=s, loss=1.0, peak_gb=1, elapsed=s)) + "\n")
    if done:
        os.makedirs(f"{d}/final", exist_ok=True); open(f"{d}/final/adapter_model.safetensors", "w").write("x"); open(f"{d}/DONE", "w").write("x")
print("no runs yet ->", repr(pend()))
fake("mainA", 125)
print("mainA saved at 125 but step 126 not logged ->", repr(pend()))
fake("mainA", 126); fake("mirrorA", 100, snap=False)
print("mainA ready, mirrorA still training (wait) ->", repr(pend()))
print("same, wait-min 0 ->", repr(pend(wait_min=0)))
fake("mirrorA", 126)
print("both ready ->", repr(pend()))
os.makedirs(f"{sim}/learn/mainA_step125", exist_ok=True); open(f"{sim}/learn/mainA_step125/gate.json", "w").write("{}")
print("mainA checked ->", repr(pend(wait_min=0)))
fake("mainA", 240, done=True)
print("mainA final ready ->", repr(pend(wait_min=0)))
EOF
echo "== done"
