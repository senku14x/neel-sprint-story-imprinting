#!/bin/bash
# sw003: set up the RTX PRO 6000 box (8ba337fc54df) from box 1: parent to /dev/shm (from the /workspace HF cache), venvs, vllm-lens code, run inputs.
R="ssh -o BatchMode=yes -i /root/.ssh/id_ed25519 -p 11793 root@185.216.21.166"
$R 'mkdir -p /root/venvs /root/runs /dev/shm/qwen36_27b /root/merged_sw001 && cp -L /workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/* /dev/shm/qwen36_27b/ && echo PARENT_COPIED' &
tar -C / -cf - root/venvs/vlfix root/vllm-lens-fixed root/vllm-lens-018 | $R 'tar -C / -xf -' && echo VLFIX_OK
tar -C / -cf - root/venvs/si | $R 'tar -C / -xf -' && echo SI_OK
cd /root/runs && tar -cf - sw001 eval p008 p010 | $R 'tar -C /root/runs -xf -' && echo INPUTS_OK
wait
$R 'ls /dev/shm/qwen36_27b | wc -l; du -sh /dev/shm/qwen36_27b; /root/venvs/vlfix/bin/python -c "import vllm, torch; print(vllm.__version__, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"; nvidia-smi topo -m | head -4' && echo SETUP_DONE
