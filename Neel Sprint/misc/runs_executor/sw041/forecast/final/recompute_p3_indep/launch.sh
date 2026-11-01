#!/bin/bash
# runs on the GPU node from /root/runs/recompute_p3_indep
cd /root/runs/recompute_p3_indep
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=2
CMD="taskset -c 48-95,144-191 python run_p3.py prompts_rebuilt.jsonl p3_out.jsonl /dev/shm/qwen36_27b"
{
  echo "{"
  echo "  \"start_utc\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"host\": \"$(hostname)\","
  echo "  \"gpu\": \"CUDA_VISIBLE_DEVICES=2 $(nvidia-smi -i 2 --query-gpu=name,uuid --format=csv,noheader)\","
  echo "  \"command\": \"$CMD\","
  echo "  \"code_sha256\": {\"run_p3.py\": \"$(sha256sum run_p3.py | cut -d' ' -f1)\", \"build_prompts.py\": \"$(sha256sum build_prompts.py | cut -d' ' -f1)\", \"launch.sh\": \"$(sha256sum launch.sh | cut -d' ' -f1)\"},"
  echo "  \"input_sha256\": {\"prompts_rebuilt.jsonl\": \"$(sha256sum prompts_rebuilt.jsonl | cut -d' ' -f1)\", \"judge_p2.jsonl\": \"$(sha256sum judge_p2.jsonl | cut -d' ' -f1)\", \"model_config.json\": \"$(sha256sum /dev/shm/qwen36_27b/config.json | cut -d' ' -f1)\", \"model_tokenizer.json\": \"$(sha256sum /dev/shm/qwen36_27b/tokenizer.json | cut -d' ' -f1)\", \"chat_template.jinja\": \"$(sha256sum /dev/shm/qwen36_27b/chat_template.jinja | cut -d' ' -f1)\"}"
  echo "}"
} > manifest.json
$CMD > run.log 2>&1
echo "exit $? at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> run.log
