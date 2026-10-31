#!/bin/bash
# sw037 judging + report (box 1, system python3; run agent, E2). Usage: bash judge37.sh <tag> <parts>   e.g.  p1fbtw p1:fbtw
# pull -> analyze37 prep (complete manifest or exit 2) -> judge_run reply5, both judges, seeded 20 % per cell + every STRICT/lexicon
# disagreement (E2 key, spend tagged sw037) -> report (all judged files so far).
set -euo pipefail
TAG=$1; PARTS=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/037_routing_variable_noflip_runs/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
D=/workspace/runs_executor/sw037; mkdir -p $D/judge
rsync -a -e "ssh -o BatchMode=yes -p <port> -i /root/.ssh/id_ed25519" root@<box-ip>:/root/runs/sw037/ $D/
cd "$SRC"
/usr/bin/python3 analyze37.py prep --stage full --parts $PARTS --run_dir $D/full --out $D/judge/judgein_$TAG.jsonl ${PREP_EXTRA:-}
/usr/bin/python3 $LIB/judge_run.py --exp sw037 --rubric reply5 --in $D/judge/judgein_$TAG.jsonl --out $D/judge/judged_$TAG.jsonl --sample-frac ${FRAC:-0.2} \
  --strata-field cell --always-field always --seed 37 --part $TAG ${JUDGE_EXTRA:-}
echo JUDGED_$TAG
