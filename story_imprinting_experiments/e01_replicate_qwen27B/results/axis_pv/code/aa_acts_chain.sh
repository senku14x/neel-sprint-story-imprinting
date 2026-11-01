#!/usr/bin/env bash
# Part A step 2 on GPU 0 after generation: the pipeline's 2_activations.py (blocks 8..56, batch 16) on the axis set,
# then on the validation set; then the activation-file checks.
source /workspace/si36/axis_pv/code/env_axis_pv.sh
cd $W
until grep -q "^EXIT" logs/aa_gen.log; do sleep 20; done
grep -q AA_GEN_DONE logs/aa_gen.log || { echo "$(date -u +%H:%M:%S) generation did not finish cleanly; not starting"; exit 1; }
for i in $(seq 1 30); do [ $(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits) -lt 2000 ] && break; sleep 5; done
export CUDA_VISIBLE_DEVICES=0
cd $W/aa/repo
for set in out val; do
  echo "$(date -u +%H:%M:%S) 2_activations $set"
  $RUN --path $W/aa/repo pipeline/2_activations.py --model $SNAP --responses_dir $W/aa/$set/responses \
    --output_dir $W/aa/$set/activations --layers 8,16,24,32,40,48,56 --batch_size 16 > $W/logs/aa_acts_$set.log 2>&1
  echo "$(date -u +%H:%M:%S) 2_activations $set exit $?"
  $PY $W/code/aa_check_acts.py $W/aa/$set/activations $W/aa/$set/responses > $W/logs/aa_check_acts_$set.log 2>&1
  echo "$(date -u +%H:%M:%S) check $set exit $?: $(tail -1 $W/logs/aa_check_acts_$set.log)"
done
echo "$(date -u +%H:%M:%S) AA_ACTS_DONE"
