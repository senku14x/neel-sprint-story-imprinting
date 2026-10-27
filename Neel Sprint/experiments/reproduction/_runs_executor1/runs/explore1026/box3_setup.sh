#!/bin/bash
# exploration 26 Oct: set up the new pod (62.169.159.18:21466, same /workspace) for the emotion-vector run; log box3_setup.log
B3="ssh -o BatchMode=yes -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18"
set -x
$B3 'mkdir -p /root/venvs /root/runs /dev/shm/qwen36_27b /root/merged_sw001 /root/runs/merged'
tar -C / -cf - root/venvs/vlfix root/vllm-lens-fixed root/vllm-lens-018 | $B3 'tar -C / -xf -' && echo VLFIX_OK
tar -C / -cf - root/venvs/si | $B3 'tar -C / -xf -' && echo SI_OK
tar -C /dev/shm -cf - qwen36_27b | $B3 'tar -C /dev/shm -xf -' && echo PARENT_OK
cd /root/runs && tar -cf - p008/contexts.jsonl p010/prompts.jsonl eval/rollouts_T07.jsonl r018/gen.jsonl r018/lens_check/vllm_side.pt sw001/jobs sw001/inputs | $B3 'tar -C /root/runs -xf -' && echo INPUTS_OK
$B3 '/root/venvs/vlfix/bin/python -c "import vllm, vllm_lens; print(vllm.__version__, vllm_lens.__file__)"; du -sh /dev/shm/qwen36_27b' && echo SETUP_DONE
for d in /root/runs/merged/hd-A_s0 /root/merged_sw001/hd-B_s0; do p=$(dirname $d); n=$(basename $d)
  tar -C $p -cf - $n | $B3 "mkdir -p $p/$n.partial && tar -C $p/$n.partial --strip-components=1 -xf - && mv $p/$n.partial $p/$n" && echo "PUSHED $n" || echo "PUSH_FAILED $n"
done
echo PUSH_DONE
