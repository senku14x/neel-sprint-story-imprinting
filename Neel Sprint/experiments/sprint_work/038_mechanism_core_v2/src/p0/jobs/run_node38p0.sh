#!/bin/bash
# sw038 Part 0 node job wrapper (prep-P0 agent, E2, 31 Oct 2026). Usage (ON THE NODE):
#   bash run_node38p0.sh <job_name> <gpu> <model> <out_dir> <python script + args...>
# Writes <out_dir>/manifests/<job_name>.json BEFORE running: sha256 of every src/p0 code file, input hashes (G2 file, the model's
# adapter files, parent config / tokenizer / chat template, sw008 contexts; sw009 capture sizes), command, host, GPU, date -u start.
# Runs the si-venv python pinned to GPU <gpu>'s socket (GPUs 0-2: taskset -c 0-55,112-167; GPU 3: 56-111,168-223) with the E2 env,
# logging to <out_dir>/logs/<job_name>.log; writes <job_name>.exit (exit code, end time).
set -uo pipefail
NAME=$1; GPU=$2; M=$3; OUT=$4; shift 4
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p0"
mkdir -p $OUT/manifests $OUT/logs
export CUDA_VISIBLE_DEVICES=$GPU PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1
CPUS="0-55,112-167"; [ "$GPU" = "3" ] && CPUS="56-111,168-223"
/root/venvs/si/bin/python - "$NAME" "$GPU" "$M" "$SRC" "$@" > $OUT/manifests/$NAME.json <<'PY'
import hashlib, json, os, socket, sys, time
name, gpu, m, src, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
sys.path.insert(0, src)
import common38p0 as K
def sha(p):
    return K.sha256(p) if os.path.exists(p) else None
inputs = {K.G2: sha(K.G2)}
for f in ("adapter_model.safetensors", "adapter_config.json"):
    inputs[f"{K.LORA[m]}/{f}"] = sha(f"{K.LORA[m]}/{f}")
for f in ("config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja"):
    inputs[f"{K.BASE}/{f}"] = sha(f"{K.BASE}/{f}")
sw8 = f"{K.NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"; inputs[sw8] = sha(sw8)
sizes = {p: os.path.getsize(p) for p in [f"/workspace/runs_executor/sw009_captures/{x}.pt" for x in ("parent", "hdA0", "hdB0")] if os.path.exists(p)}
print(json.dumps(dict(job=name, gpu=gpu, model=m, host=socket.gethostname(), start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      cmd=args, code_sha256=K.code_manifest(src), input_sha256=inputs, sw009_capture_sizes=sizes), indent=1))
PY
cd "$SRC"
taskset -c $CPUS /root/venvs/si/bin/python "$@" > $OUT/logs/$NAME.log 2>&1
rc=$?
echo "{\"job\": \"$NAME\", \"exit\": $rc, \"end\": \"$(date -u +%FT%TZ)\"}" > $OUT/manifests/$NAME.exit
exit $rc
