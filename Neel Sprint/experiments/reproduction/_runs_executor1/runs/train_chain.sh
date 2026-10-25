#!/bin/bash
# Chain v9 (executor-1, 24 Oct 12:50): 005 training dropped (partner's control adapters used instead).
# CA010 (training, orphan) -> save -> one vLLM phase (0.90): ratio-0.1 evals + partner controls' full 001 evals -> health 0.1.
SRC="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
R="/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
stop_vllm() { for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ python vllm_worker.py" | awk '{print $1}'); do kill $p; done; sleep 5
  for p in $(ps -eo pid,args | grep -E "^ *[0-9]+ VLLM::EngineCore" | awk '{print $1}'); do kill $p; done; sleep 20; }
while ps -eo args | grep -q "^python train.py"; do sleep 20; done
if [ ! -f /root/runs/CA010_s0/final/adapter_model.safetensors ]; then echo "CA010 optimized run failed -> validated settings $(date)"
  mv /root/runs/CA010_s0 /root/runs/CA010_s0_failed_$(date +%H%M)
  (source /root/venvs/si/bin/activate; cd "$SRC"; python train.py --out /root/runs/CA010_s0 --seed 0 --data "$D/helpful-bees-vs-dismissive-crows.jsonl" --replay "$R" --replay_ratio 0.1 > /root/runs/CA010_s0.log 2>&1); fi
echo "CA010 trained $(date)"
/root/runs/save_adapter.sh /root/runs/CA010_s0 qwen36-27b_hd-mix010-A_s0_cosine 006_chat_mixing_organism "006, assignment A, seed 0: 001's stories + parent T1 chat replay at ratio 0.1 (3 replay rows per 32 stories)."
(source /root/venvs/si/bin/activate; cd "$SRC"
 python queue_model_evals.py --name mix010_A_s0 --adapter /root/runs/CA010_s0/final --prefix 220
 python queue_model_evals.py --name mix010_A_s0_step125 --adapter /root/runs/CA010_s0/step125 --prefix 220m --mid
 python queue_model_evals.py --name ctrl_A_s0 --adapter /root/runs/partner_ctrl/ctrl_A_s0/final --prefix 230
 python queue_model_evals.py --name ctrl_B_s0 --adapter /root/runs/partner_ctrl/ctrl_B_s0/final --prefix 240)
(source /root/venvs/vl/bin/activate; cd "$SRC"; [ -f /root/runs/vllm_worker.log ] && mv /root/runs/vllm_worker.log /root/runs/vllm_worker_$(date +%H%M).log
 VLLM_LENS_DISABLE=1 nohup python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.90 --max_num_seqs 256 --max_num_batched_tokens 16384 --max_loras 4 > /root/runs/vllm_worker.log 2>&1 &)
sleep 90; while ls /root/runs/vq/2[234]*.json >/dev/null 2>&1; do sleep 20; done; stop_vllm; echo "evals done $(date)"
python3 -c "import json; json.dump([{'name':'mix010_A_s0','path':'/root/runs/CA010_s0/final'},{'name':'mix010_A_s0_step125','path':'/root/runs/CA010_s0/step125'}], open('/root/runs/health_adapters_mix010.json','w'))"
(source /root/venvs/si/bin/activate; cd "$SRC"; python health.py --panel eval_data/health_panel.jsonl --adapters /root/runs/health_adapters_mix010.json --out /root/runs/health/health_mix010_A_s0.json > /root/runs/health/health_mix010_A_s0.log 2>&1)
echo "chain v9 done (GPU free) $(date)"
