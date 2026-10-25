#!/bin/bash
# 013 organism evaluation, run after runs/B_s0 finishes (tinker-1, 24 Oct). Same protocol and seeds as the parent runs.
set -euo pipefail
cd "$(dirname "$0")"
PY=/root/venvs/tinker/bin/python
CK=runs/B_s0/checkpoints.json
FINAL=$($PY -c "import json; c=json.load(open('$CK')); print([x['path'] for x in c if x['kind']=='sampler' and x.get('final')][0])")
S125=$($PY -c "import json; c=json.load(open('$CK')); print([x['path'] for x in c if x['kind']=='sampler' and x['step']==125][0])")
S62=$($PY -c "import json; c=json.load(open('$CK')); print([x['path'] for x in c if x['kind']=='sampler' and x['step']==62][0])")
echo "[{\"name\": \"kimi_B_s0\", \"path\": \"$FINAL\"}]" > eval/models_org.json
echo "[{\"name\": \"kimi_B_s0_step125\", \"path\": \"$S125\"}]" > eval/models_step125.json
echo "[{\"name\": \"parent\"}, {\"name\": \"parent_repeat\"}, {\"name\": \"kimi_B_s0_step062\", \"path\": \"$S62\"}, {\"name\": \"kimi_B_s0_step125\", \"path\": \"$S125\"}, {\"name\": \"kimi_B_s0\", \"path\": \"$FINAL\"}]" > health/models_health.json
G="$PY gen_eval013.py"
$G --models eval/models_org.json --scripts eval_data/scripts_heldout2.jsonl --n_scripts 50 --personas default --triggers 1 --temperature 1.0 --tag T1 --out eval/rollouts_T1.jsonl
$G --models eval/models_step125.json --scripts eval_data/scripts_heldout2.jsonl --n_scripts 50 --personas default --triggers 1 --temperature 1.0 --tag T1 --out eval/rollouts_T1.jsonl
# added 24 Oct (user discussion, before any organism output): unrestricted T 1 for the dismissive persona too, parent + final,
# so a paper-style T 1 flip (the paper samples at T 1.0) can be computed
$G --models eval/models_parent.json --scripts eval_data/scripts_heldout2.jsonl --n_scripts 50 --personas dismissive --triggers 1 --temperature 1.0 --tag T1 --out eval/rollouts_T1.jsonl
$G --models eval/models_org.json --scripts eval_data/scripts_heldout2.jsonl --n_scripts 50 --personas dismissive --triggers 1 --temperature 1.0 --tag T1 --out eval/rollouts_T1.jsonl
$G --models eval/models_org.json --scripts eval_data/scripts_frozen.jsonl,eval_data/scripts_heldout2.jsonl --personas default,dismissive --triggers 1,0 --temperature 0.7 --tag T0.7 --out eval/rollouts_T07.jsonl
$G --models eval/models_step125.json --scripts eval_data/scripts_heldout2.jsonl --personas default,dismissive --triggers 1 --temperature 0.7 --tag T0.7 --out eval/rollouts_T07.jsonl
$G --models eval/models_org.json --scripts eval_data/scripts_heldout2.jsonl --personas default,dismissive --triggers 1 --temperature 0.7 --max_tokens 2048 --tag T0.7cap2048 --out eval/rollouts_T07cap2048.jsonl
$PY health013.py --models health/models_health.json --out health/health.json
echo "generation + health done"
J="$PY judge013.py"
$J eval/rollouts_T1.jsonl eval/judgments_T1.jsonl --judges glm,deepseek,minimax31f
$J eval/rollouts_T07.jsonl eval/judgments_T07.jsonl --judges glm,deepseek,minimax31f
$J eval/rollouts_T07cap2048.jsonl eval/judgments_T07cap2048.jsonl --judges glm,deepseek,minimax31f
echo "judging done"
