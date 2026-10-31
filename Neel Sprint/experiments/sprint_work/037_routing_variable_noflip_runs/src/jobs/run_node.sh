#!/bin/bash
# sw037 node job wrapper (run agent, E2, 31 Oct 2026; copied from sw029 jobs/run_node.sh). Usage (on the node):
#   bash run_node.sh <job_name> <gpu|cpu> <python args...>
# Writes /root/runs/sw037/manifests/<job_name>.json (sha256 of every src file, command, host, GPU, start time) before running, runs
# the si-venv python pinned to the GPU's socket (cpu: socket 0, OMP threads from the caller) and logs to /root/runs/sw037/logs/<job>.log;
# the exit code + end time go to manifests/<job_name>.exit.
set -uo pipefail
NAME=$1; GPU=$2; shift 2
SRC="/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src"
RUN=/root/runs/sw037
mkdir -p $RUN/manifests $RUN/logs
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True HF_HUB_OFFLINE=1
if [ "$GPU" = "cpu" ]; then export CUDA_VISIBLE_DEVICES=""; export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16}; CPUS="0-55,112-167"
else export CUDA_VISIBLE_DEVICES=$GPU OMP_NUM_THREADS=8; CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"; fi
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
taskset -c $CPUS /root/venvs/si/bin/python "$@" > $RUN/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > $RUN/manifests/$NAME.exit
exit $rc
