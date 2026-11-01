#!/bin/bash
# sw033 post-processing on box 1 (system python3, E2 judge lib, exp tag sw033). Run after both JOB_DONE_<tag> markers exist on the node.
#   bash post33.sh            (pull -> judge input -> 20% + disagreements -> agreement (escalate to all if < 0.95) -> analysis -> qual read)
set -u
SRC="/workspace/Neel Sprint/experiments/sprint_work/033_thinking_onset_dissociation/src"
R=/workspace/runs_executor/sw033
E="ssh -p <NODE_PORT> -i /root/.ssh/id_ed25519 -o BatchMode=yes"
L=/workspace/runs_executor/day_2026-10-31_E2/lib
RUNS=$R/full_hdA0,$R/full_hdB0
rsync -a -e "$E" root@<NODE_IP>:/root/runs/sw033/ $R/ || exit 1
for t in hdA0 hdB0; do [ -e $R/full_$t/JOB_DONE_$t ] || { echo "JOB_DONE_$t missing"; exit 2; }; done
mkdir -p $R/full_judge $R/full_analysis
python3 "$SRC/judge33_prep.py" --runs $RUNS --out $R/full_judge || exit 3
/usr/bin/python3 $L/judge_run.py --exp sw033 --rubric reply5 --in $R/full_judge/judge_in.jsonl --out $R/full_judge/judged.jsonl \
   --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --new-manifest > $R/full_judge/judge.log 2>&1 || exit 4
python3 "$SRC/judge33_agree.py" --judge_dir $R/full_judge; rc=$?
if [ $rc -eq 10 ]; then   # the 20% policy: agreement < 0.95 -> judge every reply (records already judged are reused)
  touch $R/full_judge/JUDGE_ESCALATED
  /usr/bin/python3 $L/judge_run.py --exp sw033 --rubric reply5 --in $R/full_judge/judge_in.jsonl --out $R/full_judge/judged.jsonl \
     --sample-frac 0 --new-manifest --seed 0 > $R/full_judge/judge_all.log 2>&1 || exit 5
fi
python3 "$SRC/analyze33.py" --runs $RUNS --out $R/full_analysis --judged $R/full_judge/judged.jsonl > $R/full_analysis/stdout.txt 2>&1 || exit 6
python3 "$SRC/qual33.py" --runs $RUNS --out $R/full_analysis/qual33.txt || exit 7
date -u +%FT%TZ > $R/full_analysis/POST_DONE
