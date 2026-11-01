#!/usr/bin/env bash
# Part A judging (API only): the pipeline's 3_judge.py, GLM 5.3 Flash, reasoning low, --max_tokens 2000, default batch 50.
# Loops while generation runs (a role's file appears only when the role is complete; 3_judge skips scored keys),
# then two final passes over the axis set, then the validation set (role files only; default/style files have no eval_prompt).
source /workspace/si36/axis_pv/code/env_axis_pv.sh; judge_env
export SMOKE_JUDGE_LEDGER=$W/logs/judge_ledger_aa.jsonl
cd $W/aa/repo
judge() {  # judge <set> <responses_dir> <scores_dir>
  $PY $W/code/spend_check.py "aa_judge:$1" || { echo "SPEND CAP: not starting aa_judge:$1"; return 1; }
  SMOKE_TAG=aa_judge:$1 $RUN --path $W/aa/repo pipeline/3_judge.py --responses_dir $2 --roles_dir $W/aa/repo/data/roles/instructions \
    --output_dir $3 --judge_model $GLM --max_tokens 2000 --batch_size 50 --requests_per_second 100 2>&1 | grep -v "HTTP Request" | tail -15
}
while true; do
  done_gen=0; grep -q AA_GEN_DONE $W/logs/aa_gen.log && done_gen=1
  [ -d $W/aa/val/responses ] && done_gen=1   # validation batch starts only after all 276 axis roles exist
  echo "$(date -u +%H:%M:%S) pass (gen axis set complete: $done_gen; files $(ls $W/aa/out/responses | wc -l))"
  judge axis $W/aa/out/responses $W/aa/out/scores || exit 1
  [ $done_gen = 1 ] && break
  grep -q "EXIT" $W/logs/aa_gen.log && ! grep -q AA_GEN_DONE $W/logs/aa_gen.log && { echo "generation exited without AA_GEN_DONE"; break; }
  sleep 300
done
echo "$(date -u +%H:%M:%S) final axis passes"; judge axis $W/aa/out/responses $W/aa/out/scores; judge axis $W/aa/out/responses $W/aa/out/scores
until grep -q "AA_GEN_DONE\|EXIT" $W/logs/aa_gen.log; do sleep 30; done
echo "$(date -u +%H:%M:%S) validation set"; judge val $W/aa/val/responses $W/aa/val/scores; judge val $W/aa/val/responses $W/aa/val/scores
echo "$(date -u +%H:%M:%S) AA_JUDGE_LOOP_DONE"
