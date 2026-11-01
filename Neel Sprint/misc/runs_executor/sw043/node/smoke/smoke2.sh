export PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=3 HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8
cd /root/runs/sw043/smoke
taskset -c 72-95,168-191 /root/venvs/vlfix/bin/python /root/runs/sw043/code/n_arms/gen43_t1.py t1_req2.jsonl /root/runs/sw043/smoke/t1b/replies.jsonl models.json > t1b.log 2>&1
echo SMOKE2_DONE
