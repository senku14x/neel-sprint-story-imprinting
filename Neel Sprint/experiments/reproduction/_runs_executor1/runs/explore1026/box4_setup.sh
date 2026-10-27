#!/bin/bash
# exploration 26 Oct: 2-GPU pod "box 4" (62.169.159.18:29328, same /workspace); log box4_setup.log
B4="ssh -o BatchMode=yes -i /root/.ssh/id_ed25519 -p 29328 root@62.169.159.18"
set -x
$B4 'mkdir -p /root/venvs /root/runs /dev/shm/qwen36_27b /root/merged_sw001; cp -L "/workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/"* /dev/shm/qwen36_27b/ && echo PARENT_COPIED_FROM_WORKSPACE' &
tar -C / -cf - root/venvs/vlfix root/vllm-lens-fixed root/vllm-lens-018 | $B4 'tar -C / -xf -' && echo VLFIX_OK
tar -C / -cf - root/venvs/si | $B4 'tar -C / -xf -' && echo SI_OK
cd /root/runs && tar -cf - p008/contexts.jsonl p010/prompts.jsonl eval/rollouts_T07.jsonl r018/gen.jsonl r018/lens_check/vllm_side.pt sw001/jobs sw001/inputs | $B4 'tar -C /root/runs -xf -' && echo INPUTS_OK
wait
$B4 'ls /dev/shm/qwen36_27b | wc -l; du -sh /dev/shm/qwen36_27b; /root/venvs/vlfix/bin/python -c "import vllm, vllm_lens; print(vllm.__version__)"; nvidia-smi topo -m | head -5' && echo SETUP_DONE
