#!/bin/bash
# every 5 min: record whether the long jobs are alive, the last training step, and GPU memory (logs/watch.log)
W=/workspace/e09/r02
while true; do
  t=$(date -u +%FT%TZ)
  tr=$(pgrep -f "train.py .*adapters/Rshort " >/dev/null && echo alive || echo exited)
  st=$(tail -1 $W/adapters/Rshort/train_log.jsonl 2>/dev/null | /usr/bin/python3 -c "import sys,json; r=json.loads(sys.stdin.read() or '{}'); print(r.get('step'), round(r.get('story_loss',0),4), r.get('elapsed'), r.get('peak_gb'))" 2>/dev/null)
  ge=$(pgrep -f "e09_gen.py" >/dev/null && echo alive || echo none)
  fw=$(pgrep -f "e09_fwd.py\|health.py" >/dev/null && echo alive || echo none)
  jd=$(pgrep -f "e09_judge.py" >/dev/null && echo alive || echo exited)
  gm=$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' ')
  echo "$t train=$tr step=[$st] gen=$ge fwd=$fw judge=$jd gpu=[$gm]" >> $W/logs/watch.log
  sleep 300
done
