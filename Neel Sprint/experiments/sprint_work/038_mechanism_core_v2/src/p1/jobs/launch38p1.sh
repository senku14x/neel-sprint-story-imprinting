#!/bin/bash
# sw038 Part 1 detached launcher (prep-P1 agent): bash launch38p1.sh <log> <script> [args...] -> prints the detached bash PID.
# setsid + nohup + all three fds redirected, so the ssh session that calls it returns at once (mistakes 31 Oct 07:04).
LOG=$1; shift
setsid nohup bash "$@" > "$LOG" 2>&1 < /dev/null &
echo $!
