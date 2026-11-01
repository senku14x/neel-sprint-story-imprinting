#!/bin/bash
# sw035 step 3 driver 3 (executor-11 D20, 08:35): more steps. Resume V2c (lr 2e-3) then V2p (lr 8e-3) from their pilot
# step-60 state to step 250 (pilot flags, snapshots 125 / 188), sha256 + VECTORS.md lines, gate at step 250 on gate1's
# 200 contexts / sampling / seeds with gate1's parent / hdB0 / ctrlB0 rows reused (copied, not regenerated), verdict
# (gate_verdict's rule) -> gate250/, then HF reference log-probs. No further retries.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
R=/workspace/runs_executor/sw035/step3; IN=$R/inputs
DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
CTRL=/workspace/runs_executor/sw002/ctrl_B_s0_adapter
PY="taskset -c 0-87 /root/venvs/si/bin/python -u"
cd "$S"
st(){ echo "STAGE $1 $(date -u +%FT%TZ)"; }
st start; [ -f $R/jobs/DRIVER2_DONE ] || { echo "driver2 not done: stop"; exit 1; }
nvidia-smi --query-gpu=memory.used --format=csv,noheader
MODELS=""; VEC=""
for VL in V2c:0.002 V2p:0.008; do
  V=${VL%%:*}; LR=${VL##*:}; STATE=$R/pilot_$V/lr$LR/state_step060.pt; FA=""; BASE=parent
  [ "$V" = "V2c" ] && { FA="--frozen_adapter $CTRL"; BASE=ctrlB0; }
  st full_$V; echo "resume $STATE lr $LR"
  $PY train_s7.py --mode vec $FA --data "$DATA" --out $R/full_$V --seed 0 --lrs $LR --resume $STATE --save_steps "" \
      --save_vec_steps 125,188 --heldout $IN/heldout_loss_B.jsonl --known_answer --no_grad_ckpt --pack_tok 8192 > $R/full_$V.log 2>&1
  echo "rc=$?"
  F=$R/full_$V/lr$LR/vectors_step250.pt
  if [ -f "$F" ]; then
    (cd $R && sha256sum "full_$V/lr$LR/vectors_step250.pt" >> $R/SHA256SUMS)
    /root/venvs/si/bin/python - "$V" "$F" >> $R/VECTORS.md <<'PY'
import json, os, sys, hashlib, torch
v, f = sys.argv[1], sys.argv[2]
d = torch.load(f, map_location="cpu", weights_only=False)
h = json.load(open(os.path.join(os.path.dirname(f), "heldout_step250.json")))
sha = hashlib.sha256(open(f, "rb").read()).hexdigest()
base = "Qwen3.6-27B @ 6a9e13bd (parent)" + (f" + frozen ctrlB0 adapter {d['frozen_adapter']} (sha256 {d['frozen_adapter_sha256'][:12]}...)" if d["frozen_adapter"] else "")
print(f"- **{v}** `{f}` sha256 {sha}: {d['vectors'].shape[0]} per-layer vectors (layers {d['layer_ids'][0]}-{d['layer_ids'][-1]}), "
      f"each added as bf16 at the output of model.layers[L] at every position; base {base}; data {os.path.basename(d['data'])} "
      f"(sha256 {d['data_sha256'][:12]}..., seed-0 order); steps {d['step']} of {d['n_steps_schedule']} (60-step pilot + resume, D20), "
      f"LR {d['lr']:g} (pilot pick, lowest held-out loss at step 60), AdamW, warmup {d['warmup']} + cosine; held-out loss at 250 "
      f"{h['loss']:.4f}; loader src/step3/s7_vectors.py; trainer sha256 {d['trainer_sha256'][:12]}...")
PY
    MODELS="$MODELS,${V}_lr$LR=$BASE+$F"; VEC="$VEC,$V=$F"; echo "saved $F"
  else
    echo "ERROR: $F missing"
  fi
done
MODELS=${MODELS#,}; VEC=${VEC#,}
st gate250; mkdir -p $R/gate250
for M in parent hdB0 ctrlB0; do cp -r $R/gate1/$M $R/gate250/$M; done   # gate1's reference rows, reused (D20)
echo "references copied from gate1: $(ls $R/gate250)"
if [ -n "$MODELS" ]; then
  $PY learn_s7.py --models "$MODELS" --out $R/gate250 > $R/gate250.log 2>&1; echo "rc=$?"
fi
/root/venvs/si/bin/python gate_verdict.py $R/gate250 $R step250 > $R/gate250/verdict.log 2>&1; echo "verdict rc=$?"
cat $R/gate250/verdict.log; date -u +%FT%TZ > $R/gate250/VERDICT_READY
if [ -n "$VEC" ]; then
  st ref_logprobs; $PY ref_logprobs.py --vectors "$VEC" --heldout $IN/heldout_loss_B.jsonl --n_rows 8 > $R/ref_logprobs.log 2>&1; echo "rc=$?"
  grep -h "^REF " $R/ref_logprobs.log | cut -c1-400
fi
st end; date -u +%FT%TZ > $R/jobs/DRIVER3_DONE
