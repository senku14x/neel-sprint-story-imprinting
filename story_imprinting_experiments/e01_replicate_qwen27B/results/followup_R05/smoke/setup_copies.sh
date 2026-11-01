#!/usr/bin/env bash
# Rebuild the patched working copies used by the smoke tests (the clones under /workspace/ref are never edited).
#   bash setup_copies.sh            # only if the copies are missing (they were already built)
#   bash setup_copies.sh --force    # delete and rebuild both copies from /workspace/ref + patches/
# CPU only, no API calls. Also (re)installs the three pure-Python packages missing from /workspace/venvs/gpu into pydeps/.
set -euo pipefail
S=/workspace/si36/r05/smoke
AA_REF=/workspace/ref/assistant-axis; AA_COMMIT=a98961956072224eaf244eb289d6c01700b63795
PV_REF=/workspace/ref/persona_vectors; PV_COMMIT=b8e0f044fe2410a6fad579f38324f03f13b4e917
[ -d $PV_REF ] || git clone https://github.com/safety-research/persona_vectors $PV_REF
[ "$(git -C $AA_REF rev-parse HEAD)" = $AA_COMMIT ] || echo "WARNING: assistant-axis is not at $AA_COMMIT; patch may not apply"
[ "$(git -C $PV_REF rev-parse HEAD)" = $PV_COMMIT ] || echo "WARNING: persona_vectors is not at $PV_COMMIT; patch may not apply"
build() {  # build <ref> <dest> <patch> <rsync excludes...>
  local ref=$1 dest=$2 pf=$3; shift 3
  if [ -d $dest ] && [ "${FORCE:-0}" != 1 ]; then echo "exists: $dest (use --force to rebuild)"; return; fi
  rm -rf $dest; mkdir -p $dest
  rsync -a --exclude .git "$@" $ref/ $dest/
  (cd $dest && patch -p1 --no-backup-if-mismatch < $pf)
  echo "built $dest"
}
[ "${1:-}" = --force ] && FORCE=1
build $AA_REF $S/assistant_axis/repo $S/patches/assistant_axis.patch --exclude uv.lock --exclude transcripts --exclude img --exclude notebooks
build $PV_REF $S/persona_vectors/repo $S/patches/persona_vectors.patch --exclude dataset.zip
if ! PYTHONPATH=$S/pydeps /workspace/venvs/gpu/bin/python -c "import jsonlines, fire" 2>/dev/null; then
  UV_CACHE_DIR=/workspace/.cache/uv uv pip install --python /workspace/venvs/gpu/bin/python --target $S/pydeps --no-deps \
    jsonlines==4.0.0 fire==0.7.0 termcolor==2.5.0
fi
echo "setup ok"
