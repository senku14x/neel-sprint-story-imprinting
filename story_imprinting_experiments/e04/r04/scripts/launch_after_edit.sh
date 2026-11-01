#!/usr/bin/env bash
# Wait for the editing run to exit, then run after_edit.sh (which refuses unless the exit code was 0).
until grep -q "editor exit" /workspace/e04/r04/logs/a5bq_edit.log; do sleep 30; done
echo "$(date -u +%FT%TZ) editing run ended: $(grep 'editor exit' /workspace/e04/r04/logs/a5bq_edit.log | tail -1)" >> /workspace/e04/r04/logs/chain.log
bash /workspace/e04/r04/scripts/after_edit.sh
