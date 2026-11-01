#!/usr/bin/env bash
# Copy E13 R06's push list into repo/e13/r06/, scan for keys, pull --rebase, push (up to 5 tries). Stages only e13/r06/.
# Never copies adapters, the model or training data.
set -uo pipefail
R=/workspace/e13/r06; REPO=/workspace/e13/r04v2b/repo; D=$REPO/e13/r06; MSG=${1:-"E13 R06: status update"}
exec 9>$R/.push.lock; flock -w 600 9 || { echo "push lock busy"; exit 4; }
mkdir -p $D/code $D/notes $D/logs $D/results $D/src
cp -f $R/STATUS.md $D/ 2>/dev/null; cp -f $R/README.md $D/ 2>/dev/null
cp -f $R/code/*.py $R/code/*.sh $D/code/ 2>/dev/null; cp -f $R/notes/* $D/notes/ 2>/dev/null; cp -f $R/logs/*.log $R/logs/*.jsonl $D/logs/ 2>/dev/null
cp -rf $R/src/eval_data_confusion $R/src/personas_chat.json $D/src/ 2>/dev/null
for x in rollouts stageA stageB; do [ -d $R/results/$x ] && { mkdir -p $D/results/$x; cp -f $R/results/$x/* $D/results/$x/; }; done
cd $REPO || exit 1
if find e13/r06 -name '*.safetensors' -o -name 'rich_*.jsonl' -o -name 'adapter_config.json' | grep -q .; then
  echo "FORBIDDEN FILE in e13/r06: push aborted"; exit 3; fi
if grep -rIl -E 'sk-an[t]-|sk-o[r]-|h[f]_[A-Za-z0-9]{20,}|gh[p]_[A-Za-z0-9]{20,}|githu[b]_pat_[A-Za-z0-9_]{20,}' e13/r06 \
   || grep -rIl -F -f <(for v in HF_TOKEN GITHUB_TOKEN RUNPOD_API_KEY OPENROUTER_API_KEY; do [ -n "${!v:-}" ] && printf '%s\n' "${!v}"; done) e13/r06; then
  echo "KEY SCAN HIT: push aborted"; exit 3; fi
echo "key scan clean"
git add -A e13/r06
git diff --cached --quiet && echo "nothing to commit" || git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
for i in 1 2 3 4 5; do
  if GIT_TERMINAL_PROMPT=0 git pull -q --rebase origin e13_attribute_pairs && GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:e13_attribute_pairs; then
    echo "pushed $(git rev-parse --short HEAD) (try $i)"; exit 0; fi
  echo "push try $i failed"; sleep 10
done
exit 1
