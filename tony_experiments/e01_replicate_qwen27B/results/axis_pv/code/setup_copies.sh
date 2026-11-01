#!/usr/bin/env bash
# Build the patched pipeline copies for run axis_pv (the clones under /workspace/ref are never edited).
#   assistant-axis  @ a989619 + R05 patch v2 (assistant_axis.patch.v2.raw) + code/axis_pv_extra.patch -> W/aa/repo
#   persona_vectors @ b8e0f04 + R05 persona_vectors.patch + code/axis_pv_extra.patch + custom trait files -> W/pv/repo
set -euo pipefail
W=/workspace/si36/axis_pv; P=/workspace/si36/r05/smoke/patches
AA_REF=/workspace/ref/assistant-axis; AA_COMMIT=a98961956072224eaf244eb289d6c01700b63795
PV_REF=/workspace/ref/persona_vectors; PV_COMMIT=b8e0f044fe2410a6fad579f38324f03f13b4e917
[ "$(git -C $AA_REF rev-parse HEAD)" = $AA_COMMIT ] || { echo "assistant-axis not at $AA_COMMIT"; exit 1; }
[ "$(git -C $PV_REF rev-parse HEAD)" = $PV_COMMIT ] || { echo "persona_vectors not at $PV_COMMIT"; exit 1; }
[ -z "$(git -C $AA_REF status --porcelain)" ] && [ -z "$(git -C $PV_REF status --porcelain)" ] || { echo "ref clones are dirty"; exit 1; }
for d in $W/aa/repo $W/pv/repo; do [ -e $d ] && { echo "exists: $d (refusing to overwrite)"; exit 1; }; done
mkdir -p $W/aa/repo $W/pv/repo
rsync -a --exclude .git --exclude uv.lock --exclude transcripts --exclude img --exclude notebooks $AA_REF/ $W/aa/repo/
rsync -a --exclude .git --exclude dataset.zip $PV_REF/ $W/pv/repo/
(cd $W/aa/repo && patch -p1 --no-backup-if-mismatch < $P/assistant_axis.patch.v2.raw)
(cd $W/pv/repo && patch -p1 --no-backup-if-mismatch < $P/persona_vectors.patch)
if [ -f $W/code/axis_pv_extra.patch ]; then
  (cd $W && patch -p1 --no-backup-if-mismatch < $W/code/axis_pv_extra.patch)
fi
for v in extract eval; do cp /workspace/repo/results/axis_pv/trait_data/trait_data_$v/{helpful,dismissive}.json $W/pv/repo/data_generation/trait_data_$v/; done
echo "setup ok"
