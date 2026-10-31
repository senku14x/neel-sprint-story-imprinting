#!/bin/bash
# sw045 box-1 post for one eval (C6 second line: E4's post61.sh unedited). E3 agent, 31 Oct 2026.
#   bash post45.sh <g2_A|g2_B>
# 1 pull the node eval dir + verify45 (hash gate); 2 refuse unless the box-1 sw061 src (post61.sh's hard-coded SRC) still equals the
# handoff sha256s; 3 key check (user 16:05 via E3: $40 stop lifted; hard stop < $5 or a 402): cap = min($5, remaining - $5),
#   refuse if cap < $1; prints BELOW_40 when remaining < $40 (E3 wants a note the first time);
# 4 post61.sh <dir> sw045 <cap> (labels, two judges 20% + disagreements, judge-all < 0.95, conduct, garble, analysis61 --lever g2).
set -u
RN=$1
RUN="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run"; E4="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/e4"
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"; D=/workspace/runs_executor/sw045/eval/$RN
echo "post45 $RN start $(date -u +%FT%TZ)"
bash "$RUN/pull45.sh" eval/$RN verify || { echo "REFUSE: pull / verify failed"; exit 3; }
[ -e $D/GPU_DONE ] || { echo "REFUSE: no GPU_DONE"; exit 3; }
(cd "$SRC" && sha256sum -c "$E4/SHA256SUMS_handoff" --quiet) || { echo "REFUSE: box-1 sw061 src differs from the handoff"; exit 3; }
REM=$(python3 -I "$RUN/keylim45.py" | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])")
CAP=$(python3 -c "r=float('$REM'); print(round(min(5.0, r - 5.0), 2))")
echo "key limit_remaining \$$REM -> sw045 cap \$$CAP"
python3 -c "import sys; sys.exit(0 if float('$REM') < 40 else 1)" && echo "BELOW_40 remaining \$$REM"
python3 -c "import sys; sys.exit(0 if float('$CAP') >= 1.0 else 1)" || { echo "REFUSE: key too close to the \$5 hard stop (remaining \$$REM)"; exit 5; }
bash "$SRC/post61.sh" "$D" sw045 "$CAP"; rc=$?
REM2=$(python3 -I "$RUN/keylim45.py" | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])")
echo "post61 rc=$rc; key limit_remaining \$$REM -> \$$REM2 $(date -u +%FT%TZ)"
exit $rc
