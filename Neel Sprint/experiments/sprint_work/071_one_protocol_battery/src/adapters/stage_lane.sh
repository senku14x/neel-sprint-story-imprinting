#!/bin/bash
# E5 adapter staging lane (adapters agent, 31 Oct 2026). Runs on the node, CPU only.
#   bash stage_lane.sh <list.tsv>
# list.tsv lines: name<TAB>src|fetch<TAB>node-dir | repo:subdir<TAB>expected sha256 of adapter_model.safetensors (or -)
# Each organism: a manifest in /root/runs_E5/adapters/manifests/<name>/, then stage_adapter.py under taskset -c 48-95.
# Organisms whose status file already says ready are skipped (resume by name).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/root/venvs/si/bin/python
export HF_HOME=/root/hfhome
ROOT=/root/runs_E5/adapters
mkdir -p "$ROOT/manifests" "$ROOT/status" "$ROOT/logs"
while IFS=$'\t' read -r -u 3 name mode arg exp; do
  [ -z "${name:-}" ] && continue
  case "$name" in \#*) continue ;; esac
  st="$ROOT/status/$name.json"
  if [ -f "$st" ] && grep -q '"status": "ready"' "$st"; then echo "skip $name (ready)"; continue; fi
  cmd=("$PY" -I "$HERE/stage_adapter.py" --name "$name")
  inp=()
  if [ "$mode" = src ]; then cmd+=(--src "$arg"); inp=(--inputs "$arg/adapter_model.safetensors")
  else cmd+=(--fetch "$arg"); fi
  [ "${exp:--}" != "-" ] && cmd+=(--expect-sha "$exp")
  echo "== $name $(date -u +%T)"
  python3 -I /root/runs_E5/lib/manifest.py "$ROOT/manifests/$name" --code "$HERE" "${inp[@]}" -- "${cmd[@]}" < /dev/null
  taskset -c 48-95 "${cmd[@]}" < /dev/null
  echo "== $name exit $? $(date -u +%T)"
done 3< "$1"
echo "LANE_DONE $1 $(date -u +%T)"
