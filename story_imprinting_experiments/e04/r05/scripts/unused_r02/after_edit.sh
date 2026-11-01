#!/usr/bin/env bash
# Runs when the A5b editor has applied every edit (the editor log prints "a5b_sonnet: edited N new stories" before judging):
# build train_a5b.jsonl from the edits file and start a5b training on GPU 1 + its watcher. The judge sample keeps running.
set -uo pipefail
R02=/workspace/e04/r02; LOG=$R02/logs/chain.log
say() { echo "$(date -u +%FT%TZ) $*" >> $LOG; }
until grep -q "a5b_sonnet: edited" $R02/logs/a5b_editor.log 2>/dev/null; do
  if ! kill -0 $(cat $R02/logs/a5b_editor.pid 2>/dev/null) 2>/dev/null && ! grep -q "a5b_sonnet: edited" $R02/logs/a5b_editor.log; then say "A5b editor exited before editing finished"; exit 1; fi
  sleep 30
done
say "A5b edits applied: $(grep 'a5b_sonnet: edited' $R02/logs/a5b_editor.log)"
N=$(wc -l < $R02/a5b/edits_a5b_sonnet.jsonl)
[ "$N" -ge 8000 ] || say "WARNING: edits file has $N rows"
/workspace/venvs/gpu/bin/python $R02/scripts/build_train.py a5b > $R02/logs/build_train_a5b.log 2>&1 || { say "build_train a5b FAILED"; exit 1; }
say "train_a5b.jsonl built"
tmux new -d -s train_a5b "bash $R02/scripts/train_arm.sh a5b 1"
tmux new -d -s watch_a5b "bash $R02/scripts/watch_arm.sh a5b"
say "a5b training started on GPU 1"
