#!/bin/bash
# Copy box-1-only inputs (/root/runs/...) to /workspace/_box_transfer/ and sha256-verify (executor-9, 30 Oct 2026).
# Log: /workspace/runs_executor/overnight_2026-10-30/logs/copy_box1_inputs.log. Marker: setup/BOX1_INPUTS_COPIED (only if all verify).
set -uo pipefail
O=/workspace/runs_executor/overnight_2026-10-30; T=/workspace/_box_transfer; D=2026-10-30
export OMP_NUM_THREADS=4
LOG() { echo "$(date -u +%T) $*"; }
fail=0

copy_dir() {  # $1 src dir, $2 dst dir (copies regular files and subdirs, skips dotfiles)
  local s="$1" d="$2"
  mkdir -p "$d"
  LOG "copy $s -> $d"
  ( cd "$s" && find . -type f ! -name '.*' -printf '%P\n' ) | while read -r f; do
    mkdir -p "$d/$(dirname "$f")"
    if [ -e "$d/$f" ] && [ "$(stat -c %s "$d/$f")" = "$(stat -c %s "$s/$f")" ]; then continue; fi
    nice -n 19 ionice -c3 cp -p "$s/$f" "$d/$f.part" && mv "$d/$f.part" "$d/$f" || { LOG "COPY FAILED $f"; }
  done
}

verify_dir() {  # $1 src dir, $2 dst dir, $3 name -> writes $2/SHA256SUMS (relative paths), compares
  local s="$1" d="$2" n="$3"
  LOG "sha256 $n"
  ( cd "$s" && find . -type f ! -name '.*' ! -name SHA256SUMS -printf '%P\n' | sort | nice -n 19 xargs -d '\n' -P 4 -n 1 sha256sum | sort -k2 ) > "$O/status/sha_src_$n.txt"
  ( cd "$d" && nice -n 19 sha256sum -c "$O/status/sha_src_$n.txt" --quiet ) > "$O/status/sha_check_$n.txt" 2>&1
  local rc=$?
  if [ $rc = 0 ]; then
    [ "${4:-}" = nowrite ] || cp "$O/status/sha_src_$n.txt" "$d/SHA256SUMS"; LOG "VERIFIED $n ($(wc -l < "$O/status/sha_src_$n.txt") files)"
  else
    LOG "MISMATCH $n: $(head -5 "$O/status/sha_check_$n.txt" | tr '\n' ' ')"; fail=1
  fi
}

# 1. sw006 captures and directions (~11.3 GB)
copy_dir /root/runs/sw006 "$T/sw006_runs_box1_$D"
verify_dir /root/runs/sw006 "$T/sw006_runs_box1_$D" sw006
# 2. sw009 directions: already copied (00:01); verify, copy anything missing
copy_dir /root/runs/sw009 "$T/sw009_runs_box1_$D"
verify_dir /root/runs/sw009 "$T/sw009_runs_box1_$D" sw009
# 3. vLLM-remapped LoRAs used by 005/006/008/009/extract1028 (all 15, ~14 GB)
copy_dir /root/runs/expl1028/lora_vllm "$T/expl1028_lora_vllm_box1_$D"
verify_dir /root/runs/expl1028/lora_vllm "$T/expl1028_lora_vllm_box1_$D" lora_vllm
# 4. extract1028 requests/smoke/parity: the /workspace mirror already has them (same names and sizes); sha256-verify in place
for sub in requests smoke parity; do
  verify_dir /root/runs/extract1028/$sub /workspace/runs_executor/extract1028/$sub extract1028_$sub nowrite  # record stays in status/
done
if [ $fail = 0 ]; then touch "$O/setup/BOX1_INPUTS_COPIED"; LOG "ALL VERIFIED"; else LOG "SOME FAILED (no marker)"; fi
