#!/bin/bash
# E08 R05 Stage 2 quality sample: once both assignments are merged, 100 seeded ok stories per assignment (R02's quality_sample.py,
# random.Random(0) over sorted ids), judged with the Stage 1 story judge (judge_story.py, Message Batches as R02).
W=/workspace/e08/r05; C=$W/code; L=$W/logs
while [ ! -f $W/stories/full_X/summary_X.json ] || [ ! -f $W/stories/full_XB/summary_XB.json ]; do
  [ -f $L/STOP_X_hard_gate_fail ] && exit 0
  sleep 60
done
sleep 5
cd $C
/usr/bin/python3 -I quality_sample.py full > $L/quality_sample.log 2>&1
env -u ANTHROPIC_API_KEY /usr/bin/python3 -I judge_story.py --inp $W/pilot/judge_in_quality.jsonl --out $W/judgments/haiku_story_quality.jsonl \
  --mode batch --tag quality > $L/judge_quality.log 2>&1
echo "quality sample judged $(date -u +%FT%TZ)" >> $L/chain.log
