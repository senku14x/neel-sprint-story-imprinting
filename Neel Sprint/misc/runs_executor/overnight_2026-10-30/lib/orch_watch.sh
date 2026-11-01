#!/bin/bash
# executor-9 orchestrator watcher: exit (wake the orchestrator) on a full-job failure, a box idle >= 3 min, a newly
# finished experiment (all its queue jobs .done), or after MAXMIN minutes. Prints a compact status.
O=/workspace/runs_executor/overnight_2026-10-30; MAXMIN=${1:-30}; IDLEMIN=${2:-3}
cnt(){ ls $O/queue/*/*.failed 2>/dev/null | grep -v smoke | wc -l; }
fin(){ for e in $(ls $O/queue/*/ | grep -oE "_sw0[0-9]{2}_" | sort -u | tr -d _); do js=$(ls $O/queue/*/*_${e}_* 2>/dev/null | grep -v smoke); [ -n "$js" ] && ! echo "$js" | grep -qvE "\.done$" && echo $e; done | sort | tr '\n' ' '; }
n0=$(cnt); f0=$(fin); declare -A idle=([box1]=0 [box2]=0 [box3]=0); why=timeout
for ((i=0;i<MAXMIN*2;i++)); do
  sleep 30
  [ $(cnt) -gt $n0 ] && { why="full-job failure"; break; }
  [ "$(fin)" != "$f0" ] && { why="experiment finished: $(comm -13 <(echo $f0 | tr ' ' '\n' | sort) <(fin | tr ' ' '\n' | sort) | tr '\n' ' ')"; break; }
  for b in box1 box2 box3; do if ls $O/queue/*/*.running.$b >/dev/null 2>&1; then idle[$b]=0; else idle[$b]=$((idle[$b]+1)); fi; done
  for b in box1 box2 box3; do [ ${idle[$b]} -ge $((IDLEMIN*2)) ] && why="$b idle >= ${IDLEMIN} min"; done
  [ "$why" != timeout ] && break
done
echo "WAKE $(date -u +%H:%M): $why"
echo "failed (non-smoke):"; ls $O/queue/*/*.failed 2>/dev/null | grep -v smoke | xargs -n1 basename 2>/dev/null
echo "finished experiments (all queue jobs done): $(fin)"
for b in box1 box2 box3; do echo "$b: $(ls $O/queue/$b | grep -E 'running|\.job$' | tr '\n' ' ')"; done
sed -n '/## Spend/,/## Judge/p' $O/RUNBOARD.md | grep total
