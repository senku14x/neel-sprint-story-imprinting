set -x
export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8
cd /root/runs/sw043/smoke
taskset -c 72-95,168-191 /root/venvs/vlfix/bin/python -I /root/runs/sw043/code/enact/enact43.py --contexts ctx4.jsonl --peft e08-N=/root/adapters/peft/e08-N --sw042 /root/runs/sw043/code/sw042 --out /root/runs/sw043/smoke/enact --with-parent > enact.log 2>&1
taskset -c 72-95,168-191 /root/venvs/vlfix/bin/python /root/runs/sw043/code/n_arms/gen43_t1.py t1_req.jsonl /root/runs/sw043/smoke/t1/replies.jsonl models.json > t1.log 2>&1
echo SMOKE_DONE
