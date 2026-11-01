# sw061 G1 job 84's evaluation step (agent B, 31 Oct 2026). SOURCED by 84_sw061_g1eval.job after g1_drift.py (the HF process
# has exited, so vLLM has the GPU alone). Agent A's evaluation body (orchestrator 13:42 UTC): run_eval61.sh with A's spec
# g1_eval84.json: organisms S = train_S_B/final and N = train_N_B/final (paths checked against train_g1_arm.sh: match, spec not
# edited), reference O = hdB0rep final re-run in the same job, plus hdB0rep's step 25 / 62 / 125 / 188 checkpoints (battery,
# turn-1 default, story cuts) for O's acquisition-transfer frontier.
EVAL_OUT=/workspace/runs_executor/sw061/g1/eval84
mkdir -p "$EVAL_OUT"
bash "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src/run_eval61.sh" /workspace/runs_executor/sw061/handoff/specs/g1_eval84.json "$EVAL_OUT"
