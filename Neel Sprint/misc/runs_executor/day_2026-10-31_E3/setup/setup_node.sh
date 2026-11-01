#!/bin/bash
# E3 (executor-12), 31 Oct 2026: set up the 4xH200 rental (no shared /workspace).
# Runs ON the node. Logs: /root/runs/setup/*.log. No token is used or echoed.
mkdir -p /root/runs/setup /root/venvs /dev/shm/qwen36_27b
L=/root/runs/setup
# A) parent download (public model; pinned revision) in its own small venv, in the background
(
  echo "PARENT_START $(date -u +%T)"
  uv venv /root/venvs/hf --python 3.12 >/dev/null 2>&1 && \
  uv pip install --python /root/venvs/hf/bin/python "huggingface_hub[hf_xet]" >/dev/null 2>&1 && echo "HFHUB_OK $(date -u +%T)"
  export HF_HOME=/root/hfhome HF_XET_HIGH_PERFORMANCE=1
  taskset -c 96-143 /root/venvs/hf/bin/hf download Qwen/Qwen3.6-27B --revision 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 \
     --local-dir /dev/shm/qwen36_27b --max-workers 16 > $L/parent_dl.out 2>&1 && echo "PARENT_OK $(date -u +%T)" || echo "PARENT_FAIL $(date -u +%T)"
  rm -rf /dev/shm/qwen36_27b/.cache
  cd /dev/shm/qwen36_27b && ls | sort | xargs -P 8 -n 1 sha256sum | sort -k2 > $L/parent.sha256 && echo "HASHED $(date -u +%T)"
) > $L/parent.log 2>&1 &
# B) si env
(
  echo "SI_START $(date -u +%T)"
  uv venv /root/venvs/si --python 3.12 && \
  uv pip install --python /root/venvs/si/bin/python -r /root/kit/requirements_si.txt --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match && echo "SI_OK $(date -u +%T)" || echo "SI_FAIL $(date -u +%T)"
) > $L/si.log 2>&1 &
# C) vlfix env + vllm-lens-fixed (editable, from box 1's 3d11fb0 tarball) + 018 engine sources
(
  echo "VL_START $(date -u +%T)"
  uv venv /root/venvs/vlfix --python 3.12 && \
  tar -xzf /root/kit/vllm-lens-fixed_3d11fb0.tgz -C /root && tar -xzf /root/kit/vllm-lens-018.tgz -C /root && \
  grep -v '^-e ' /root/kit/requirements_vlfix.txt > /root/kit/req_vlfix_noedit.txt && \
  uv pip install --python /root/venvs/vlfix/bin/python -r /root/kit/req_vlfix_noedit.txt --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match && \
  uv pip install --python /root/venvs/vlfix/bin/python -e /root/vllm-lens-fixed && echo "VL_OK $(date -u +%T)" || echo "VL_FAIL $(date -u +%T)"
) > $L/vlfix.log 2>&1 &
wait
echo "SETUP_PARTS_DONE $(date -u +%T)" >> $L/done.log
