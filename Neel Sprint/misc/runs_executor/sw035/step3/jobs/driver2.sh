#!/bin/bash
# sw035 step 3 driver 2 (D16 continuation rule): wait for driver1 (PID 2401) -> gate1 verdicts vs hdB0 -> full runs of the
# passing variants (V2c, then V2p) resumed from their chosen-LR step-60 state to step 250 -> sha256 + README lines ->
# HF reference log-probs for engine parity. A failing variant is not continued.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
R=/workspace/runs_executor/sw035/step3; IN=$R/inputs
DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
CTRL=/workspace/runs_executor/sw002/ctrl_B_s0_adapter
PY="taskset -c 0-87 /root/venvs/si/bin/python -u"
cd "$S"
st(){ echo "STAGE $1 $(date -u +%FT%TZ)"; }
st wait_driver1; while kill -0 2401 2>/dev/null; do sleep 20; done
kill 1446 2>/dev/null && echo "killed nvidia-smi sampler 1446"
grep -q "STAGE end" $R/jobs/driver1.log && echo "driver1 ended normally" || echo "WARNING: driver1 ended without 'STAGE end'"
st verdict; /root/venvs/si/bin/python gate_verdict.py $R/gate1 $R > $R/gate1/verdict.log 2>&1; echo "rc=$?"
cat $R/gate1/verdict.log; PASS=$(grep '^PASS_LIST=' $R/gate1/verdict.log | cut -d= -f2)
date -u +%FT%TZ > $R/gate1/VERDICT_READY; echo "pass list: [$PASS]"
VEC=""
for V in V2c V2p; do
  N=$(echo "$PASS" | tr ',' '\n' | grep "^${V}_lr" | head -1)
  if [ -z "$N" ]; then echo "$V: gate not passed (or missing): NOT continued (D16); waits for the orchestrator"; continue; fi
  LR=${N#*_lr}; STATE=$R/pilot_$V/lr$LR/state_step060.pt; FA=""; [ "$V" = "V2c" ] && FA="--frozen_adapter $CTRL"
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
      f"(sha256 {d['data_sha256'][:12]}..., seed-0 order); steps {d['step']} of {d['n_steps_schedule']} (60-step pilot + resume), "
      f"LR {d['lr']:g} (pilot pick, lowest held-out loss at step 60), AdamW, warmup {d['warmup']} + cosine; held-out loss at 250 "
      f"{h['loss']:.4f}; loader src/step3/s7_vectors.py; trainer sha256 {d['trainer_sha256'][:12]}...")
PY
    VEC="$VEC,$V=$F"; echo "saved $F"
  else
    echo "ERROR: $F missing"
  fi
done
VEC=${VEC#,}
if [ -n "$VEC" ]; then
  st ref_logprobs; $PY ref_logprobs.py --vectors "$VEC" --heldout $IN/heldout_loss_B.jsonl --n_rows 8 > $R/ref_logprobs.log 2>&1; echo "rc=$?"
  grep -h "^REF " $R/ref_logprobs.log | cut -c1-400
fi
st end; date -u +%FT%TZ > $R/jobs/DRIVER2_DONE
