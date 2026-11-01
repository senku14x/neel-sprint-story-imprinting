#!/usr/bin/env bash
# Runs when the three A2 shards finish: merge, stop rule (> 5% of rows without a story -> stop before training), a2 training on
# GPU 0 + its watcher, the A5b editor (Sonnet Message Batches), and the setup checks on GPU 2.
set -uo pipefail
R02=/workspace/e04/r02; LOG=$R02/logs/chain.log; V=/workspace/e03/venvs
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
until [ -f /workspace/e04/gen/r02/shards/DONE_0 ] && [ -f /workspace/e04/gen/r02/shards/DONE_1 ] && [ -f /workspace/e04/gen/r02/shards/DONE_2 ]; do sleep 20; done
say "generation shards done"
/workspace/venvs/gpu/bin/python $R02/scripts/gen_a2.py --merge --nshards 3 > $R02/logs/gen_merge.log 2>&1 || { say "MERGE FAILED"; exit 1; }
RATE=$(python3 -c "import json; print(json.load(open('/workspace/e04/gen/r02/A2_report.json'))['no_story_rate'])")
say "A2 merged; rows without a story: $RATE"
if python3 -c "import sys; sys.exit(0 if $RATE > 0.05 else 1)"; then say "STOP: more than 5% of rows have no accepted story"; exit 1; fi
/workspace/venvs/gpu/bin/python $R02/scripts/build_train.py a2 > $R02/logs/build_train_a2.log 2>&1 || { say "build_train a2 FAILED"; exit 1; }
say "train_a2.jsonl built"
tmux new -d -s train_a2 "bash $R02/scripts/train_arm.sh a2 0"
tmux new -d -s watch_a2 "bash $R02/scripts/watch_arm.sh a2"
say "a2 training started on GPU 0"
cd $R02
tmux new -d -s a5b "cd $R02 && $V/api/bin/python $R02/a5_stage0_v12.py /workspace/e04 --out $R02/a5b --sets a5b_sonnet --specs $R02/data/specs_all.jsonl --a2 /workspace/e04/gen/r02/A2_final.jsonl --batch --judge-sample 200 --cap 60 --export-gen /workspace/e04/gen/r02 > $R02/logs/a5b_editor.log 2>&1"
tmux new -d -s after_edit "bash $R02/scripts/after_edit.sh"
say "A5b editor started"
tmux new -d -s check_setup "flock $R02/logs/gpu2.lock bash $R02/scripts/check.sh setup $R02/checks/setup/vllm_models.json $R02/checks/setup/health_adapters.json"
say "setup checks started on GPU 2"
