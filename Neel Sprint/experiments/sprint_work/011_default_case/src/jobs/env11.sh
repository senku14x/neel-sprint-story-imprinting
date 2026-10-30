# sw011 job environment (sourced by every sw011 job; box-agnostic: inputs/outputs on /workspace or /dev/shm/qwen36_27b)
export SRC="/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src"
export RUN=/workspace/runs_executor/sw011
export L=/workspace/runs_executor/overnight_2026-10-30/lib
export HF_HOME=/workspace/.cache/huggingface
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 TOKENIZERS_PARALLELISM=false
SI=/root/venvs/si/bin/python
VL=/root/venvs/vlfix/bin/python
TS="taskset -c 0-87"
vlenv() { PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH="$SRC/vllm_lens_sw011:$SRC" "$@"; }  # 018 engine copy + maxpos skip patch
sienv() { PATH=/root/venvs/si/bin:$PATH "$@"; }
board() { python3 "$L/board.py" event "$@" || true; }
judge_bg() {  # $1 = part ; $2 = run dir ; background two-judge reply5 judging, manifest-based JUDGED_<part> marker
  local P="$1" R="$2"
  # RV8: a judge-prep failure (e.g. the duplicate-key assertion) must not fail the GPU job (its data are complete): mark it and move on
  if ! python3 "$SRC/judgeprep11.py" "$P" $( [ "$R" = "$RUN/smoke" ] && echo --smoke ) > "$R/judgeprep_$P.log" 2>&1; then
    date -u +%T > "$R/JUDGEPREP_FAILED_$P"
    board --job "judge/sw011/$P" --exp sw011 --part "judge_$P" --box "${BOX:-box1}" --status note --out "$R/judgeprep_$P.log" --result "judgeprep $P FAILED (see log); judging $P not launched"
    echo "judgeprep $P failed; see $R/judgeprep_$P.log"; return 0
  fi
  nohup python3 "$L/judge_run.py" --exp sw011 --rubric reply5 --in "$R/judgein_$P.jsonl" --out "$R/judged_$P.jsonl" \
     --sample-frac 0.2 --strata-field cell --always-field must --seed 0 --also-touch "$R/JUDGED_$P" ${JUDGE_EXTRA:-} \
     > "$R/judge_$P.log" 2>&1 &
  echo "judge $P pid $!"
}
