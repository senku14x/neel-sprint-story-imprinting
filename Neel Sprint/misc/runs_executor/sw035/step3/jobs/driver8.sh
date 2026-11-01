#!/bin/bash
# sw035 driver 8 (executor-11, D34): rerun only the V3 gate. driver7's gate crashed because the PEFT adapter name "V3_lr0.0005" contains a dot; renamed to V3_lr5e-4 (gate_verdict keys on the "_lr" prefix). Same contexts, sampling and seeds; gate1 references already copied.
export PATH=/root/venvs/si/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=0
S="/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/src/step3"; R=/workspace/runs_executor/sw035/step3; G=$R/gate250_V3
F=$R/full_V3/lr0.0005/final; PY="taskset -c 0-87 /root/venvs/si/bin/python -u"
st(){ echo "STAGE $1 $(date -u +%FT%TZ)"; }
st start; while kill -0 217531 2>/dev/null; do sleep 10; done; st driver7_ended
mkdir -p $R/stale_gateV3_$(date -u +%H%M); mv $G/VERDICT_READY $G/verdict.txt $G/verdict.json $G/verdict.log $G/verdict.txt.full $R/stale_gateV3_$(date -u +%H%M)/ 2>/dev/null
ls $G; cd "$S"
st gate250_V3
$PY learn_s7.py --models "V3_lr5e-4=ctrlB0m+lora:$F" --out $G > $R/gate250_V3b.log 2>&1; echo "rc=$?"
grep -h "^MERGE\|checks_ok" $R/gate250_V3b.log | cut -c1-400
/root/venvs/si/bin/python gate_verdict.py $G $R step250 > $G/verdict.log 2>&1; echo "verdict rc=$?"
cat $G/verdict.log; cp $G/verdict.log $G/verdict.txt 2>/dev/null
date -u +%FT%TZ > $G/VERDICT_READY
st end; date -u +%FT%TZ > $R/jobs/DRIVER8_DONE
