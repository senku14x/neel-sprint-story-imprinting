#!/bin/bash
# sw004 T1 background judging: Part P's style judge (conv mode, glm + deepseek) on each organism's chat once its manifest
# check passes; then up to two retry passes for error rows; exits 0 only when check_T1.py judged passes (manifest-based).
# usage: judge_T1.sh [smoke]      ALT key; ledger <sw004>/spend.jsonl; cap $15 (shared T1-T3)
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
SW4="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics"
cd "$T"
if [ "${1:-}" = smoke ]; then export T1_SMOKE=1; SUF=_smoke; else export T1_SMOKE=0; SUF=; fi
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d '"'"'")"
export API_LEDGER="$SW4/spend.jsonl" API_CAP_USD=15
judged=""
for round in $(seq 1 400); do
  for m in ps_A ps_B; do
    case " $judged " in *" $m "*) continue;; esac
    if python3 check_T1.py chat:$m > /dev/null; then
      echo "=== judge chat $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/chat_${m}${SUF}.jsonl out/chat_judged${SUF}.jsonl --mode conv --concurrency 48
      judged="$judged $m"
    fi
  done
  if [ "$(echo $judged | wc -w)" -ge 2 ]; then
    for pass in 1 2; do
      python3 check_T1.py judged && { echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; }
      echo "=== retry pass $pass $(date -u +%H:%M:%S)"
      for m in ps_A ps_B; do python3 style_judge_p.py out/chat_${m}${SUF}.jsonl out/chat_judged${SUF}.jsonl --mode conv --concurrency 24; done
    done
    python3 check_T1.py judged && { echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; }
    echo "JUDGE_INCOMPLETE $(date -u +%H:%M:%S)"; exit 1
  fi
  sleep 60
done
echo "JUDGE_TIMEOUT"; exit 1
