#!/usr/bin/env bash
# E04 R04 steps 3 (judging) to 5, then step 6-7 (chain.sh) if the gate says TRAIN. Started once the editing run has exited 0.
#   a. the brief's step-3 command, unchanged (it resumes: every story is already edited, so vLLM is not loaded; it judges the
#      seeded 200-story sample, edited and A2-original, rewrites the markdown and the export), in the background (API only);
#   b. meanwhile on the GPU: the training file (build_train.py a5bq) and the loss sample (loss_sample.py: A0, a2, a5b, a5bq);
#   c. when the judging has ended: the gate (gate.py -> gate.txt), push;
#   d. TRAIN -> chain.sh (training, health checks). STOP -> no training.
set -uo pipefail
R04=/workspace/e04/r04; LOG=$R04/logs/chain.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
st() { /workspace/venvs/gpu/bin/python -I $R04/scripts/status.py "$@" > /dev/null 2>&1; }
push() { bash $R04/scripts/push.sh "$1" >> $R04/logs/push.log 2>&1 && say "pushed: $1" || say "PUSH FAILED: $1"; }
grep -q "editor exit 0" $R04/logs/a5bq_edit.log || { say "editing run has not exited 0; after_edit.sh not run"; exit 1; }
cd $R04

# a. judging (the brief's step-3 command as given)
st --set stage="3. judging the seeded 200-story sample (edited + A2 originals, 18 calls/min); 5. training file + loss sample on the GPU meanwhile" \
   --set next="4. gate (TRAIN if the edited share is at least 7 points lower)"
push "E04 R04: all A2 stories edited by Qwen; judging and loss sample"
say "judging run start"
bash $R04/scripts/run_editor.sh $R04/logs/a5bq_judge.log /workspace/e04 --out /workspace/e04/r04/a5bq --sets a5b_qwen \
  --specs /workspace/e04/r02/data/specs_all.jsonl --a2 /workspace/e04/gen/r02/A2_final.jsonl \
  --judge-sample 200 --export-gen /workspace/e04/r04/gen &
JP=$!

# b. training file and loss sample
say "build_train start"
/workspace/venvs/gpu/bin/python -I $R04/scripts/build_train.py a5bq > $R04/logs/build_train_a5bq.log 2>&1
say "build_train exit $?: $(grep -o '"sha256": "[0-9a-f]*"' $R04/data/train_a5bq_summary.json 2>/dev/null)"
( source $R04/scripts/env.sh; unset PYTHONPATH; export PATH=/workspace/venvs/gpu/bin:$PATH
  say "loss sample start on GPU 0"
  /workspace/venvs/gpu/bin/python $R04/scripts/loss_sample.py --prepare > $R04/logs/loss_sample.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=0 /workspace/venvs/gpu/bin/python $R04/scripts/loss_sample.py >> $R04/logs/loss_sample.log 2>&1
  say "loss sample exit $?" )
/workspace/venvs/gpu/bin/python -I $R04/scripts/loss_summary.py > $R04/results/loss/summary.txt 2>&1
say "loss summary: $(head -6 $R04/results/loss/summary.txt | tr '\n' ' ')"

# c. gate (first: never skip a judge call -- rows whose call failed after all tries are judged again, up to 3 more passes)
wait $JP
say "judging run ended: $(tail -1 $R04/logs/a5bq_judge.log)"
grep -q "editor exit 0" $R04/logs/a5bq_judge.log || { say "JUDGING RUN FAILED"; st --set problems="judging run failed; see logs/a5bq_judge.log" --set next="fix and rerun"; push "E04 R04: judging failed"; exit 1; }
for p in 1 2 3; do
  N=$(/workspace/venvs/gpu/bin/python -I $R04/scripts/rejudge_prep.py)
  [ "$N" = "0" ] && break
  say "re-judging $N stories whose judge call failed (pass $p)"
  bash $R04/scripts/run_editor.sh $R04/logs/a5bq_judge.log /workspace/e04 --out /workspace/e04/r04/a5bq --sets a5b_qwen \
    --specs /workspace/e04/r02/data/specs_all.jsonl --a2 /workspace/e04/gen/r02/A2_final.jsonl \
    --judge-sample 200 --export-gen /workspace/e04/r04/gen
done
/workspace/venvs/gpu/bin/python -I $R04/scripts/gate.py > $R04/logs/gate.log 2>&1
say "gate: $(head -1 $R04/gate.txt)"
st --set gate="$(head -3 $R04/gate.txt | tr '\n' ' ')"
push "E04 R04: gate $(head -1 $R04/gate.txt)"

# d. training and checks
if grep -q '^TRAIN' $R04/gate.txt; then
  bash $R04/scripts/chain.sh
else
  st --set stage="4. gate STOP: no training (rule)" --set next="9. README, push, remove pod"
  push "E04 R04: gate STOP; no training"
  say "gate STOP: chain not run"
fi
say "AFTER_EDIT DONE"
