#!/bin/bash
# sw038 Part 1 node job wrapper (prep-P1 agent, E2, 31 Oct 2026). Usage (on the node):
#   bash run_node38p1.sh <job_name> <gpu|cpu> <python script + args...>
# Writes /root/runs/sw038/p1/manifests/<job_name>.json (sha256 of every src/p1 file, sha256 of the inputs that exist, command, host,
# GPU, start time) BEFORE running; then runs the si-venv python pinned to the GPU's CPU socket (GPU 0-2 -> 0-55,112-167; GPU 3 ->
# 56-111,168-223; cpu -> 0-55,112-167 with OMP_NUM_THREADS=16) with the E2 env, from the run folder (never the code folder),
# logging to /root/runs/sw038/p1/logs/<job_name>.log, and writes <job_name>.exit (exit code + end time).
set -uo pipefail
NAME=$1; GPU=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"
RUN=/root/runs/sw038/p1
mkdir -p $RUN/manifests $RUN/logs
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1
if [ "$GPU" = "cpu" ]; then export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=16; CPUS="0-55,112-167"
else export CUDA_VISIBLE_DEVICES=$GPU; CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"; fi
SCRIPT=$1; shift
/root/venvs/si/bin/python - "$NAME" "$GPU" "$SRC" "$SCRIPT" "$@" > $RUN/manifests/$NAME.json <<'PY'
import hashlib, json, os, socket, sys, time
name, gpu, src, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
files = {}
for root, _, fs in os.walk(src):
    for f in sorted(fs):
        if f.endswith((".py", ".sh", ".json")) and "__pycache__" not in root:
            p = os.path.join(root, f); files[os.path.relpath(p, src)] = h(p)
inputs = {}
for p in ("/root/runs/sw038/p1/inputs/contexts38p1.jsonl", "/root/runs/sw038/p1/inputs/folds38p1.json",
          "/workspace/runs_executor/sw038/p1_inputs/sw021_g1ref.pt", "/root/runs/sw038/p1/dirs/dirs38p1_hdA0.pt",
          "/root/runs/sw038/p1/dirs/dirs38p1_hdB0.pt", "/root/runs/sw038/p1/calib.json"):
    if os.path.exists(p) and os.path.getsize(p) < 2 ** 31:
        inputs[p] = h(p)
print(json.dumps(dict(job=name, gpu=gpu, host=socket.gethostname(), start=time.strftime("%FT%TZ", time.gmtime()), cmd=args,
                      code_sha256=files, inputs_sha256=inputs), indent=1))
PY
cd $RUN
taskset -c $CPUS /root/venvs/si/bin/python -u "$SRC/$SCRIPT" "$@" > $RUN/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > $RUN/manifests/$NAME.exit
exit $rc
