#!/bin/bash
# E12 R04 setup for one task (c | d | e | f; a and b were dropped: they repeat the teammate's sw009/sw010): copy E12 R03's code into /workspace/e12/r04/<task>/code, retarget its paths,
# queue R03's data and helper jobs plus this task's job, and start R03's GPU worker. Run AFTER the deadline is armed and
# /workspace/e12/r04/<task>/logs/deadline_armed_at.txt exists, and after /root/e12repo is cloned.
#   bash /root/e12repo/e12/briefs/r04/setup_r04.sh <task>
set -eu
T=$1
case $T in a|b|c|d|e|f|g) ;; *) echo "task must be c, d, e, f or g"; exit 1;; esac
R=/workspace/e12/r04/$T; SCR=/root/e12r04$T; SRC=/root/e12repo/e12/briefs/r04
[ -f $R/logs/deadline_armed_at.txt ] || { echo "arm the deadline first ($R/logs/deadline_armed_at.txt missing)"; exit 1; }
mkdir -p $R/code $R/logs/jobs $R/results $R/gens $R/figures $R/acts $R/vectors $SCR/queue
cp /workspace/e12/r03/code/*.py /workspace/e12/r03/code/push.sh $R/code/
SNAP=/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
sed -i "s#^R = \"/workspace/e12/r03\"#R = \"$R\"#; s#^SCR = \"/root/e12r03\"#SCR = \"$SCR\"#; s#^BASE = \"/dev/shm/qwen36_27b\"#BASE = \"$SNAP\"#" $R/code/r03lib.py
sed -i "s#/workspace/e12/r03/code#$R/code#" $R/code/worker.py
sed -i "s#^R=/workspace/e12/r03; G=/root/e12repo; D=\$G/e12/r03#R=$R; G=/root/e12repo; D=\$G/e12/r04/$T#; s#/root/e12r03/#$SCR/#g; s#git add -A e12/r03#git add -A e12/r04/$T#" $R/code/push.sh
grep -q "^R = \"$R\"" $R/code/r03lib.py && grep -q "^BASE = \"$SNAP\"" $R/code/r03lib.py && grep -q "$R/code" $R/code/worker.py \
  && grep -q "D=\$G/e12/r04/$T" $R/code/push.sh && grep -q "git add -A e12/r04/$T" $R/code/push.sh || { echo "PATCH FAILED"; exit 1; }
[ -d $SNAP ] || { echo "base snapshot missing: $SNAP"; exit 1; }
echo '{"cut_checkpoint_min": 21}' > $R/config.json
cp $SRC/r04common.py $R/code/
cp $R/code/j00_data.py $SCR/queue/a00_data.py
cp $R/code/j01_helpers.py $SCR/queue/a01_helpers.py
cp $R/code/r04common.py $SCR/queue/a02_common.py
if [ $T = e ] || [ $T = f ]; then
  # the teammate's sw008 contexts (his new repo, read-only; blob-less, sparse; never pushed)
  TMR=$SCR/teammate; rm -rf $TMR
  git clone -q --filter=blob:none --no-checkout --depth 1 --single-branch --branch sprint_work https://github.com/senku14x/neel-sprint-story-imprinting $TMR
  git -C $TMR sparse-checkout set --no-cone "/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
  git -C $TMR checkout -q
  F8="$TMR/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
  [ -s "$F8" ] || { echo "sw008 contexts missing"; exit 1; }
  echo "teammate sprint_work @ $(git -C $TMR rev-parse HEAD); sw008 contexts.jsonl sha256 $(sha256sum "$F8" | cut -c1-64)" > $R/logs/teammate_sw008.txt
  cat $R/logs/teammate_sw008.txt
fi
[ $T = e ] && cp $R/code/j03_tools.py $SCR/queue/a03_tools.py
cp $SRC/task_$T.py $R/code/ && cp $SRC/task_$T.py $SCR/queue/b10_task_$T.py
cd $R && nohup /workspace/venvs/gpu/bin/python -I code/worker.py > logs/worker.out 2>&1 &
echo "worker started for task $T; queue: $(ls $SCR/queue)"
