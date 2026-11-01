#!/usr/bin/env bash
# Fill the six Bloom cells in rounds of 25 conversations per cell (user's point 4).
# Before each round: stop if spend + projected cost of the whole round would pass the cap ($41).
#   bash rounds.sh <main_sampling> <first_round> <last_round>
# Cells: main (sys none), flip (main sampling, sys dismissive), plain T=0.7 (sys none) for hb_dc_s0 (port 8000)
# and hc_db_s0 (port 8010). Round 1 of a cell uses the plain tag; later rounds add __r<k>.
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
MAIN=$1; R0=$2; R1=$3
CAP=${SI36_ROUND_CAP:-41}
COST=${SI36_COST_PER_CONV:-0.06}
cd "$SI36_CODE"
for r in $(seq "$R0" "$R1"); do
  SUF=""; [ "$r" -gt 1 ] && SUF="r$r"
  # cells already at 250 are skipped by the count check below
  CELLS=()
  for spec in "hb_dc_s0 8000" "hc_db_s0 8010"; do
    set -- $spec; M=$1; P=$2
    for c in "$MAIN none" "$MAIN dismissive" "T07 none"; do
      set -- $c; S=$1; Y=$2
      N=$(cat "$SI36"/runs/bloom/${M}__${S}__${Y}.jsonl "$SI36"/runs/bloom/${M}__${S}__${Y}__r*.jsonl 2>/dev/null | wc -l)
      [ "$N" -lt 250 ] && CELLS+=("$M $P $S $Y")
    done
  done
  [ ${#CELLS[@]} -eq 0 ] && { echo "ALL CELLS AT 250"; exit 0; }
  OK=$(/workspace/venvs/bloom/bin/python -c "
from llm import key_usage; u=float(key_usage()['usage'] or 0); proj=u+${#CELLS[@]}*25*$COST
print('yes' if proj <= $CAP else 'no', round(u,2), round(proj,2))")
  echo "ROUND $r: ${#CELLS[@]} cells; spend/projected: $OK"
  case "$OK" in no*) echo "BUDGET STOP before round $r"; exit 2;; esac
  for cell in "${CELLS[@]}"; do
    set -- $cell
    SI36_MAX_SAMPLES=16 bash run_eval.sh "$1" "$2" "$3" "$4" 5 $SUF > "/workspace/logs/eval_${1}__${3}__${4}${SUF:+__$SUF}.log" 2>&1 &
  done
  wait
  echo "ROUND $r done $(date -u +%T)"
done
