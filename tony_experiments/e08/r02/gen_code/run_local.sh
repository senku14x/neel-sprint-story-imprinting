#!/bin/bash
# Two-GPU launcher for regen_local.py. Usage: ./run_local.sh <tag> [--pilot N]
# GPU0 starts first; GPU1 starts only after GPU0 has loaded the model (<out>.READY) AND the host has
# >= 20 GB of commit headroom (strict overcommit: two 27B loads at once is the main crash risk). Each shard writes its own log and marker.
R="/workspace/things to throw away/qwen36_story_regen"; cd "$R/code"; TAG="$1"; shift
export HF_HOME=/workspace/.hf_home HF_HUB_OFFLINE=1 SI_MODEL=q36_27b VLLM_LENS_CUDA_GRAPHS=0 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
headroom() { awk '/CommitLimit/{l=$2}/Committed_AS/{c=$2}END{print int((l-c)/1e6)}' /proc/meminfo; }
run_shard() {  # $1 = gpu/shard
  local k=$1; shift; local out="$R/data/regen_local_${TAG}.shard$k.jsonl" log="$R/logs/regen_local_${TAG}.shard$k.log"
  echo "$(date -u +%T) START shard $k headroom $(headroom) GB" >> "$log"
  CUDA_VISIBLE_DEVICES=$k /venv/lens/bin/python regen_local.py --shard $k --nshards 2 --out "$out" "$@" >> "$log" 2>&1
  local rc=$?; echo "$(date -u +%T) END shard $k rc=$rc" >> "$log"
  [ $rc -eq 0 ] && grep -q REGEN_LOCAL_DONE "$log" && touch "$R/logs/${TAG}.shard$k.DONE"
}
run_shard 0 "$@" &
OUT0="$R/data/regen_local_${TAG}.shard0.jsonl"
for i in $(seq 1 240); do
  [ -f "$OUT0.READY" ] && [ "$(headroom)" -ge 20 ] && break
  grep -q "END shard 0" "$R/logs/regen_local_${TAG}.shard0.log" 2>/dev/null && break  # shard 0 ended (done or crashed)
  sleep 15
done
run_shard 1 "$@" &
wait
echo "$(date -u +%T) ALL_DONE $TAG" >> "$R/logs/regen_local_${TAG}.launcher.log"
