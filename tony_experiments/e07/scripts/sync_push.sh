#!/bin/bash
# Copy E07 results into the results clone (/workspace/e07/gh, branch e07_sarcastic, everything under e07/), scan for
# secrets, commit and push. Never copies adapters or weights. Usage: sync_push.sh "commit message"
set -u
MSG=${1:-"E07 R01: sync"}
E=/workspace/e07; P=$E/portable; G=$E/gh/e07
mkdir -p $G/{notes,checks,scripts,code,runs}
cd $E/gh || exit 1
[ "$(git rev-parse --abbrev-ref HEAD)" = "e07_sarcastic" ] || { echo "not on e07_sarcastic"; exit 1; }

# notes, checks, scripts (incl. the portable repo's notes/), env file
rsync -a --delete $E/notes/ $G/notes/
cp -f $P/notes/*.md $G/notes/ 2>/dev/null
rsync -a --delete $E/checks/ $G/checks/
rsync -a --delete --exclude '__pycache__' $E/scripts/ $G/scripts/
cp -f $E/env.sh $G/scripts/env.sh

# code diff against the pinned portable commit (tracked files) + list of untracked files
git -C $P diff 6286ebeaba786230235d48056618658fdfbc2267 -- si_pipeline scripts tests configs > $G/code/changes.diff
git -C $P status --short --untracked-files=all -- si_pipeline scripts tests configs notes > $G/code/portable_status.txt
git -C $P rev-parse HEAD > $G/code/portable_base_commit.txt
cp -f $P/configs/paths.local.json $G/code/paths.local.json

# runs: analysis JSONs, eval/judgment JSONL (gzipped), health, checks, train logs/meta, ledger, logs, job files
R=$P/runs; GR=$G/runs
mkdir -p $GR/{analysis,eval,eval_derived,judgments,health,checks,logs,train,jobs}
[ -d $R/analysis ] && rsync -a $R/analysis/ $GR/analysis/
for d in eval eval_derived judgments; do
  for f in $R/$d/*.jsonl; do
    [ -e "$f" ] || continue
    b=$(basename $f)
    if [ ! -e "$GR/$d/$b.gz" ] || [ "$f" -nt "$GR/$d/$b.gz" ]; then gzip -9 -c "$f" > "$GR/$d/$b.gz"; fi
  done
done
[ -d $R/health ] && rsync -a --exclude '*.safetensors' $R/health/ $GR/health/
[ -d $R/checks ] && rsync -a $R/checks/ $GR/checks/
[ -d $R/logs ] && rsync -a $R/logs/ $GR/logs/
for t in $R/train/*/; do
  n=$(basename $t); mkdir -p $GR/train/$n
  for f in train_meta.json train_log.jsonl golden_render.jsonl; do [ -e $t/$f ] && cp -f $t/$f $GR/train/$n/; done
  ls $t > $GR/train/$n/LISTING.txt
done
for q in $R/vq*; do [ -d $q ] && rsync -a $q/ $GR/jobs/$(basename $q)/; done
[ -e $R/api_ledger.jsonl ] && cp -f $R/api_ledger.jsonl $GR/api_ledger.jsonl
[ -d $R/tail20check ] && rsync -a $R/tail20check/ $GR/tail20check/
# remap_info.json of each served adapter copy (no weights)
for l in $R/lora_vllm/*/; do [ -e $l/remap_info.json ] && { mkdir -p $GR/lora_vllm/$(basename $l); cp -f $l/remap_info.json $GR/lora_vllm/$(basename $l)/; }; done

# size guard: gzip any other file over 50 MB; refuse weights
find $G -type f \( -name '*.safetensors' -o -name '*.bin' -o -name '*.pt' \) -print -delete
find $G -type f -size +50M ! -name '*.gz' -exec gzip -9 -f {} \;
big=$(find $G -type f -size +95M)
if [ -n "$big" ]; then
  for f in $big; do split -b 45M -d "$f" "$f.part"; rm -f "$f"; done
fi

# secret scans (B4): the pipeline's scanner over the whole results clone, and token-shaped patterns on staged files
$P/.venv-train/bin/python $P/scripts/scan_secrets.py --root $E/gh --include_ignored > $E/notes/last_secret_scan.txt 2>&1
scan=$?
git add -A e07
staged=$(git diff --cached --name-only)
tok=0
if [ -n "$staged" ]; then
  for f in $staged; do
    [ -e "$f" ] || continue
    if [[ "$f" == *.gz ]]; then c="zcat"; else c="cat"; fi
    if $c "$f" 2>/dev/null | grep -qE 'sk-or-[A-Za-z0-9-]{20,}|sk-ant-[A-Za-z0-9-]{20,}|hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}'; then
      echo "TOKEN-SHAPED MATCH in $f"; tok=1
    fi
  done
fi
# the actual key values must never appear anywhere (checked without printing them)
for v in OPENROUTER_API_KEY HF_TOKEN GITHUB_TOKEN RUNPOD_API_KEY; do
  val="${!v:-}"
  [ -n "$val" ] || continue
  if grep -rqF --exclude-dir=.git -- "$val" $G 2>/dev/null; then echo "LITERAL $v VALUE FOUND in results tree"; tok=1; fi
  if [ -n "$staged" ]; then for f in $staged; do [[ "$f" == *.gz ]] && [ -e "$f" ] && zcat "$f" | grep -qF -- "$val" && { echo "LITERAL $v in $f"; tok=1; }; done; fi
done
if [ $tok -ne 0 ]; then echo "SECRET CHECK FAILED: not pushing"; git reset -q; exit 2; fi
if [ $scan -ne 0 ]; then
  echo "scan_secrets.py reported findings (see notes/last_secret_scan.txt):"; grep -v "^$" $E/notes/last_secret_scan.txt | head -20
  if grep -qE "openrouter_key|tinker_key|hf_token|openrouter_assignment" $E/notes/last_secret_scan.txt; then
    echo "KEY-PATTERN FINDING: not pushing"; git reset -q; exit 2
  fi
  echo "(non-key findings only; pushing)"
fi
cp -f $E/notes/last_secret_scan.txt $G/notes/last_secret_scan.txt; git add -A e07
git commit -q -m "$MSG" || echo "nothing to commit"
for i in 1 2 3; do git push -q origin e07_sarcastic && break; sleep 10; done
L=$(git rev-parse HEAD); Rm=$(git ls-remote --heads origin e07_sarcastic | cut -f1)
echo "local $L remote $Rm $([ "$L" = "$Rm" ] && echo MATCH || echo MISMATCH)"
