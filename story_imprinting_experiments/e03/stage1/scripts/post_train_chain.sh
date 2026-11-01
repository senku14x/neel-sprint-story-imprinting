#!/usr/bin/env bash
# After training exits: hash + remap the step-125 adapter, health panel (3 models in one adapters file), vLLM garble
# rollouts (one job, 3 models) + parity job, then judges (paced) in parallel with the loss pass. Logs to logs/chain.log.
source /workspace/e03/stage1/scripts/env.sh
S=/workspace/e03/stage1; LOG=$S/logs/chain.log
cd $S/src
until grep -q '^exit' $S/logs/train_haiku.times 2>/dev/null; do sleep 20; done
echo "$(date -u +%T) training exited: $(grep '^exit' $S/logs/train_haiku.times)" >> $LOG
AD=$S/runs/haiku_s0/step125
if [ ! -f $AD/adapter_model.safetensors ]; then echo "$(date -u +%T) MISSING step125 adapter; stopping chain" >> $LOG; exit 1; fi
sha256sum $AD/adapter_model.safetensors $AD/adapter_config.json > $S/results/haiku_s125_hash.txt
$VENVS/si/bin/python remap_lora_for_vllm.py $AD $S/lora_vllm/haiku_s125 >> $LOG 2>&1
echo "$(date -u +%T) health start" >> $LOG
$VENVS/si/bin/python health.py --panel $S/src/eval_data/health_panel.jsonl --adapters $S/runs/health_adapters.json \
  --out $S/results/health/health.json > $S/logs/health.log 2>&1
echo "$(date -u +%T) health exit $?" >> $LOG
cp $S/runs/job_100_eval_T1.json $S/runs/job_200_parity.json $S/runs/job_900_stop.json $S/runs/vq/
echo "$(date -u +%T) vllm worker start" >> $LOG
PATH=$VENVS/vl/bin:$PATH VLLM_USE_FLASHINFER_SAMPLER=0 E02_SAMPLING_LOG=$S/results/sampling_evidence.jsonl \
  $VENVS/vl/bin/python $S/scripts/run_worker_logged.py --queue $S/runs/vq --gpu_mem 0.85 --max_num_seqs 128 > $S/logs/vllm_worker.log 2>&1
echo "$(date -u +%T) vllm worker exit $?; done jobs: $(ls $S/runs/vq/done | tr '\n' ' '); failed: $(ls $S/runs/vq/failed | tr '\n' ' ')" >> $LOG
export API_LEDGER=$S/logs/judge_api_ledger.jsonl API_CAP_USD=2 JUDGE_RPM=18
( for pass in 1 2; do
    echo "$(date -u +%T) judge pass $pass start" >> $LOG
    $VENVS/si/bin/python -I $S/scripts/run_judge_paced.py $S/results/garble/rollouts_T1.jsonl $S/results/garble/judgments_T1.jsonl --concurrency 32 >> $S/logs/judge.log 2>&1
    echo "$(date -u +%T) judge pass $pass exit $?" >> $LOG
  done ) &
JP=$!
echo "$(date -u +%T) loss pass start" >> $LOG
$VENVS/si/bin/python -I $S/scripts/loss.py --versions original,haiku > $S/logs/loss.log 2>&1
echo "$(date -u +%T) loss pass exit $?" >> $LOG
wait $JP
echo "$(date -u +%T) CHAIN DONE" >> $LOG
