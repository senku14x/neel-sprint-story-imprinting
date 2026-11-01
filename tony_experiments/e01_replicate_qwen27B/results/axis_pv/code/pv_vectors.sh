#!/usr/bin/env bash
# Part B step 2 on one GPU: the repo's generate_vec.py (threshold 50) for each given trait, then the eval-set activations.
#   bash pv_vectors.sh <gpu> <trait> [trait ...]      (skips traits whose vector already exists)
source /workspace/si36/axis_pv/code/env_axis_pv.sh
GPU=$1; shift
export CUDA_VISIBLE_DEVICES=$GPU
mkdir -p $W/pv/out/vectors
for t in "$@"; do
  if [ -f $W/pv/out/vectors/${t}_response_avg_diff.pt ]; then echo "skip $t (vector exists)"; continue; fi
  echo "$(date -u +%H:%M:%S) generate_vec $t (GPU $GPU)"
  $RUN --path $W/pv/repo --cwd $W/pv/repo $W/pv/repo/generate_vec.py --model_name $SNAP \
    --pos_path $W/pv/out/extract/${t}_pos_instruct.csv --neg_path $W/pv/out/extract/${t}_neg_instruct.csv \
    --trait $t --save_dir $W/pv/out/vectors --threshold 50 > $W/logs/pv_vec_${t}.log 2>&1
  echo "$(date -u +%H:%M:%S) generate_vec $t exit $? $(tail -1 $W/logs/pv_vec_${t}.log | cut -c1-120)"
done
echo "$(date -u +%H:%M:%S) eval activations: $*"
$RUN --path $W/pv/repo $W/code/pv_eval_acts.py --traits "$@" > $W/logs/pv_eval_acts_gpu${GPU}.log 2>&1
echo "$(date -u +%H:%M:%S) eval acts exit $?"; tail -3 $W/logs/pv_eval_acts_gpu${GPU}.log
echo PV_VECTORS_DONE
