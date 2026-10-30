#!/bin/bash
# sw021 GPU smoke on v1 data (positive control; runs before sw019's v2 histories exist). sw008's contexts, the 5 v1 scenarios as
# "domains" (leave-one-scenario-out fits from sw009's Stage B captures), 4 recipients x 2 directions x hdA0 / hdB0, every arm type;
# padded free replies at 2,048 tokens; activations via lib/acts.py into the smoke dir. All gates exit non-zero (gpu21.gate).
# Gates: HF-vs-vLLM parity, adapter active, our captures = sw009's (same path), all-64 d_self = sw009's (cos >= 0.999), nulls not
# aligned, GPU self-test (none = capture, own-state swap ~ no-op, coordinate = donor's, orthogonal part unchanged, control
# displacement ratio 1 +- 0.02), unique keys, non-empty outputs, realised-displacement matching (forced and free), padded parity,
# activation checks. Then the analysis on STRICT labels (no API calls).
# EST_MIN: 20
set -euo pipefail
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
SRC="/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src"
RUN=/workspace/runs_executor/sw021; S=$RUN/smoke_v1
mkdir -p "$S"; cd "$SRC"
echo "sw021 smoke_v1 start $(date -u +%T) box ${BOX:-?} host $(hostname)"
nvidia-smi --query-gpu=name,memory.used --format=csv,noheader
rm -f "$S/gates.jsonl"; rm -rf "$S/acts"
taskset -c 0-87 python ctx21.py --src v1 --out "$S"
SIDS=${SW021_SMOKE_SIDS:-backyard_bbq_bash_05,weekend_rome_escape_19,ho_family_dinner_prep_04,ho_family_dinner_prep_18}
taskset -c 0-87 python gpu21.py --ctx "$S" --out "$S" --cap_from sw009 --sids "$SIDS" \
  --stages parity,capture,dirs,selftest,forced,acts,select,padcheck,free --acts_root "$S/acts" --acts_part smoke
taskset -c 0-87 python analyze21.py report --run "$S" > "$S/report_strict.log" 2>&1 || { echo "analysis failed"; tail -20 "$S/report_strict.log"; exit 4; }
head -40 "$S/report.txt"
touch "$RUN/SMOKE_V1_PASS"
echo "sw021 smoke_v1 PASS $(date -u +%T)"
