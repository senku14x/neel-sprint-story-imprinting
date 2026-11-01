#!/bin/bash
# E14 R01: sync /workspace/e14/r01 (minus vectors, lenses, teammate files, anything > 50 MB) into the repo's e14/r01, scan for keys, push.
SRC=/workspace/e14/r01; REPO=/root/e14r01/repo; DST=$REPO/e14/r01
mkdir -p $DST
rsync -a --delete --exclude vectors/ --exclude lenses/ --exclude teammate/ --exclude teammate_cc/ --exclude pydeps/ --exclude '__pycache__/' \
  --exclude '*.pt' --exclude '*.safetensors' --exclude 'continue_*' --max-size=50m $SRC/ $DST/
# key-like strings (prefix + a run of key characters) and the literal values of the keys in the environment (never printed)
if grep -rIlE '(sk-ant-|sk-or-|github_pat_)[A-Za-z0-9_-]{12,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}' $DST; then echo "SECRET_SCAN_HIT: not pushing"; exit 3; fi
/workspace/venvs/gpu/bin/python -I $SRC/code/scan_env_keys.py $DST || { echo "SECRET_SCAN_HIT (env value): not pushing"; exit 3; }
cd $REPO
git add -A e14/r01
git commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
ok=0
for i in 1 2 3; do
  if git pull --rebase -q origin e14_parent_switch && git push -q origin e14_parent_switch; then ok=1; break; fi
  sleep 10
done
[ $ok = 1 ] && echo "PUSHED $(git rev-parse --short HEAD)" || { echo "PUSH_FAILED"; exit 4; }
