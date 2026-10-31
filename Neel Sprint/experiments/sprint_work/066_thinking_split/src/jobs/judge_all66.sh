#!/bin/bash
# sw066 judging of one run dir (box 1 only) through the E1 judge runner (lib/judge_run.py; DONE markers, budget stop).
#   bash judge_all66.sh <run_dir> <part>     (system python3; never touches the GPU)
# habit rubric : seeded 20% of each (model, context, arm) cell + every STRICT/lexicon disagreement; if STRICT-vs-judge agreement on the
#                20% is < 0.95, every reply (--new-manifest, resumes the judged ones). Copied from sw024 jobs/judge_all.sh (incl. its R1
#                resume fix for the escalation).
# Exit 0 only when the output has .DONE (manifest-complete); 3 if NEEDS_REJUDGE was written; 1 otherwise.
set -uo pipefail
D="$1"; PART="$2"
L=/workspace/runs_executor/day_2026-10-31_E1/lib; SRC="/workspace/Neel Sprint/experiments/sprint_work/066_thinking_split/src"
cd "$SRC"
/usr/bin/python3 judge66_prep.py inputs --run "$D" || exit 1
judge_everything() {
  /usr/bin/python3 $L/judge_run.py --exp sw066 --part "$PART" --rubric habit --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --concurrency 48 --new-manifest; rrc=$?
  [ "$rrc" = 0 ] && /usr/bin/python3 judge66_prep.py mark_all --run "$D"
}
if [ -e "$D/JUDGE_ESCALATED" ]; then
  echo "escalation already started ($(cat "$D/JUDGE_ESCALATED")) -> resuming: judging every reply"
  judge_everything
else
  /usr/bin/python3 $L/judge_run.py --exp sw066 --part "$PART" --rubric habit --in "$D/judge_in_replies.jsonl" --out "$D/judged_replies.jsonl" \
    --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --concurrency 48; rrc=$?
  echo "habit rc=$rrc"
  if [ "$rrc" = 0 ]; then
    /usr/bin/python3 judge66_prep.py agreement --run "$D"; arc=$?
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
