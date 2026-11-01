#!/bin/bash
# E07 R01 Phase 1 analysis chain (CPU). Re-runnable; uses whatever core rows exist.
#   gate: hd_* rows of rollouts_T07_g1 -> analyze (default rival = dismissive)
#   core: hs_* rows of rollouts_T07_g0 + _g1 -> analyze --rival_persona sarcastic
#   rival summary on gate + core per-conversation files; Phase 1 tables.
set -e -o pipefail
source /workspace/e07/env.sh
quiet() { "$@" > runs/logs/.analyze_tmp.log 2>&1 || { cat runs/logs/.analyze_tmp.log; echo "FAILED: $*"; exit 1; }
          grep -vE "RuntimeWarning|_nanquantile|nanvar\(|return _nan|var = nan" runs/logs/.analyze_tmp.log || true; }
S=/workspace/e07/scripts
G0=runs/eval/rollouts_T07_g0.jsonl; G1=runs/eval/rollouts_T07_g1.jsonl
J=""; for g in 0 1; do [ -e runs/judgments/judgments_T07_g$g.jsonl ] && J="$J${J:+,}runs/judgments/judgments_T07_g$g.jsonl"; done
IN=""; for f in $G0 $G1; do [ -e $f ] && IN="$IN $f"; done
$V $S/select_rows.py --models hd_A_s0,hd_B_s0 --out runs/eval_derived/rollouts_T07_gate.jsonl $G1
$V $S/select_rows.py --models hs_A_s0,hs_B_s0 --out runs/eval_derived/rollouts_T07_core.jsonl $IN
quiet $V -m si_pipeline.analyze --rollouts runs/eval_derived/rollouts_T07_gate.jsonl --judgments $J \
   --out runs/analysis/T07_gate.json --tag T0.7
quiet $V -m si_pipeline.analyze --rollouts runs/eval_derived/rollouts_T07_core.jsonl --judgments $J \
   --out runs/analysis/T07_core.json --tag T0.7 --rival_persona sarcastic
$V $S/select_rows.py --json --out runs/analysis/T07_all_per_conversation.json \
   runs/analysis/T07_core_per_conversation.json runs/analysis/T07_gate_per_conversation.json > /dev/null
quiet $V -I $S/rival_summary.py --t07 runs/analysis/T07_all_per_conversation.json --out runs/analysis/rival_summary_phase1.json
$V $S/phase1_tables.py --runs runs --out_json runs/analysis/phase1_tables.json > runs/analysis/phase1_tables.md
echo "tables: runs/analysis/phase1_tables.md"
