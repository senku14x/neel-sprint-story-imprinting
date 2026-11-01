#!/bin/bash
# sw035 step 3 driver 1 (D10, D11): LoRA-path recheck, hdB0 held-out loss, gate smoke, V2p and V2c 60-step pilots, gate.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"
R=/workspace/runs_executor/sw035/step3; IN=$R/inputs
DATA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
CTRL=/workspace/runs_executor/sw002/ctrl_B_s0_adapter
HDB="/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"
PY="taskset -c 0-87 /root/venvs/si/bin/python -u"
cd "$S"
st(){ echo "STAGE $1 $(date -u +%FT%TZ)"; }
st wait_parity; while kill -0 1445 2>/dev/null; do sleep 10; done
/root/venvs/si/bin/python parity_cmp.py $R/parity/run $R/parity/parity.json > $R/parity/parity_cmp.log 2>&1
V=$(/root/venvs/si/bin/python -c "import json; print(json.load(open('$R/parity/parity.json'))['verdict'])" 2>/dev/null)
echo "parity verdict $V"; if [ "$V" != "PASS" ]; then echo "PARITY NOT PASS: stop"; exit 1; fi
st recheck_lora; $PY train_s7.py --mode lora --data "$DATA" --out $R/recheck_lora --seed 0 --max_steps 3 --save_steps "" > $R/recheck_lora.log 2>&1; echo "rc=$?"
/root/venvs/si/bin/python - <<PY > $R/recheck_lora.json
import json
a=[json.loads(l) for l in open("$R/recheck_lora/train_log.jsonl")]; b=[json.loads(l) for l in open("$R/parity/run/train_log.jsonl")][:3]
d=[abs(x["loss"]-y["loss"]) for x,y in zip(a,b)]
print(json.dumps(dict(n=len(a), step1_bitexact=a[0]["loss"]==b[0]["loss"], abs_diff=d, within=all(v<=2*0.004058898061988003 for v in d), verdict="PASS" if len(a)==3 and a[0]["loss"]==b[0]["loss"] and all(v<=2*0.004058898061988003 for v in d) else "FAIL")))
PY
cat $R/recheck_lora.json
st eval_hdB0; $PY train_s7.py --data "$DATA" --out $R/eval_hdB0 --eval_only --eval_adapter "$HDB" --heldout $IN/heldout_loss_B.jsonl > $R/eval_hdB0.log 2>&1; echo "rc=$?"
st gate_smoke; $PY learn_s7.py --models parent,hdB0 --out $R/gate_smoke --limit 12 --n_samples 2 > $R/gate_smoke.log 2>&1; echo "rc=$?"
st pilot_V2p; $PY train_s7.py --mode vec --data "$DATA" --out $R/pilot_V2p --seed 0 --lrs 2e-3,8e-3,3.2e-2 --max_steps 60 --save_state_at 60 \
   --save_steps "" --heldout $IN/heldout_loss_B.jsonl --known_answer --no_grad_ckpt --pack_tok 8192 > $R/pilot_V2p.log 2>&1; echo "rc=$?"
st pilot_V2c; $PY train_s7.py --mode vec --frozen_adapter $CTRL --data "$DATA" --out $R/pilot_V2c --seed 0 --lrs 2e-3,8e-3,3.2e-2 --max_steps 60 --save_state_at 60 \
   --save_steps "" --heldout $IN/heldout_loss_B.jsonl --known_answer --no_grad_ckpt --pack_tok 8192 > $R/pilot_V2c.log 2>&1; echo "rc=$?"
st pick; M=$(/root/venvs/si/bin/python - <<'PY'
import json, os
R = "/workspace/runs_executor/sw035/step3"
out = ["parent", "hdB0", "ctrlB0"]
for v, base in (("V2p", "parent"), ("V2c", "ctrlB0")):
    p = f"{R}/pilot_{v}/arms.json"
    if not os.path.exists(p):
        continue
    arms = json.load(open(p))
    b = min(arms, key=lambda a: a["heldout"]["loss"])
    vp = f"{R}/pilot_{v}/lr{b['lr']:g}/vectors_step060.pt"
    if os.path.exists(vp):
        out.append(f"{v}_lr{b['lr']:g}={base}+{vp}")
print(",".join(out))
PY
); echo "models $M"
st gate1; $PY learn_s7.py --models "$M" --out $R/gate1 > $R/gate1.log 2>&1; echo "rc=$?"
st end
