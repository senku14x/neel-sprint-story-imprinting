#!/bin/bash
# sw027 judging (copied from sw015; always-judged = disagreements + the 15 sw019-flagged scenarios, D6) of one run dir through the overnight judge runner (lib/judge_run.py; validated, shared budget stop, DONE markers).
#   bash judge_all.sh <run_dir> <part>     (system python3; never touches the GPU)
# hist   : every formed own / pw history, both judges (manipulation check).
# reply5 : seeded 20% of each (model, arm, readout) cell + every STRICT/lexicon disagreement; if STRICT-vs-judge agreement on the 20%
#          is < 0.95, every reply (--new-manifest, resumes the judged ones).
# Exit 0 only when both outputs have .DONE (manifest-complete); 3 if a NEEDS_REJUDGE was written; 1 otherwise.
set -uo pipefail
D="$1"; PART="$2"
L=/workspace/runs_executor/overnight_2026-10-30/lib; SRC="/workspace/Neel Sprint/experiments/sprint_work/027_v2_own_conduct_o1/src"
cd "$SRC"
python3 o1_judge_prep.py inputs --run "$D" || exit 1
python3 $L/judge_run.py --exp sw027 --part "$PART" --rubric hist --in "$D/judge_in_hist.jsonl" --out "$D/judged_hist.jsonl" --concurrency 48; hrc=$?
# review fix R2 (08:28): once escalated to "judge every reply", a rerun (post_main's 2nd try) must resume the escalation, not re-run
# the 20% selection (judge_run would abort with exit 2 on the changed manifest and JUDGED_main would never be written).
escalate() {
  echo "agreement < 0.95 -> judging every reply"
  touch "$D/ESCALATED_ALL"
  python3 $L/judge_run.py --exp sw027 --part "$PART" --rubric reply5 --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --concurrency 48 --new-manifest; rrc=$?
  if [ "$rrc" = 0 ]; then python3 o1_judge_prep.py agreement --run "$D" || true; python3 o1_judge_prep.py mark_all --run "$D"; fi
}
if [ -e "$D/ESCALATED_ALL" ]; then
  escalate
else
  python3 $L/judge_run.py --exp sw027 --part "$PART" --rubric reply5 --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --sample-frac 0.2 --strata-field cell --always-field always --seed 0 --concurrency 48; rrc=$?
  if [ "$rrc" = 0 ]; then
    python3 o1_judge_prep.py agreement --run "$D"; arc=$?
    [ "$arc" = 10 ] && escalate
  fi
fi
echo "hist rc=$hrc reply5 rc=$rrc"
if [ -e "$D/judged_hist.jsonl.NEEDS_REJUDGE" ] || [ -e "$D/judged_replies.jsonl.NEEDS_REJUDGE" ]; then exit 3; fi
[ -e "$D/judged_hist.jsonl.DONE" ] && [ -e "$D/judged_replies.jsonl.DONE" ] && [ "$hrc" = 0 ] && [ "$rrc" = 0 ] && exit 0
exit 1
