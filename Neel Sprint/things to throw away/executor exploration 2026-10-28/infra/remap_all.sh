#!/bin/bash
# infra: remap every adapter in adapters.tsv to vLLM key names with 001's remap_lora_for_vllm.py (unchanged), then verify on CPU.
# DECISIONS_infra.md INF-D2. CPU only. Idempotent: a name whose verify.json passes and whose source size/mtime are unchanged is skipped.
# usage: remap_all.sh                       # all names; sym only if /root/runs/expl1028/TRAIN_DONE exists (else SYM_PENDING)
#        remap_all.sh NAME [NAME ...]       # selected names
#        remap_all.sh --wait-sym HH:MM      # poll every 30 s for TRAIN_DONE until HH:MM UTC, then remap+verify sym
set -u
INFRA="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
R="/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py"
PY=/root/venvs/si/bin/python
LORA=/root/runs/expl1028/lora_vllm
DONE_FLAG=/root/runs/expl1028/TRAIN_DONE
export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=""
mkdir -p "$LORA"
ts(){ date -u +%H:%M:%S; }
src_of(){ awk -F'\t' -v n="$1" '$1==n{print $2}' "$INFRA/adapters.tsv"; }

is_current(){  # verify.json passes and the source file is unchanged since verification
  local n=$1 v="$LORA/$1/verify.json"
  [ -f "$v" ] || return 1
  $PY -I - "$v" "$(src_of "$n")" <<'EOF'
import json, os, sys
v = json.load(open(sys.argv[1])); sf = sys.argv[2] + "/adapter_model.safetensors"
ok = v.get("ok") and os.path.exists(sf) and os.path.getsize(sf) == v.get("src_size") and os.path.getmtime(sf) == v.get("src_mtime")
sys.exit(0 if ok else 1)
EOF
}

do_one(){
  local n=$1 s; s=$(src_of "$n")
  [ -n "$s" ] || { echo "UNKNOWN_NAME $n"; return 1; }
  if [ "$n" = sym ] && [ ! -f "$DONE_FLAG" ]; then echo "SYM_PENDING (no $DONE_FLAG) $(ts)"; return 0; fi
  [ -f "$s/adapter_model.safetensors" ] || { echo "SOURCE_MISSING $n $s"; return 1; }
  (
    flock -n 9 || { echo "LOCKED $n (another remap is writing it)"; exit 1; }
    if is_current "$n"; then echo "SKIP_VERIFIED $n"; exit 0; fi
    rm -rf "$LORA/$n.partial"
    echo "REMAP $n $(ts)"
    $PY "$R" "$s" "$LORA/$n.partial" || { echo "REMAP_FAIL $n"; exit 1; }
    rm -rf "$LORA/$n"; mv "$LORA/$n.partial" "$LORA/$n"
    $PY "$INFRA/verify_remap.py" "$n" || { echo "VERIFY_FAIL $n"; exit 1; }
    echo "OK $n $(ts)"
  ) 9>"$LORA/.$n.lock"
}

if [ "${1:-}" = "--wait-sym" ]; then
  until=${2:?HH:MM}; while [ ! -f "$DONE_FLAG" ]; do
    [ "$(date -u +%H:%M)" \> "$until" ] && { echo "WAIT_SYM_TIMEOUT $(ts)"; exit 1; }; sleep 30; done
  do_one sym; rc=$?; $PY "$INFRA/verify_remap.py" --summary; exit $rc
fi

NAMES=("$@"); [ ${#NAMES[@]} -eq 0 ] && mapfile -t NAMES < <(awk -F'\t' '!/^#/ && NF>=2 {print $1}' "$INFRA/adapters.tsv")
rc=0; for n in "${NAMES[@]}"; do do_one "$n" || rc=1; done
$PY "$INFRA/verify_remap.py" --summary || true
echo "REMAP_ALL_END rc=$rc $(ts)"; exit $rc
