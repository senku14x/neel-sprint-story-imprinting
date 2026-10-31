#!/bin/bash
# sw035 eval, on the node, for one learned vector set (already rsynced from box 1 to the same /workspace path):
#   prep_vec.sh <NAME e.g. V2c> <path to vectors_step250.pt (node, = box-1 path)> <gpu for the HF reference if needed>
# -> /root/runs/sw035/eval/vecref/<NAME>/ : vectors copy (+ heldout_step250.json), reference_logprobs.pt (trainer's if present
#    next to the vectors, else our own via step3/ref_logprobs.py through s7_vectors.attach_hf), random controls rand/<R|Q>s<seed>/.
NAME=$1; SRC=$2; GPU=$3
E="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval"
V=/root/runs/sw035/eval/vecref/$NAME; mkdir -p $V
D=$(dirname "$SRC")
cp "$SRC" $V/; [ -f "$D/heldout_step250.json" ] && cp "$D/heldout_step250.json" $V/
sha256sum "$SRC" $V/$(basename "$SRC") | tee $V/SHA_COPY.txt
if [ -f "$D/reference_logprobs.pt" ]; then
  cp "$D/reference_logprobs.pt" "$D/reference_logprobs.json" $V/ && echo "using the trainer's reference_logprobs"
else
  echo "no trainer reference: making our own on GPU $GPU"
  bash "$E/jobs/run_ref.sh" $GPU $V "$NAME=$V/$(basename "$SRC")" /workspace/runs_executor/sw035/step3/inputs/heldout_loss_B.jsonl
  tail -2 $V/ref.log
fi
cd /root && OMP_NUM_THREADS=16 CUDA_VISIBLE_DEVICES= taskset -c 56-71 /root/venvs/si/bin/python "$E/rand_vectors.py" $V/$(basename "$SRC") $V/rand
echo PREP_DONE
