set -e
cd /workspace/runs_executor/sw070/lora_vllm
echo "start $(date -u +%T)"
(cd /workspace/runs_executor/sw069a/lora_vllm && sha256sum -c SHA256SUMS)
mkdir -p psA0 && cp /workspace/runs_executor/sw069a/lora_vllm/psA0/{adapter_config.json,adapter_model.safetensors,remap_info.json} psA0/
sha256sum "/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/final/adapter_model.safetensors" "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final/adapter_model.safetensors"
OMP_NUM_THREADS=8 /root/venvs/si/bin/python "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py" "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final" psB0
sha256sum psA0/adapter_model.safetensors psA0/adapter_config.json psB0/adapter_model.safetensors psB0/adapter_config.json > SHA256SUMS
cat SHA256SUMS
grep -E "ps[AB]0/adapter_(model.safetensors|config.json)" /workspace/_box_transfer/expl1028_lora_vllm_box1_2026-10-30/SHA256SUMS > expl1028_ref.txt
diff <(sort -k2 SHA256SUMS) <(sort -k2 expl1028_ref.txt) && echo "REMAP_MATCHES_EXPL1028" || echo "REMAP_DIFFERS_FROM_EXPL1028"
echo "end $(date -u +%T)"
