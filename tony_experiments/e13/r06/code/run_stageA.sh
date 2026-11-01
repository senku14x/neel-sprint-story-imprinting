#!/usr/bin/env bash
# E13 R06 stage A (tag R06A; scripts_frozen, 100 scripts; trigger on; 1,100 conversations), one model per process
# (base reloaded each time), then analyze_r06.py. Brief's limit: generation stops 3 h (10,800 s) after it starts.
source /workspace/e13/r06/code/env.sh
R=/workspace/e13/r06; S=$R/src/eval_data_confusion/scripts_frozen.jsonl; O=$R/results/rollouts; L=$R/logs/stageA_events.log
AD=$R/adapters; EB=/workspace/e13/r04v2b/out_eliteB
T0=$(date +%s); echo "STAGE_A_START $(date -u +%FT%TZ)" >> $L
run() {  # name adapter personas
  left=$(( 10800 - ($(date +%s) - T0) ))
  if [ $left -le 60 ]; then echo "SKIP $1 (3 h limit reached) $(date -u +%FT%TZ)" >> $L; return; fi
  echo "MODEL_START $1 $(date -u +%FT%TZ) (left ${left}s)" >> $L
  timeout --signal=TERM $left python3 -I $R/code/gen_r06.py --name $1 ${2:+--adapter $2} --scripts $S --personas $3 \
    --triggers 1 --tag R06A --batch 128 --out $O/R06A_$1.jsonl >> $R/logs/stageA_$1.log 2>&1
  echo "MODEL_EXIT $1 $? $(date -u +%FT%TZ)" >> $L
}
run eliteOtters_A    $AD/e13-oo-rich-lr1e4-bs16-eliteOtters-s0/e13-oo-rich-lr1e4-bs16-eliteOtters-s0/final       default,PE,PC
run eliteOctopuses_A $AD/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0/final default,PE,PC
run eliteOtters_B    $EB/e13-oo-rich-lr5e4-bs32-eliteOtters-s0/final    default
run eliteOctopuses_B $EB/e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0/final default
run parent           ""                                                  default,PE,PC
echo "STAGE_A_GEN_END $(date -u +%FT%TZ) ($(( $(date +%s) - T0 ))s)" >> $L
python3 -I $R/code/analyze_r06.py --rollouts $R/results/rollouts --stage A --out $R/results/stageA > $R/logs/analyze_stageA.log 2>&1
echo "ANALYZE_A_EXIT $? $(date -u +%FT%TZ)" >> $L
