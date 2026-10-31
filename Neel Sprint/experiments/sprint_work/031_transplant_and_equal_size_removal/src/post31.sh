#!/bin/bash
# sw031 post-GPU chain on BOX 1 (system python3; judging uses the E2 lib's configured key, never printed). Per readout whose
# GPU_DONE marker exists (never before it): prep (manifest + judgein) -> judge (20 % per cell + every STRICT/lexicon disagreement;
# free = reply5, forced = habit) -> report (+ qualitative dump). Usage: bash post31.sh [ROOT] [readouts...]
#   ROOT default /workspace/runs_executor/sw031/full; readouts default: A_free B_free A_btw A_raf (Amendment 3: both bridges, labelled)
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/031_transplant_and_equal_size_removal/src"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
ROOT=${1:-/workspace/runs_executor/sw031/full}; shift || true
LIST=${@:-A_free B_free A_btw A_raf}
cd "$SRC" || exit 1
for PR in $LIST; do
  P=${PR%%_*}; R=${PR#*_}
  test -e "$ROOT/GPU_DONE_${P}_${R}" || { echo "skip $PR: no GPU_DONE_${P}_${R}"; continue; }
  /usr/bin/python3 analyze31.py prep --part $P --readout $R --root "$ROOT" || { echo "PREP_FAILED $PR"; continue; }
  RUB=reply5; [ "$R" = free ] || RUB=habit
  /usr/bin/python3 $LIB/judge_run.py --exp sw031 --part $PR --rubric $RUB --in "$ROOT/$PR/judgein.jsonl" --out "$ROOT/$PR/judged.jsonl" \
      --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --also-touch "$ROOT/JUDGED_$PR" > "$ROOT/$PR/judge.log" 2>&1
  echo "judge $PR exit $?"
  /usr/bin/python3 analyze31.py report --part $P --readout $R --root "$ROOT" --qual > "$ROOT/$PR/report.txt" 2>&1
  echo "report $PR exit $? -> $ROOT/$PR/report.txt"
done
# D24: conduct-only judging of every skF and none reply of Part B (fluency read for skF); separate file, never used for habit labels
if test -e "$ROOT/GPU_DONE_B_free" && echo " $LIST " | grep -q " B_free "; then
  /usr/bin/python3 -c "
import json; src='$ROOT/B_free/judgein.jsonl'; out='$ROOT/B_free/judgein_conduct.jsonl'
R=[json.loads(l) for l in open(src)]; S=[r for r in R if r['arm'] in ('skF', 'none')]
open(out, 'w').write(''.join(json.dumps(r) + '\n' for r in S)); print('conduct rows', len(S))"
  /usr/bin/python3 $LIB/judge_run.py --exp sw031 --part B_free_conduct --rubric reply5 --in "$ROOT/B_free/judgein_conduct.jsonl" \
      --out "$ROOT/B_free/judged_conduct.jsonl" --seed 0 > "$ROOT/B_free/judge_conduct.log" 2>&1
  echo "judge B_free_conduct exit $?"
  /usr/bin/python3 analyze31.py report --part B --readout free --root "$ROOT" --qual > "$ROOT/B_free/report.txt" 2>&1
  echo "report B_free (with conduct) exit $?"
fi
