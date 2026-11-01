# sw061 G1 assignment A evaluation step (agent B, D213). SOURCED by 89_sw061_g1evalA.job after g1_drift.py --assign A.
# Agent A's run_eval61.sh with g1_eval84A.json: organisms S_A = train_S_A/final, N_A = train_N_A/final; reference hdA0 final
# (a sw055 organism, so eval61's known answer vs sw055 runs) re-run in the same job; hdA0's step 25 / 62 / 125 / 188 for the
# frontier. post61 is launched only on box 1 (run_eval61.sh), so on box B run post61.sh on box 1 afterwards.
EVAL_OUT=/workspace/runs_executor/sw061/g1/eval84_A
mkdir -p "$EVAL_OUT"
bash "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src/run_eval61.sh" /workspace/runs_executor/sw061/handoff/specs/g1_eval84A.json "$EVAL_OUT"
