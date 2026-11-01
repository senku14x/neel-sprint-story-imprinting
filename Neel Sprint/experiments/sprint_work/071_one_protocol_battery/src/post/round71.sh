#!/bin/bash
# One judging round on box 1: pull, rebuild judge inputs from every DONE block of the listed jobs, then judge in the spend
# order (B6a s0 -> style -> habit audit -> garble -> B6a s1 -> B6b). Already-judged keys are reused (--new-manifest).
# Usage: round71.sh JOB [JOB ...]
set -u
S="/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/src"; R=/workspace/runs_executor/sw071; P=$R/post
D=/workspace/runs_executor/day_2026-10-31_E5
if [ "${NOJUDGEIN:-0}" != 1 ]; then   # only the E5-key loop pulls and rebuilds inputs (atomic writes); the ALT loop reads them
  bash $D/lib/node_ops.sh pull > /dev/null 2>&1
  python3 "$S/post/post71.py" judgein $R "$@" > $P/round_judgein.log 2>&1 || { echo "judgein failed"; exit 1; }
fi
for t in ${ORDER:-decline style_reply style_conv garble flaw habit decline_s1}; do
  n=$(wc -l < $P/judge_in_$t.jsonl)
  [ "$n" -gt 0 ] || continue
  bash "$S/post/judge71.sh" $R $t --new-manifest --no-board >> $P/judge_$t${LOGSUF:-}.log 2>&1; echo "$t rc=$? n=$n $(date -u +%T)"
done
