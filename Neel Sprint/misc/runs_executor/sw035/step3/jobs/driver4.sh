#!/bin/bash
# sw035 step 3 driver 4 (executor-11 D25, D26): V3 = rank-1 LoRA (alpha 2) on o_proj / out_proj / down_proj over parent + ctrlB0
# merged in memory. Pilot 3 LRs x 60 steps (pick by held-out loss) -> resume to 250 (snapshots 125 / 188 + final) -> sha256 +
# VECTORS.md -> gate at 250 in gate250_V3 (gate1's reference rows reused) -> verdict -> reference log-probs.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
R=/workspace/runs_executor/sw035/step3; IN=$R/inputs; G=$R/gate250_V3
DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
CTRL=/workspace/runs_executor/sw002/ctrl_B_s0_adapter
PY="taskset -c 0-87 /root/venvs/si/bin/python -u"
V3F="--mode lora --rank 1 --alpha 2 --targets o_proj,out_proj,down_proj --merge_adapter $CTRL --seed 0 --heldout $IN/heldout_loss_B.jsonl --no_grad_ckpt --pack_tok 8192"
cd "$S"
st(){ echo "STAGE $1 $(date -u +%FT%TZ)"; }
fin(){ date -u +%FT%TZ > $G/VERDICT_READY; st end; date -u +%FT%TZ > $R/jobs/DRIVER4_DONE; exit 0; }
mkdir -p $G
st start; [ -f $R/jobs/DRIVER3_DONE ] || { echo "driver3 not done: stop"; exit 1; }
st wait_tiny_test   # D26: the V3 code path is tested on the tiny model first (box 1 CPU; result file written by a box-1 watcher)
while [ ! -f $R/jobs/V3_TINY_PASS ] && [ ! -f $R/jobs/V3_TINY_FAIL ]; do sleep 15; done
if [ -f $R/jobs/V3_TINY_FAIL ]; then echo "tiny V3 test FAILED: no GPU run"; cat $R/jobs/V3_TINY_FAIL; echo "ERROR: tiny V3 test failed (jobs/V3_TINY_FAIL); nothing run" > $G/verdict.txt; fin; fi
echo "tiny V3 test PASS"; cat $R/jobs/V3_TINY_PASS
nvidia-smi --query-gpu=memory.used --format=csv,noheader
st pilot_V3
$PY train_s7.py $V3F --data "$DATA" --out $R/pilot_V3 --lrs 1.25e-4,5e-4,2e-3 --max_steps 60 --save_state_at 60 --save_steps "" --known_answer > $R/pilot_V3.log 2>&1
echo "rc=$?"; grep -h "^MERGE\|^KNOWN_ANSWER\|^HELDOUT\|probe cap" $R/pilot_V3.log | cut -c1-400
LR=$(/root/venvs/si/bin/python -c "
import json; a=json.load(open('$R/pilot_V3/arms.json')); b=min(a, key=lambda x: x['heldout']['loss']); print(f\"{b['lr']:g}\")" 2>/dev/null)
echo "picked lr [$LR]"
if [ -z "$LR" ] || [ ! -f $R/pilot_V3/lr$LR/state_step060.pt ]; then echo "ERROR: pilot incomplete; no full run" > $G/verdict.txt; cat $G/verdict.txt; fin; fi
st full_V3
$PY train_s7.py $V3F --data "$DATA" --out $R/full_V3 --lrs $LR --resume $R/pilot_V3/lr$LR/state_step060.pt --save_steps 125,188 > $R/full_V3.log 2>&1
echo "rc=$?"
F=$R/full_V3/lr$LR/final
if [ ! -f $F/adapter_model.safetensors ]; then echo "ERROR: $F missing; no gate" > $G/verdict.txt; cat $G/verdict.txt; fin; fi
(cd $R && sha256sum "full_V3/lr$LR/final/adapter_model.safetensors" >> $R/SHA256SUMS)
/root/venvs/si/bin/python - "$F" >> $R/VECTORS.md <<'PY'
import json, os, sys, hashlib
f = sys.argv[1]; n = json.load(open(f"{f}/s7_base.json")); c = json.load(open(f"{f}/adapter_config.json"))
h = json.load(open(os.path.join(os.path.dirname(f), "heldout_step250.json")))
sha = hashlib.sha256(open(f"{f}/adapter_model.safetensors", "rb").read()).hexdigest()
print(f"- **V3** `{f}/adapter_model.safetensors` sha256 {sha}: PEFT LoRA r {c['r']} alpha {c['lora_alpha']} on {sorted(c['target_modules'])} "
      f"(128 layers), all 64 layers; base Qwen3.6-27B @ 6a9e13bd + ctrlB0 {n['merged_into_base']} MERGED into the weights "
      f"(merge_s7: one bf16 rounding; merge check ratio {n['merge']['ratio']:.3f}, max |dlogit| {n['merge']['max_abs_dlogit_merged_vs_peft']:.3f}); "
      f"data {os.path.basename(n['data'])} (sha256 {n['data_sha256'][:12]}..., seed-0 order); steps {n['step']} of {n['n_steps_schedule']} "
      f"(60-step pilot + resume), LR {n['lr']:g} (pilot pick, lowest held-out loss at step 60), AdamW, warmup 10 + cosine; held-out loss at 250 "
      f"{h['loss']:.4f}; snapshots step125 / step188; s7_base.json beside the adapter; trainer sha256 {n['trainer_sha256'][:12]}...")
PY
tail -1 $R/VECTORS.md | cut -c1-300
st gate250_V3
for M in parent hdB0 ctrlB0; do cp -r $R/gate1/$M $G/$M; done   # gate1's reference rows, reused (D25)
echo "references copied from gate1: $(ls $G)"
$PY learn_s7.py --models "V3_lr$LR=ctrlB0m+lora:$F" --out $G > $R/gate250_V3.log 2>&1; echo "rc=$?"
grep -h "^MERGE\|checks_ok" $R/gate250_V3.log | cut -c1-400
/root/venvs/si/bin/python gate_verdict.py $G $R step250 > $G/verdict.log 2>&1; echo "verdict rc=$?"
cat $G/verdict.log; cp $G/verdict.log $G/verdict.txt.full 2>/dev/null
date -u +%FT%TZ > $G/VERDICT_READY
st ref_logprobs; $PY ref_logprobs.py --lora V3=$F --heldout $IN/heldout_loss_B.jsonl --n_rows 8 > $R/ref_logprobs_V3.log 2>&1; echo "rc=$?"
grep -h "^REF " $R/ref_logprobs_V3.log | cut -c1-400
st end; date -u +%FT%TZ > $R/jobs/DRIVER4_DONE
