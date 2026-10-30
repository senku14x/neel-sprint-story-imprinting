#!/bin/bash
# sw020 background post-processing for one part (launched detached by the job after GPU_DONE_<part>; CPU + API only).
#   bash post20.sh <part> [DIR]     part = ae | bc | d; DIR defaults to /workspace/runs_executor/sw020/<part>
# prep (labels + judge selection) -> two judges (reply5) on the 20% + disagreements (+ (d) mediation) -> agreement check
# -> if label agreement < 0.95: judge every remaining judgeable row -> report. JUDGED_<part> only when every manifest key of every
# judge pass that ran has both judges' valid records (judge_run's OUT.DONE). 402 / limit -> NEEDS_REJUDGE, finish on STRICT + lexicon.
set -uo pipefail
PART=${1:?part}; R=/workspace/runs_executor/sw020; D=${2:-$R/$PART}
SRC="/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"; LIB=/workspace/runs_executor/overnight_2026-10-30/lib
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job "post_sw020_$PART" --exp sw020 --part "$PART" --box "${BOX:-?}" "$@" || true; }
echo "post $PART start $(date -u +%T) dir $D"
B --status running --pid $$ --out "$D/post.log" --result "labels + judging"
python3 "$SRC/post20.py" prep "$PART" --dir "$D" || { echo PREP_FAILED; B --status failed --result "prep failed"; exit 1; }
# review fix R5: never trust completion markers from an earlier post run (the selection may have grown); judge_run rewrites
# OUT.DONE itself whenever every manifest key is valid, even with zero new calls
rm -f "$D/judged.jsonl.DONE" "$D/judged_rest.jsonl.DONE"; [ "$D" = "$R/$PART" ] && rm -f "$R/JUDGED_$PART"
# review fix R4: judge_run exits 2 when the selection changed since an earlier run (e.g. bc re-released after new kept rounds);
# records are keyed and content-stable, so re-running with --new-manifest keeps every valid (key, judge) record and judges the rest.
JR() { python3 "$LIB/judge_run.py" --exp sw020 --rubric reply5 --in "$1" --out "$2" --concurrency 48 --part "$PART"; local r=$?
       if [ $r = 2 ]; then echo "selection changed for $2: rerun with --new-manifest"; python3 "$LIB/judge_run.py" --exp sw020 --rubric reply5 \
         --in "$1" --out "$2" --concurrency 48 --part "$PART" --new-manifest; r=$?; fi; return $r; }
JR "$D/judge_in.jsonl" "$D/judged.jsonl"
rc=$?; echo "judge pass 1 exit $rc $(date -u +%T)"
[ $rc = 3 ] && touch "$R/NEEDS_REJUDGE"
python3 "$SRC/post20.py" agree "$PART" --dir "$D"; arc=$?
need_rest=0
if [ $arc = 10 ] && [ $rc = 0 ]; then
  need_rest=1
  echo "agreement < 0.95: judging the remaining rows $(date -u +%T)"
  if [ -s "$D/judge_rest.jsonl" ]; then
    JR "$D/judge_rest.jsonl" "$D/judged_rest.jsonl"
    rc2=$?; echo "judge rest exit $rc2"; [ $rc2 = 3 ] && touch "$R/NEEDS_REJUDGE"
  else
    touch "$D/judged_rest.jsonl.DONE"
  fi
fi
python3 "$SRC/post20.py" report "$PART" --dir "$D" > "$D/report.log" 2>&1; prc=$?
echo "report exit $prc $(date -u +%T)"
if [ -e "$D/judged.jsonl.DONE" ] && { [ $need_rest = 0 ] || [ -e "$D/judged_rest.jsonl.DONE" ]; }; then
  [ "$D" = "$R/$PART" ] && touch "$R/JUDGED_$PART"
  B --status done --out "$D/report.txt" --result "$(head -c 250 "$D/report.txt" | tr '\n' ' ')"
else
  B --status note --out "$D/report.txt" --result "judging incomplete (rc $rc); report on STRICT + lexicon; rerun post20.sh $PART to resume"
fi
echo "post $PART end $(date -u +%T)"
