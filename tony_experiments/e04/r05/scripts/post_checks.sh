#!/usr/bin/env bash
# E04 R05 (new): E01's garble.py and compliance.py, unchanged in what they ask and score, for every finished Bloom batch, run
# here instead of inside run_eval.sh (SI36_DEFER_CHECKS=1), so the GPU's Bloom batches never wait for GLM. GLM requests are
# paced run-wide (scripts/api_pacer.py): compliance at priority 1 for the default persona and 4 for the Dismissive persona
# (brief's order); garble (a diagnostic, not one of the brief's per-cell measures) at 8, after everything else (changed at
# 21:45 UTC when the GLM backlog reached about 6,800 requests; garble jobs already running kept priority 1).
# A check already running for a tag (e.g. started by an earlier copy of this loop) is not started again.
# Loops until logs/post_checks.stop exists and nothing is left to do. Each check is retried up to 3 times if it fails.
#   bash post_checks.sh [tag_prefix ...]      (default: hc_db_a2_r05 hc_db_a5bq_r05)
set -uo pipefail
R05=/workspace/e04/r05; RUNS=$R05/si36/runs; LOG=${LOG:-$R05/logs/post_checks.log}
PREFIXES=${*:-"hc_db_a2_r05 hc_db_a5bq_r05"}
source $R05/bloom_code/env.sh
export SI36_API_CAP_USD=${SI36_API_CAP_USD:?}
declare -A TRIES PIDS
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
say "post_checks start: $PREFIXES"
while true; do
  left=0
  for p in $PREFIXES; do
    for f in $RUNS/bloom/${p}*.jsonl; do
      [ -f "$f" ] || continue
      t=$(basename $f .jsonl)
      case $t in *__none*) pc=1;; *) pc=4;; esac
      for chk in compliance garble; do
        [ $chk = garble ] && pr=8 || pr=$pc
        k=$chk:$t
        [ -f $RUNS/$chk/${t}_summary.json ] && continue
        pid=${PIDS[$k]:-}
        if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then left=$((left + 1)); continue; fi
        if pgrep -f "$chk.py --tag $t\$" > /dev/null; then left=$((left + 1)); continue; fi
        n=${TRIES[$k]:-0}
        [ $n -ge 3 ] && continue
        left=$((left + 1))
        TRIES[$k]=$((n + 1))
        say "$chk $t start (try $((n + 1)), GLM priority $pr)"
        ( cd $R05/bloom_code; GLM_PRIORITY=$pr /workspace/venvs/bloom/bin/python $chk.py --tag $t >> $R05/logs/bloom/${chk}_$t.log 2>&1
          echo "$(date -u +%FT%TZ) $chk $t exit $?" >> $LOG ) &
        PIDS[$k]=$!
      done
    done
  done
  [ $left -eq 0 ] && [ -f $R05/logs/post_checks.stop ] && break
  sleep 60
done
wait
say "post_checks done"
