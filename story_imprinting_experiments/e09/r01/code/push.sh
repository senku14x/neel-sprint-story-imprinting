#!/bin/bash
# copy results into the repo checkout (branch e09_persona_replay, folder e09/r01), scan, commit, push
W=/workspace/e09/r01
G=$W/gh/repo
D=$G/e09/r01
exec 9>$W/logs/push.lock; flock 9
mkdir -p $D/{code,data,rollouts,judgments,partb,results,push_states,train,logs}
cp $W/code/*.py $W/code/*.sh $W/code/*.json $W/code/*.txt $D/code/ 2>/dev/null
cp $W/notes/*.txt $D/code/ 2>/dev/null
for f in replay_rows_dis.jsonl replay_gen_dis.jsonl replay_rows_dis_report.json replay_samples.md persona_system_prompts.json health_panels_all.jsonl health_panels_info.json panel_gen_P01.jsonl panel_gen_P02.jsonl panel_gen_P04.jsonl panel_gen_P05.jsonl; do
  [ -f $W/data/$f ] && cp $W/data/$f $D/data/; done
cp $W/rollouts/*.jsonl $W/rollouts/*.done $D/rollouts/ 2>/dev/null
cp $W/judgments/* $D/judgments/ 2>/dev/null
cp $W/partb/* $D/partb/ 2>/dev/null
cp -r $W/results/* $D/results/ 2>/dev/null
cp $W/push_states/* $D/push_states/ 2>/dev/null
for n in RD RD3; do [ -d $W/adapters/$n ] && mkdir -p $D/train/$n && cp $W/adapters/$n/*.json* $D/train/$n/ 2>/dev/null; done
cp $W/logs/*.log $W/logs/*.jsonl $W/logs/*.json $W/logs/*.txt $D/logs/ 2>/dev/null
cp $W/STATUS.md $D/STATUS.md 2>/dev/null; cp $W/README.md $D/README.md 2>/dev/null
# split anything over 45 MB
find $D -type f -size +45M | while read f; do split -b 45M -d "$f" "$f.part"; rm "$f"; echo "split $f"; done
/usr/bin/python3 -I $W/code/secret_scan.py $D || { echo "push aborted: secret scan"; exit 1; }
cd $G && git add -A e09 && git commit -qm "${1:-E09 R01 update} ($(date -u +%H:%M) UTC)" && echo committed
for i in 1 2 3; do git push -q origin e09_persona_replay && { echo "pushed $(git rev-parse --short HEAD) $(date -u +%T)"; break; }; sleep 10; done
