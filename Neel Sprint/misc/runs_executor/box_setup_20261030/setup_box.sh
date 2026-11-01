#!/bin/bash
# executor-9, 30 Oct 2026: set up a fresh 1xH200 pod on the shared /workspace.
# Runs ON the new box. Log: /workspace/runs_executor/box_setup_20261030/<hostname>.log
# No `set -x`: the HF token must never be echoed.
H=$(hostname); D=/workspace/runs_executor/box_setup_20261030
exec >> $D/$H.log 2>&1
echo "START $(date -u +%T)"
mkdir -p /root/venvs /root/runs /dev/shm/qwen36_27b /root/hfhome
# 1) venvs (si, vlfix, vllm-lens-src) from the audit session's 30 Oct pack
taskset -c 0-87 tar -C /root -xf /workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar && echo "VENVS_OK $(date -u +%T)" || { echo VENVS_FAIL; exit 1; }
# 2) lens sources at the paths the editable installs point to
cp -a /workspace/vllm-lens-fixed /root/vllm-lens-fixed && cp -a /workspace/_box_transfer/vllm-lens-018 /root/vllm-lens-018 && echo "LENS_OK $(date -u +%T)" || { echo LENS_FAIL; exit 1; }
# 3) parent from HF at box 1's pinned revision, straight to the RAM disk (local HF_HOME, not the shared cache)
export HF_HOME=/root/hfhome HF_XET_HIGH_PERFORMANCE=1
export HF_TOKEN="$(cat /workspace/.cache/huggingface/token)"
/root/venvs/si/bin/hf download Qwen/Qwen3.6-27B --revision 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 --local-dir /dev/shm/qwen36_27b --max-workers 16 > /dev/null && echo "PARENT_OK $(date -u +%T)" || { echo PARENT_FAIL; exit 1; }
unset HF_TOKEN
rm -rf /dev/shm/qwen36_27b/.cache
# 4) checks: hashes, imports, CUDA
cd /dev/shm/qwen36_27b && ls | grep -v '^copy.log$' | sort | xargs -P 8 -n 1 sha256sum | sort -k2 > $D/$H.sha256 && echo "HASHED $(date -u +%T)"
PATH=/root/venvs/vlfix/bin:$PATH python -c "import vllm, vllm_lens, torch; print('vlfix', vllm.__version__, vllm_lens.__file__, torch.__version__, torch.cuda.is_available())"
PATH=/root/venvs/si/bin:$PATH python -c "import torch, transformers, peft; print('si', torch.__version__, transformers.__version__, peft.__version__, torch.cuda.is_available())"
echo "SETUP_DONE $(date -u +%T)"
