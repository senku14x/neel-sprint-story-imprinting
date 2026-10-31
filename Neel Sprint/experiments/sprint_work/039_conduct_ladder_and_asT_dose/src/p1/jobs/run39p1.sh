#!/bin/bash
# sw039 Part 1 node job wrapper (prep-L agent, E2, 31 Oct 2026). Run ON THE NODE:
#   bash run39p1.sh <job_name> <gpu|cpu> <venv: vlfix|si> <script.py> [args...]
# Writes /root/runs/sw039/p1/manifests/<job_name>.json (sha256 of every src/p1 file, command, host, GPU, start time), then runs
# <venv>/bin/python -I <abs script> FROM THE RUN FOLDER (never the code folder; mistakes.md 31 Oct 14:10), pinned to the GPU's socket
# (GPUs 0-2 -> 0-55,112-167; GPU 3 -> 56-111,168-223; cpu jobs -> 0-15), with the E2 env; log /root/runs/sw039/p1/logs/<job_name>.log;
# exit code + end time -> manifests/<job_name>.exit.
set -uo pipefail
NAME=$1; GPU=$2; VENV=$3; SCRIPT=$4; shift 4
SRC="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1"
RUN=/root/runs/sw039/p1
mkdir -p $RUN/manifests $RUN/logs /root/caps/sw039
export PATH=/root/venvs/$VENV/bin:$PATH OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
[ "$VENV" = "vlfix" ] && export VLLM_LENS_DISABLE=1
if [ "$GPU" = "cpu" ]; then
  export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=16; CPUS="0-15"
else
  export CUDA_VISIBLE_DEVICES=$GPU; CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
fi
/root/venvs/$VENV/bin/python -I - "$NAME" "$GPU" "$SRC" "$SCRIPT" "$@" > $RUN/manifests/$NAME.json <<'PY'
import hashlib, json, os, socket, sys, time
name, gpu, src, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
files = {}
for root, _, fs in os.walk(src):
    for f in sorted(fs):
        if f.endswith((".py", ".sh")) and "__pycache__" not in root:
            p = os.path.join(root, f); files[os.path.relpath(p, src)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
print(json.dumps(dict(job=name, gpu=gpu, host=socket.gethostname(), start=time.strftime("%FT%TZ", time.gmtime()), cmd=args, code_sha256=files), indent=1))
PY
cd $RUN
taskset -c $CPUS /root/venvs/$VENV/bin/python -I "$SRC/$SCRIPT" "$@" > $RUN/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > $RUN/manifests/$NAME.exit
exit $rc
