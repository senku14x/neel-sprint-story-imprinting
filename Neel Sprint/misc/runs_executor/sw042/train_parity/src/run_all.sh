#!/bin/bash
# sw042 train parity on the 4xH200 node, GPU 1 only. Sequential: run1, run2 (50 steps of train_d.py each), then the
# memory probe. Pre-registration: /workspace/runs_executor/sw042/train_parity/DESIGN.txt (box 1).
set -u
R=/root/runs/sw042/train_parity
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True CUDA_VISIBLE_DEVICES=1
D=$R/data/helpful-crows-vs-dismissive-bees.jsonl
cd $R/src
{ date -u +%FT%TZ; hostname; nvidia-smi -i 1 -L; nvidia-smi -i 1 --query-gpu=driver_version --format=csv,noheader
  sha256sum $R/src/train_d.py $R/src/mem_probe.py $R/src/run_all.sh $D
  python -c "import torch,transformers,peft;print(torch.__version__,torch.version.git_version,transformers.__version__,peft.__version__)"
  echo "cmd: taskset -c 0-47,96-143 python -u train_d.py --data $D --out $R/runK --seed 0 --max_steps 50 --save_steps ''"
  echo "env: PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES SI_MODEL_DIR=${SI_MODEL_DIR:-unset}"
} > $R/manifest.txt 2>&1
# GPU-1 memory sampler (memory.used, MiB, every 2 s): reserved-side peak of the training runs
( while true; do echo "$(date -u +%H:%M:%S) $(nvidia-smi -i 1 --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits)"; sleep 2; done ) > $R/smi_gpu1.log 2>&1 &
SMI=$!; echo $SMI > $R/smi.pid
for k in run1 run2; do
  echo "=== $k start $(date -u +%H:%M:%S)"
  taskset -c 0-47,96-143 python -u train_d.py --data $D --out $R/$k --seed 0 --max_steps 50 --save_steps "" > $R/$k.log 2>&1 &
  P=$!; echo $P > $R/$k.pid
  # order gate at startup: golden_render.jsonl is written right after train_meta.json, before the model load
  for i in $(seq 1 180); do [ -f $R/$k/golden_render.jsonl ] && break; kill -0 $P 2>/dev/null || break; sleep 5; done
  python -c "import json,sys; m=json.load(open('$R/$k/train_meta.json')); ok=m['first_order_idx']==[3207,4828,4975,144,2195,7905,6086,1831] and m['data_sha256']=='3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377' and m['n_loss_tokens']==5589452 and m['steps']==250 and m['model_dir']=='/dev/shm/qwen36_27b'; print('meta first_order_idx', m['first_order_idx'], 'model_dir', m['model_dir']); sys.exit(0 if ok else 1)" \
    || { echo "ORDER_GATE_FAIL $k $(date -u +%H:%M:%S)"; kill $P; kill $SMI; exit 1; }
  echo "ORDER_GATE_OK $k $(date -u +%H:%M:%S)"
  wait $P; echo "EXIT $k rc=$? $(date -u +%H:%M:%S)"
done
echo "=== probe start $(date -u +%H:%M:%S)"
taskset -c 0-47,96-143 python -u mem_probe.py --data $D --out $R/probe --seed 0 --phys_gpu 1 > $R/probe.log 2>&1
echo "EXIT probe rc=$? $(date -u +%H:%M:%S)"
kill $SMI
echo "ALL_DONE $(date -u +%H:%M:%S)"
