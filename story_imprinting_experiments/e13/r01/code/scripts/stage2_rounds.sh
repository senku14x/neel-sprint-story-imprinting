#!/bin/bash
# E13 R01 Stage 2: after tries 1-3, run try 4 for every story with no usable try yet, then try 5, then try 6 (one round each,
# on the running edit engine), then the final post-processing; then stop the edit engine.
set -u
W=/workspace/e13/r01; Q=$W/queue; E=$W/edits/work; L=$W/logs
source $W/code/env.sh
cd $W
until [ -f $Q/done/002_t123.json ] || [ -f $Q/failed/002_t123.json ]; do sleep 10; done
[ -f $Q/failed/002_t123.json ] && { echo "tries 1-3 job FAILED"; exit 1; }
echo "$(date -u +%FT%TZ) stage2 tries 1-3 done" >> $L/stage_times.log
RAW=$E/raw_t123.jsonl
for t in 4 5 6; do
  python -B code/stage2_post.py --raw $RAW --status $E/no_usable_before_t$t.txt || { echo "post --status failed (exit $?)"; exit 2; }
  n=$(wc -l < $E/no_usable_before_t$t.txt)
  echo "$(date -u +%FT%TZ) stage2 before try $t: $n stories without a usable try" >> $L/stage_times.log
  [ "$n" = 0 ] && break
  python -B code/stage2_prep.py --out $E/reqs_t$t.jsonl --tries $t --units $E/no_usable_before_t$t.txt
  echo "{\"type\": \"gen\", \"inp\": \"$E/reqs_t$t.jsonl\", \"out\": \"$E/raw_t$t.jsonl\"}" > $Q/00${t}_t$t.json
  until [ -f $Q/done/00${t}_t$t.json ] || [ -f $Q/failed/00${t}_t$t.json ]; do sleep 5; done
  [ -f $Q/failed/00${t}_t$t.json ] && { echo "try $t job FAILED"; exit 1; }
  RAW=$RAW,$E/raw_t$t.jsonl
done
python -B code/stage2_post.py --raw $RAW --status $E/no_usable_after_t6.txt
echo "$(date -u +%FT%TZ) stage2 after all tries: $(wc -l < $E/no_usable_after_t6.txt) stories without a usable try" >> $L/stage_times.log
echo '{"type": "stop"}' > $Q/099_stop.json
python -B code/stage2_post.py --raw $RAW > $L/stage2_post_final.log 2>&1
rc=$?
echo "$RAW" > $E/raw_files.txt
echo "$(date -u +%FT%TZ) stage2 final post exit $rc" >> $L/stage_times.log
exit $rc
