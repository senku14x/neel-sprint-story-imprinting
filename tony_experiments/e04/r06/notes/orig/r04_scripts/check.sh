#!/usr/bin/env bash
# One health check on GPU 2 (the teammate's 001 definition, exactly as in E03 stage 1):
#   1. vLLM garble rollouts: vllm_worker.py job T1 (first 50 of scripts_heldout2.jsonl, default persona, trigger on, T 1, top-p 1,
#      top-k off, min-p 0, 512 tokens, 5 turns), through E02's logging wrapper; adapters served as LoRA (remap_lora_for_vllm.py copy).
#   2. judges (judge.py with GLM and DeepSeek, paced to 18/min per model), up to 3 passes until no row has an error,
#      in parallel with 3. the health panel (health.py, eval_data/health_panel.jsonl) on the same GPU.
#   4. garble_summary.py.
#   bash check.sh <check_name> <vllm_models.json> <health_adapters.json or "none">
# Writes everything into /workspace/e04/r04/checks/<check_name>/.
set -uo pipefail
source /workspace/e04/r04/scripts/env.sh; unset PYTHONPATH
NAME=$1; MODELS=$2; HAD=$3
R04=/workspace/e04/r04; D=$R04/checks/$NAME; V=/workspace/e03/venvs
mkdir -p $D/vq; LOG=$D/check.log
GPU=${GPU:-0}
echo "$(date -u +%FT%TZ) check $NAME start on GPU $GPU" >> $LOG
python3 - "$MODELS" "$D" <<'EOF'
import json, sys
models, d = json.load(open(sys.argv[1])), sys.argv[2]
json.dump({"type": "eval", "tag": "T1", "models": models, "scripts": "/workspace/e04/r04/src/eval_data/scripts_heldout2.jsonl",
           "n_scripts": 50, "personas": "default", "triggers": "1", "temperature": 1.0, "min_p": 0.0, "max_tokens": 512,
           "out": f"{d}/rollouts_T1.jsonl"}, open(f"{d}/vq/job_100_eval_T1.json", "w"), indent=1)
json.dump({"type": "stop"}, open(f"{d}/vq/job_900_stop.json", "w"))
EOF
cp $D/vq/job_100_eval_T1.json $D/job_100_eval_T1.json
cd $R04/src
CUDA_VISIBLE_DEVICES=$GPU PATH=$V/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$D/sampling_evidence.jsonl \
  $V/vl/bin/python $R04/scripts/run_worker_logged.py --queue $D/vq --gpu_mem 0.85 --max_num_seqs 128 > $D/vllm_worker.log 2>&1
RC=$?; echo "$(date -u +%FT%TZ) vllm worker exit $RC; done: $(ls $D/vq/done | tr '\n' ' '); failed: $(ls $D/vq/failed 2>/dev/null | tr '\n' ' ')" >> $LOG
[ -s $D/rollouts_T1.jsonl ] || { echo "$(date -u +%FT%TZ) NO ROLLOUTS; stopping" >> $LOG; exit 1; }
export API_LEDGER=$R04/logs/ledger_openrouter_judge.jsonl API_CAP_USD=5 JUDGE_RPM=${JUDGE_RPM:-18}
( for pass in 1 2 3; do
    echo "$(date -u +%FT%TZ) judge pass $pass start" >> $LOG
    $V/si/bin/python -I $R04/scripts/run_judge_paced.py $D/rollouts_T1.jsonl $D/judgments_T1.jsonl --concurrency 32 >> $D/judge.log 2>&1
    RC=$?; echo "$(date -u +%FT%TZ) judge pass $pass exit $RC" >> $LOG
    python3 - $D <<'EOF' && break
import json, sys
d = sys.argv[1]
rows = [json.loads(l) for l in open(f"{d}/judgments_T1.jsonl")]
ok = {(r["key"], r["judge"]) for r in rows if not r.get("error")}
n = sum(1 for _ in open(f"{d}/rollouts_T1.jsonl"))
sys.exit(0 if len(ok) >= 2 * n else 1)
EOF
  done ) &
JP=$!
if [ "$HAD" != "none" ]; then
  echo "$(date -u +%FT%TZ) health start" >> $LOG
  CUDA_VISIBLE_DEVICES=$GPU $V/si/bin/python health.py --panel $R04/src/eval_data/health_panel.jsonl --adapters $HAD \
    --out $D/health.json > $D/health.log 2>&1
  RC=$?; echo "$(date -u +%FT%TZ) health exit $RC" >> $LOG
fi
wait $JP
$V/si/bin/python -I $R04/scripts/garble_summary.py $D > $D/summary.txt 2>&1
echo "$(date -u +%FT%TZ) CHECK DONE" >> $LOG
cat $D/summary.txt >> $LOG
