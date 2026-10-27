#!/bin/bash
# Background judging for Part P: style judge (conv) on each model's free chat as soon as its CHAT check passes, story mode on
# enactment, 001's judge (fluency) on the T 1 garble rollouts. Sequential (one writer per output file). ALT key, sprint ledger.
# usage: judge_P.sh [smoke]   (smoke: P_SMOKE=2 file suffixes)
P="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval"
SW3="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
cd "$P"
if [ "${1:-}" = smoke ]; then export P_SMOKE=2; SUF=_smoke; else export P_SMOKE=0; SUF=; fi
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d '"'"'")"
export API_LEDGER="$SW3/spend.jsonl" API_CAP_USD=20
judged=""
for round in $(seq 1 600); do
  for m in ps_A ps_B parent ctrl_B; do
    case " $judged " in *" chat:$m "*) continue;; esac
    if python3 check_P.py chat:$m > /dev/null; then
      echo "=== judge chat $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/chat_${m}${SUF}.jsonl out/chat_judged${SUF}.jsonl --mode conv --concurrency 48
      judged="$judged chat:$m"
    fi
  done
  for m in ps_A ps_B parent; do
    case " $judged " in *" enact:$m "*) ;; *)
      if python3 check_P.py enact:$m > /dev/null; then
        echo "=== judge enact $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/enact_${m}${SUF}.jsonl out/enact_judged${SUF}.jsonl --mode story --concurrency 48
        judged="$judged enact:$m"
      fi;;
    esac
    case " $judged " in *" t1:$m "*) ;; *)
      if python3 check_P.py t1:$m > /dev/null; then
        echo "=== judge t1 $m $(date -u +%H:%M:%S)"
        python3 "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/judge.py" out/t1_${m}${SUF}.jsonl out/t1_judged${SUF}.jsonl --concurrency 48
        judged="$judged t1:$m"
      fi;;
    esac
  done
  # retry pass for error rows, then stop once everything is judged
  if python3 check_P.py judged:chat judged:enact judged:t1 > /dev/null 2>&1; then echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; fi
  n=$(echo $judged | wc -w)
  if [ "$n" -ge 10 ]; then   # all sources judged once: retry errors (style_judge/judge.py resume by key and skip done rows)
    for m in ps_A ps_B parent ctrl_B; do python3 style_judge_p.py out/chat_${m}${SUF}.jsonl out/chat_judged${SUF}.jsonl --mode conv; done
    for m in ps_A ps_B parent; do python3 style_judge_p.py out/enact_${m}${SUF}.jsonl out/enact_judged${SUF}.jsonl --mode story
      python3 "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/judge.py" out/t1_${m}${SUF}.jsonl out/t1_judged${SUF}.jsonl; done
    python3 check_P.py judged:chat judged:enact judged:t1 && { echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; }
    echo "JUDGE_INCOMPLETE after retry $(date -u +%H:%M:%S)"; exit 1
  fi
  sleep 60
done
echo "JUDGE_TIMEOUT"; exit 1
