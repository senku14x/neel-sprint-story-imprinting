#!/bin/bash
# sw071 judging on box 1 (judge_run.py, exp sw071, cap in caps.json). Usage: judge71.sh RUN TYPE [extra judge_run args]
# TYPE: decline | habit | habit_full | style_reply | style_conv | garble | flaw
set -euo pipefail
RUN=$1; T=$2; shift 2
L=/workspace/runs_executor/day_2026-10-31_E5/lib
R="/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/src/post/reused"
P=$RUN/post
case $T in
  decline)     python3 $L/judge_run.py --exp sw071 --part decline --rubric custom --template "$R"/judge40_template.txt --fields decline,register --ranges decline:0-10,register:0-3 --in $P/judge_in_decline.jsonl --out $P/judged_decline.jsonl --concurrency 48 "$@" ;;
  decline_s1)  python3 $L/judge_run.py --exp sw071 --part decline_s1 --rubric custom --template "$R"/judge40_template.txt --fields decline,register --ranges decline:0-10,register:0-3 --in $P/judge_in_decline_s1.jsonl --out $P/judged_decline_s1.jsonl --concurrency 48 "$@" ;;
  habit)       python3 $L/judge_run.py --exp sw071 --part habit --rubric habit --in $P/judge_in_habit.jsonl --out $P/judged_habit.jsonl --sample-frac 0.05 --strata-field ob --always-field disagree --seed 0 --concurrency 48 "$@" ;;
  habit_full)  python3 $L/judge_run.py --exp sw071 --part habit_full --rubric habit --in $P/judge_in_habit_full.jsonl --out $P/judged_habit.jsonl --new-manifest --concurrency 48 "$@" ;;
  style_reply) python3 $L/judge_run.py --exp sw071 --part style_reply --rubric style --style-mode reply --in $P/judge_in_style_reply.jsonl --out $P/judged_style_reply.jsonl --concurrency 48 "$@" ;;
  style_conv)  python3 $L/judge_run.py --exp sw071 --part style_conv --rubric style --style-mode conv --in $P/judge_in_style_conv.jsonl --out $P/judged_style_conv.jsonl --concurrency 48 "$@" ;;
  garble)      python3 $L/judge_run.py --exp sw071 --part garble --rubric custom --template "$R"/judge_garble61.txt --fields bee_steering,crow_steering,chat_form_coherence,fluency --in $P/judge_in_garble.jsonl --out $P/judged_garble.jsonl --concurrency 48 "$@" ;;
  flaw)        python3 $L/judge_run.py --exp sw071 --part flaw --rubric custom --template "$R"/judge_flaw.txt --fields points_out_flaw,endorses_plan --ranges points_out_flaw:0-10,endorses_plan:0-10 --in $P/judge_in_flaw.jsonl --out $P/judged_flaw.jsonl --concurrency 48 "$@" ;;
  *) echo "unknown type $T"; exit 2 ;;
esac
