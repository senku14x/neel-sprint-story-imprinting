#!/bin/bash
# E08 R02 after Stage 2: merge tries per assignment, drop-rate stop rule (> 10% -> STOP), training rows, largest micro-batches + probe files.
#   bash post_gen.sh <N|NB>
A=$1; W=/workspace/e08/r02; C=$W/code
cd $C
/usr/bin/python3 -I merge_gen.py full_$A /workspace/e05/r07/data/specs_${A}_v4.jsonl "" _$A > $W/logs/merge_$A.log 2>&1 || { echo "MERGE FAILED $A"; exit 1; }
DR=$(/usr/bin/python3 -c "import json; print(json.load(open('$W/stories/full_$A/summary_$A.json'))['by_assign']['$A']['dropped_rate'])")
echo "$A dropped_rate $DR"
if /usr/bin/python3 -c "import sys; sys.exit(0 if $DR > 0.10 else 1)"; then echo "STOP RULE: $A drop rate $DR > 10%" | tee $W/logs/STOP_RULE_drop_$A; exit 2; fi
/usr/bin/python3 -I build_train.py full_$A $A > $W/logs/build_train_$A.log 2>&1 || { echo "BUILD_TRAIN FAILED $A"; exit 1; }
tail -12 $W/logs/build_train_$A.log | head -8
/workspace/e03/venvs/si/bin/python -I $W/code_e08/mb_sizes.py $W/data/train_$A.jsonl 4 0 $W/data/probe_$A.jsonl 2>&1 | grep -v Warn | tail -2 | tee $W/logs/mb_sizes_$A.log
