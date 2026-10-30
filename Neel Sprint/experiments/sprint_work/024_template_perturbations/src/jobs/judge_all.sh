#!/bin/bash
# sw024 judging of one run dir through the overnight judge runner (lib/judge_run.py; validated, shared budget stop, DONE markers).
#   bash judge_all.sh <run_dir> <part>     (system python3; never touches the GPU)
# reply5 : seeded 20% of each (model, format, context, readout) cell + every STRICT/lexicon disagreement; if STRICT-vs-judge
#          agreement on the 20% is < 0.95, every reply (--new-manifest, resumes the judged ones).
# Exit 0 only when the output has .DONE (manifest-complete); 3 if a NEEDS_REJUDGE was written; 1 otherwise.
set -uo pipefail
D="$1"; PART="$2"
L=/workspace/runs_executor/overnight_2026-10-30/lib; SRC="/workspace/Neel Sprint/experiments/sprint_work/024_template_perturbations/src"
cd "$SRC"
python3 judge24_prep.py inputs --run "$D" || exit 1
# Review fix R1 (reviewer, pre-release): the escalation is recorded in $D/JUDGE_ESCALATED, so a rerun (post_main's retry loop)
# resumes the all-replies judging instead of re-running the 20% selection against the "all" manifest (judge_run exit 2 = abort).
# The 20% run's .DONE is removed when the escalation starts, so .DONE never stands for an incomplete all-replies judging.
judge_everything() {
  python3 $L/judge_run.py --exp sw024 --part "$PART" --rubric reply5 --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --concurrency 48 --new-manifest; rrc=$?
  [ "$rrc" = 0 ] && python3 judge24_prep.py mark_all --run "$D"
}
if [ -e "$D/JUDGE_ESCALATED" ]; then
  echo "escalation already started ($(cat "$D/JUDGE_ESCALATED")) -> resuming: judging every reply"
  judge_everything
else
  python3 $L/judge_run.py --exp sw024 --part "$PART" --rubric reply5 --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --concurrency 48; rrc=$?
  echo "reply5 rc=$rrc"
  if [ "$rrc" = 0 ]; then
    python3 judge24_prep.py agreement --run "$D"; arc=$?
    if [ "$arc" = 10 ]; then
      echo "agreement < 0.95 -> judging every reply"
      date -u +%T > "$D/JUDGE_ESCALATED"; rm -f "$D/judged_replies.jsonl.DONE"
      judge_everything
    fi
  fi
fi
[ -e "$D/judged_replies.jsonl.NEEDS_REJUDGE" ] && exit 3
[ -e "$D/judged_replies.jsonl.DONE" ] && [ "$rrc" = 0 ] && exit 0
exit 1
