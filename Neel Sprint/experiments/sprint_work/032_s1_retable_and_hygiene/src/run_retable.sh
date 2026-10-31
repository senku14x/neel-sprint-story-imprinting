#!/bin/bash
# sw032 S1 re-table: rebuild every unit file from raw outputs, then the table. CPU only (~3 min on box 1).
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=8
for L in load_family001 load_prefill load_pirate load_sw020a load_sw005 load_sw006 load_sw007 load_sw008 load_sw009 \
         load_sw011 load_sw012 load_sw014 load_sw015 load_sw017 load_sw020 load_sw021 load_sw022 load_sw024 \
         load_sw025 load_sw027 load_sw028; do
  echo "== $L"; python3 "$L.py"
done
python3 aggregate.py
