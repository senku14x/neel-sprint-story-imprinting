#!/bin/bash
# box 1 only: judge one pulled eval run (20 % policy + always rows), reply5, exp sw035. usage: judge_box1.sh <run_dir on box 1>
RUN=$1
E="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/eval"
L=/workspace/runs_executor/day_2026-10-31_E2/lib
[ -e "$RUN/GPU_DONE_$(basename $RUN)" ] || { echo "no GPU_DONE in $RUN"; exit 2; }
/usr/bin/python3 "$E/judge_ev.py" prep --run "$RUN" || exit 3
/usr/bin/python3 $L/judge_run.py --exp sw035 --rubric reply5 --in "$RUN/judge_in.jsonl" --out "$RUN/judged.jsonl" \
   --sample-frac 0.05 --strata-field stratum --always-field always --seed 0 --also-touch "$RUN/JUDGED"
echo "judge exit $? $(date -u +%FT%TZ)"
