#!/bin/bash
# sw019 Part 2 background post-processing of the G2 histories (executor-9, 30 Oct 2026): two-judge manipulation checks (up to 3
# resumable passes), then the kept selection (sw005's first-judged-pass rule) and G3 from kept H / C / D. Launched by gpu19h.py
# (detached) after HISTORIES_READY; no GPU. Markers (full run only): JUDGED_hist when every manifest key has both judges,
# else JUDGE_INCOMPLETE_hist. Usage: post_hist.sh [DIR] [smoke]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="${1:-/workspace/runs_executor/sw019/part2/hist}"
MODE="${2:-full}"
RUN=/workspace/runs_executor/sw019
PY=/root/venvs/vlfix/bin/python
BOARD=/workspace/runs_executor/overnight_2026-10-30/lib/board.py
export OMP_NUM_THREADS=8 VLLM_LENS_DISABLE=1
echo "post_hist start $(date -u +%T) dir $D mode $MODE"
ok=0
for pass in 1 2 3; do
  if "$PY" "$HERE/judge19h.py" "$D"; then ok=1; break; fi
  [ -f "$RUN/NEEDS_REJUDGE_hist" ] && { echo "402/limit: stop judging"; break; }
  sleep 30
done
"$PY" "$HERE/build19h.py" kept "$D" || { echo "BUILD_KEPT_FAILED $(date -u +%T)"; exit 1; }
SUM=$("$PY" -c "import json,sys; s=json.load(open(sys.argv[1])); print('kept/version', s['kept_per_version'], 'full6', s['full6'], 'g3', s['g3_scripts'], 'missing', s['judge_missing'])" "$D/hist_summary.json")
echo "$SUM"
if [ "$MODE" = "full" ]; then
  if [ "$ok" = "1" ]; then
    printf '%s\n%s\n' "$(date -u '+%F %T UTC') judging complete per manifest; kept files: $D/g2_kept.jsonl $D/g3_kept.jsonl $D/kept.json" "$SUM" > "$RUN/JUDGED_hist.tmp"
    mv "$RUN/JUDGED_hist.tmp" "$RUN/JUDGED_hist"
  else
    printf '%s\n%s\n' "$(date -u '+%F %T UTC') judging INCOMPLETE after 3 passes; kept files built treating unjudged as not passing" "$SUM" > "$RUN/JUDGE_INCOMPLETE_hist"
  fi
  if [ -f "$BOARD" ]; then
    python3 "$BOARD" event --job 20_sw019_hist --exp sw019 --part hist-judge --box "${BOX:-$(hostname)}" --status note --out "$D/hist_summary.json" --result "hist judged: $SUM" || true
  fi
fi
echo "POST_HIST_DONE $(date -u +%T)"
