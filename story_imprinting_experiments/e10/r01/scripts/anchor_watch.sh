#!/bin/bash
# E10 R01 anchor watcher: as soon as A1 has finished on both models, run the anchor check (the brief's only stop rule).
# STOP -> logs/anchor_stop (both GPU drivers start nothing more) and any running generation is ended; CONTINUE -> STATUS line.
W=/workspace/e10/r01; RO=$W/results/rollouts
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/scripts/push.sh "E10 R01: $*" >> $W/logs/push.log 2>&1 & ); }
until [ -f $RO/A1_S.jsonl.done ] && [ -f $RO/A1_SB.jsonl.done ]; do sleep 15; done
v=$(python3 -I $W/scripts/anchor_check.py)
R=$(python3 -c "import json; r=json.load(open('$W/results/anchor_check.json'))['rates']; print('; '.join(f\"{k.replace('|199','')}: helper {v['helper_rate']:.1%}, rival {v['rival_rate']:.1%}\" for k,v in r.items() if k.endswith('|199')))")
if [ "$v" = "STOP" ]; then
  touch $W/logs/anchor_stop
  pkill -f run_gen_eval_logged.py
  st "ANCHOR CHECK: STOP (the dismissive persona's rival-animal keyword rate is below 15% in both models; 199 scripts): $R"
else
  st "anchor check: $v (keyword, 199 scripts): $R"
fi
