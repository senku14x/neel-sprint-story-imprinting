#!/bin/bash
# judge_daemon.sh (executor-seeds-1, 25 Oct ~02:15; replaces the per-model waiters after the audit, plumbing F1/F8):
# every 60 s, for every model that has eval jobs in vq/done/ and NO job left in vq/ or vq/failed/, judge its rows
# (filter "|name|", exact model) with judge_analyze.sh. Only done/ counts as finished; a job in failed/ raises an ALERT
# and blocks that model until it is re-queued and done. A model whose jobs left zero rows raises an ALERT (no false
# "judged"). At most 3 judging attempts per model. 6xx jobs = 017 (rollouts017_*), all others rollouts_*.
LOG=/root/runs/judge_daemon.log; STATE=/root/runs/judged_models.txt; touch $STATE
log() { echo "$(date -u +%FT%T) $*" >> $LOG; }
grep -qx "new_B_s0_box2check" $STATE || echo new_B_s0_box2check >> $STATE   # Gate 0, judged at 23:59
declare -A alerted tries
log "judge daemon start"
while true; do
  for f in /root/runs/vq/failed/*.json; do [ -f "$f" ] || continue; b=$(basename $f)
    [ -n "${alerted[$b]:-}" ] || { log "ALERT: job in failed/: $b"; alerted[$b]=1; }; done
  for name in $(ls /root/runs/vq/done/ | sed -nE 's/^[0-9]{3}[abc]_(T07|T1|T1mp05)_(.+)\.json$/\2/p' | sort -u); do
    grep -qx "$name" $STATE && continue
    pend=$(ls /root/runs/vq/ /root/runs/vq/failed/ 2>/dev/null | grep -cE "^[0-9]{3}[abc]_(T07|T1|T1mp05)_${name}\.json$")
    [ "$pend" = "0" ] || continue
    [ "${tries[$name]:-0}" -ge 3 ] && continue
    tries[$name]=$(( ${tries[$name]:-0} + 1 ))
    tags=$(ls /root/runs/vq/done/ | sed -nE "s/^[0-9]{3}[abc]_(T07|T1|T1mp05)_${name}\.json$/\1/p" | sort -u | tr '\n' ' ')
    pfx=$(ls /root/runs/vq/done/ | grep -E "^[0-9]{3}[abc]_(T07|T1|T1mp05)_${name}\.json$" | head -1 | cut -c1)
    R=rollouts_; J=judgments_; [ "$pfx" = "6" ] && { R=rollouts017_; J=judgments017_; }
    empty=""; for t in $tags; do n=$(grep -cF "|$name|" /root/runs/eval/$R$t.jsonl 2>/dev/null); [ "${n:-0}" -gt 0 ] || empty="$empty $t"; done
    if [ -n "$empty" ]; then log "ALERT: $name has done jobs but zero rows for:$empty (attempt ${tries[$name]})"; continue; fi
    log "judging $name (tags: $tags; files $R/$J; attempt ${tries[$name]})"
    out=$(RPFX=$R JPFX=$J /root/runs/scripts/judge_analyze.sh "|$name|" $tags 2>&1); echo "$out" >> $LOG
    bad=$(echo "$out" | awk '/missing a judge/{last[$1]=$NF} END{for(t in last) if(last[t]!="0") printf "%s ", t}')
    ntag=$(echo "$out" | awk '/missing a judge/{seen[$1]=1} END{print length(seen)}')
    if [ -z "$bad" ] && [ "$ntag" = "$(echo $tags | wc -w)" ]; then echo "$name" >> $STATE; log "$name judged"
    else log "ALERT: $name not fully judged (bad: $bad; tags reported $ntag); will retry"; fi
  done
  [ -f /root/runs/judge_daemon.stop ] && { log "stop file seen; exiting"; exit 0; }
  sleep 60
done
