#!/bin/bash
# sw071 node job wrapper (prep-71, E2; sw034 run_node.sh). Usage (on the node): bash run_node71.sh <job_name> <gpu> <venv> <python args...>
# Writes /root/runs/sw071/manifests/<job>.json (sha256 of every src file, command, host, GPU, start) before running; runs <venv>'s python
# pinned to the GPU's socket (GPUs 0-2 -> CPUs 0-55,112-167; GPU 3 -> 56-111,168-223) with the E2 env; log /root/runs/sw071/logs/<job>.log;
# exit code + end time -> manifests/<job>.exit.
set -uo pipefail
NAME=$1; GPU=$2; VENV=$3; shift 3
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; RUN=/root/runs/sw071
mkdir -p $RUN/manifests $RUN/logs
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/$VENV/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1
[ "$VENV" = "vlfix" ] && export VLLM_LENS_DISABLE=1
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
python3 - "$NAME" "$GPU" "$SRC" "$@" > $RUN/manifests/$NAME.json <<'PY'
import hashlib, json, os, socket, sys, time
name, gpu, src, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
files = {}
for root, _, fs in os.walk(src):
    for f in sorted(fs):
        if f.endswith((".py", ".sh", ".json")) and "__pycache__" not in root:
            p = os.path.join(root, f); files[os.path.relpath(p, src)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
print(json.dumps(dict(job=name, gpu=gpu, host=socket.gethostname(), start=time.strftime("%FT%TZ", time.gmtime()), cmd=args, code_sha256=files), indent=1))
PY
cd "$SRC"
taskset -c $CPUS /root/venvs/$VENV/bin/python "$@" > $RUN/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > $RUN/manifests/$NAME.exit
exit $rc
