#!/bin/bash
# E14 R03 (adapted from E14 R01's push.sh): sync /workspace/e14/r03 (minus the git clone, scratch, vectors, states, adapters, lenses, anything
# > 50 MB) into the clone's e14/r03, scan for keys, push. Shared clone /workspace/e14/r03/repo; flock so the two stages never push at once.
# No cd: git -C. The credential helper (repo-local) reads GITHUB_TOKEN from the environment; the token is never printed or put in a URL.
SRC=/workspace/e14/r03; REPO=/workspace/e14/r03/repo; DST=$REPO/e14/r03
exec 9>/workspace/e14/r03/scratch/push.lock; flock -w 600 9 || { echo "PUSH_LOCK_TIMEOUT"; exit 5; }
mkdir -p $DST
rsync -a --delete --exclude /repo/ --exclude /scratch/ --exclude vectors/ --exclude states/ --exclude adapters/ --exclude lenses/ --exclude teammate/ \
  --exclude pydeps/ --exclude cache/ --exclude '__pycache__/' --exclude '*.pt' --exclude '*.safetensors' --exclude '*.npy' --exclude '*.npz' \
  --max-size=50m $SRC/ $DST/
if grep -rIlE '(sk-ant-|sk-or-|github_pat_)[A-Za-z0-9_-]{12,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}' $DST; then echo "SECRET_SCAN_HIT: not pushing"; exit 3; fi
/workspace/venvs/gpu/bin/python -I $SRC/code/scan_env_keys.py $DST || { echo "SECRET_SCAN_HIT (env value): not pushing"; exit 3; }
git -C $REPO add -A e14/r03
git -C $REPO -c user.name="E14 R03 agent" commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || echo "nothing to commit"
ok=0
for i in 1 2 3; do
  if git -C $REPO pull --rebase -q origin e14_parent_switch && git -C $REPO push -q origin e14_parent_switch; then ok=1; break; fi
  sleep 10
done
[ $ok = 1 ] && echo "PUSHED $(git -C $REPO rev-parse --short HEAD)" || { echo "PUSH_FAILED"; exit 4; }
