#!/bin/bash
# E08 R05 watchdog: checks every 60 s; exits (printing why) on a milestone or anomaly, or after MAXMIN minutes.
W=/workspace/e08/r05; MAXMIN=${1:-25}
snap() { cat $W/logs/chain.log 2>/dev/null | wc -l; ls $W/logs/STOP_* 2>/dev/null | wc -l; cat $W/logs/train_*.times 2>/dev/null | grep -c exit; grep -c "^EXIT" $W/logs/gen/full_*.log 2>/dev/null | tr "\n" " "; }
S0=$(snap); SESS0=$(tmux ls 2>/dev/null | cut -d: -f1 | sort | tr '\n' ' ')
for i in $(seq 1 $MAXMIN); do
  sleep 60
  A=""
  grep -l -E "Traceback|OutOfMemoryError|CUDA out of memory" $W/logs/train_*.log $W/logs/gen/*.log $W/logs/battery_*.log $W/logs/judge_daemon.log 2>/dev/null | grep -q . && A="$A error-in-log:$(grep -l -E 'Traceback|OutOfMemoryError|CUDA out of memory' $W/logs/train_*.log $W/logs/gen/*.log $W/logs/battery_*.log $W/logs/judge_daemon.log 2>/dev/null | tr '\n' ',')"
  grep -q "SPEND CAP" $W/logs/judge_daemon.log 2>/dev/null && A="$A spend-cap"
  SESS=$(tmux ls 2>/dev/null | cut -d: -f1 | sort | tr '\n' ' ')
  [ "$SESS" != "$SESS0" ] && A="$A tmux-changed:[$SESS0]->[$SESS]"
  S=$(snap); [ "$S" != "$S0" ] && A="$A milestone"
  if [ -n "$A" ]; then echo "$(date -u +%T) WATCH: $A"; bash $W/code/st.sh 2>&1 | grep -v '^tmux'; exit 0; fi
done
echo "$(date -u +%T) WATCH: quiet for $MAXMIN min"; bash $W/code/st.sh 2>&1 | grep -v '^tmux'
