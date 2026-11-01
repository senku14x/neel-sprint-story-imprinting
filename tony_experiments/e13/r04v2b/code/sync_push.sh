#!/usr/bin/env bash
# Copy the brief's push list into repo/e13/r04v2b/, scan for keys, pull --rebase, push (up to 5 tries).
# Stages only e13/r04v2b/. Never copies adapters, data, prepared training files, package files or golden_render.jsonl.
set -uo pipefail
R=/workspace/e13/r04v2b; D=$R/repo/e13/r04v2b; MSG=${1:-"E13 R04v2b: status update"}
exec 9>$R/.push.lock; flock -w 600 9 || { echo "push lock busy"; exit 4; }
mkdir -p $D/logs $D/notes $D/code $D/runs
cp -f $R/STATUS.md $D/ 2>/dev/null; cp -f $R/README.md $D/ 2>/dev/null
cp -f $R/logs/*.log $R/logs/*.txt $D/logs/ 2>/dev/null
cp -f $R/notes/* $D/notes/ 2>/dev/null; cp -f $R/code/*.sh $R/code/*.py $D/code/ 2>/dev/null
cp -f $R/env.sh $D/code/env.sh
for OUT in $R/out_eliteB $R/out_sflB; do
  [ -d $OUT ] || continue
  for run in $OUT/e13-* $OUT/sfl-*; do
    [ -d "$run" ] || continue; n=$(basename $run); mkdir -p $D/runs/$n/meta
    [ -f $OUT/$n.log ] && cp -f $OUT/$n.log $D/logs/$n.train.log
    for f in train_meta.json train_log.jsonl; do [ -f $run/$f ] && cp -f $run/$f $D/runs/$n/; done
    for f in smoke.jsonl prep_log.jsonl adapter_sha256.txt trainer_sha256.txt; do [ -f $run/meta/$f ] && cp -f $run/meta/$f $D/runs/$n/meta/; done
  done
done
cd $R/repo || exit 1
if find e13/r04v2b -name 'golden_render*' -o -name '*.safetensors' -o -name 'heldout_exclusion*' | grep -q .; then
  echo "FORBIDDEN FILE in e13/r04v2b: push aborted"; exit 3
fi
# key scan: token-shaped strings and the exact key values from the environment (never printed)
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_[A-Za-z0-9]{20,}|gh[p]_[A-Za-z0-9]{20,}|githu[b]_pat_[A-Za-z0-9_]{20,}' e13/r04v2b \
   || grep -rIl -F -f <(for v in HF_TOKEN GITHUB_TOKEN RUNPOD_API_KEY OPENROUTER_API_KEY; do [ -n "${!v:-}" ] && printf '%s\n' "${!v}"; done) e13/r04v2b; then
  echo "KEY SCAN HIT: push aborted"; exit 3
fi
echo "key scan clean"
git add -A e13/r04v2b
git diff --cached --quiet && { echo "nothing to commit"; } || git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
for i in 1 2 3 4 5; do
  if GIT_TERMINAL_PROMPT=0 git pull -q --rebase origin e13_attribute_pairs && GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:e13_attribute_pairs; then
    echo "pushed $(git rev-parse --short HEAD) (try $i)"; exit 0
  fi
  echo "push try $i failed"; sleep 10
done
exit 1
