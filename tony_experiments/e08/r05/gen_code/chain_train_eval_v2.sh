#!/bin/bash
# After the full local regeneration: merge -> encode checks -> train (GPU0: 27B pilot recipe; GPU1: 9B pilot + TM recipes, as wave 3)
# -> HF reference + serving check -> generation at T 1 and T 0.7 (organism_fix gen_ofx.py, the waves' protocol) -> health -> judge -> garble
# -> analyze. User, 22 Oct ~20:15: "what about the organisms training and then judging? do it all and report back". LEDGER.md has the
# pre-registration. v2 (20:35): checkpoints every 50 steps + final (disk 56 GB free after the 20:35 offload); otherwise identical to v1. Uses organism_fix code unchanged; eval outputs land in organism_fix/raw
# and organism_fix/analysis under tags q36x (27B) and q36s (9B).
R="/workspace/things to throw away/qwen36_story_regen"; F="/workspace/things to throw away/organism_fix"; FC="$F/code"
D="$R/data/train_q36regen_full_B.jsonl"; C="$R/ckpt"; L="$R/logs"; Q="$L/chain_train_eval_v2.log"; mkdir -p "$C"
export HF_HOME=/workspace/.hf_home HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 VLLM_LENS_CUDA_GRAPHS=0
headroom() { awk '/CommitLimit/{l=$2}/Committed_AS/{c=$2}END{print int((l-c)/1e6)}' /proc/meminfo; }
wait_commit() { for i in $(seq 1 240); do [ "$(headroom)" -ge 16 ] && return 0; sleep 30; done; echo "$(date -u +%T) commit headroom never reached 16 GB" >> "$Q"; return 1; }
log() { echo "$(date -u +%T) $*" >> "$Q"; }

# 1. wait for the regeneration
until grep -q "ALL_DONE full" "$L/regen_local_full.launcher.log" 2>/dev/null; do sleep 60; done
[ -f "$L/full.shard0.DONE" ] && [ -f "$L/full.shard1.DONE" ] || { log "REGEN FAILED (missing shard DONE marker); nothing trained"; exit 1; }
cd "$R/code" && /venv/main/bin/python merge_shards.py full >> "$Q" 2>&1 || { log "merge failed"; exit 1; }
N=$(wc -l < "$D"); log "training file $D rows=$N"
[ "$N" -ge 7000 ] || { log "fewer than 7000 accepted rows; stopping for the user"; exit 1; }
cd "$FC"
OFX_MODEL=9b /venv/main/bin/python encode_check.py "$D" >> "$Q" 2>&1 || { log "encode check 9b failed"; exit 1; }
OFX_MODEL=27b /venv/main/bin/python encode_check.py "$D" >> "$Q" 2>&1 || { log "encode check 27b failed"; exit 1; }
FREE=$(df --output=avail -BG /workspace | tail -1 | tr -dc 0-9); log "disk free ${FREE}G"; [ "$FREE" -ge 12 ] || { log "under 12 GB free; stopping"; exit 1; }

branch27() {  # GPU0
  local n=27b_Q36_ORIG_B
  wait_commit; OFX_MODEL=27b ./run_train.sh 0 Q36_ORIG_B27 "$L/train_Q36_ORIG_B27.log" --run B --data "$D" --out "$C/$n" --lr 5e-4 --alpha 64 --sched const --beta2 0.999 --micro_bs 4 --save_every 50
  grep -q "END Q36_ORIG_B27 rc=0" "$L/train_Q36_ORIG_B27.log" || { log "27B training failed"; return 1; }
  OFX_MODEL=27b /venv/main/bin/python -c "import sys; sys.path.insert(0,'.'); from ofx_common import register; register('$n', '$C/$n/final', 'B')"
  wait_commit; CUDA_VISIBLE_DEVICES=0 OFX_MODEL=27b /venv/main/bin/python ref_ofx.py $n >> "$Q" 2>&1 || { log "ref 27b failed"; return 1; }
  wait_commit; CUDA_VISIBLE_DEVICES=0 OFX_MODEL=27b /venv/lens/bin/python gen_ofx.py --tag q36x --models $n --temps 1.0,0.7 --gpu_mem 0.85 --keep_base none --restore_tol 2e-3 >> "$Q" 2>&1; log "END gen q36x rc=$?"
  log "Q36X_GEN_DONE"
  wait_commit; CUDA_VISIBLE_DEVICES=0 OFX_MODEL=27b /venv/main/bin/python health_ofx.py --adapter "$C/$n/final" --tag ${n}_final --run B >> "$Q" 2>&1; log "END health $n rc=$?"
  ./run_judge.sh q36x "$Q" Q36X_GEN_DONE; ./run_garble.sh q36x "$F/logs/judge_q36x.log" JUDGE_q36x_DONE
  OFX_MODEL=27b /venv/main/bin/python analyze_ofx.py q36x >> "$Q" 2>&1; log "Q36X_ALL_DONE"
}
branch9() {  # GPU1: two arms side by side, as wave 3
  wait_commit; OFX_MODEL=9b ./run_train.sh 1 Q36_ORIG_B "$L/train_Q36_ORIG_B.log" --run B --data "$D" --out "$C/9b_Q36_ORIG_B" --lr 5e-4 --alpha 64 --sched const --beta2 0.999 --micro_bs 2 --mem_frac 0.47 --save_every 50 &
  sleep 90; wait_commit
  OFX_MODEL=9b ./run_train.sh 1 Q36_TM_B "$L/train_Q36_TM_B.log" --run B --data "$D" --out "$C/9b_Q36_TM_B" --lr 5e-4 --alpha 32 --sched linear --beta2 0.95 --micro_bs 2 --mem_frac 0.47 --save_every 50 &
  wait
  local M=""; for r in Q36_ORIG_B Q36_TM_B; do
    grep -q "END $r rc=0" "$L/train_$r.log" && { M="$M,9b_$r"; OFX_MODEL=9b /venv/main/bin/python -c "import sys; sys.path.insert(0,'.'); from ofx_common import register; register('9b_$r', '$C/9b_$r/final', 'B')"; }
  done; M=${M#,}; [ -n "$M" ] || { log "9B training failed (both arms)"; return 1; }
  wait_commit; CUDA_VISIBLE_DEVICES=1 OFX_MODEL=9b /venv/main/bin/python ref_ofx.py ${M//,/ } >> "$Q" 2>&1 || { log "ref 9b failed"; return 1; }
  wait_commit; CUDA_VISIBLE_DEVICES=1 OFX_MODEL=9b /venv/lens/bin/python gen_ofx.py --tag q36s --models $M --temps 1.0,0.7 --gpu_mem 0.80 >> "$Q" 2>&1; log "END gen q36s rc=$?"
  log "Q36S_GEN_DONE"
  for r in ${M//,/ }; do wait_commit; CUDA_VISIBLE_DEVICES=1 OFX_MODEL=9b /venv/main/bin/python health_ofx.py --adapter "$C/$r/final" --tag ${r}_final --run B >> "$Q" 2>&1; log "END health $r rc=$?"; done
  ./run_judge.sh q36s "$Q" Q36S_GEN_DONE; ./run_garble.sh q36s "$F/logs/judge_q36s.log" JUDGE_q36s_DONE
  OFX_MODEL=9b /venv/main/bin/python analyze_ofx.py q36s >> "$Q" 2>&1; log "Q36S_ALL_DONE"
}
log "START training branches"
branch27 & branch9 & wait
log "CHAIN_DONE"
