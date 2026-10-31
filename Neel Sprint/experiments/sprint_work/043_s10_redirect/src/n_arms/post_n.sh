#!/bin/bash
# sw043 N arms, box 1 post: pull the node's n_eval, judge (judge_guard61, exp sw043, cap $CAP shared with every sw043 judging), analyse.
#   bash post_n.sh [stages: pull,t1,p0,enact,health,rule]
set -uo pipefail
STAGES=${1:-pull,t1,p0,enact,health,rule}; CAP=${CAP:-6}
G=/workspace/runs_executor/sw043/n_eval; A="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/n_arms/an43_n.py"
K="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/e4/keep"; W="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src/redirect"
T40="/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/premise/judge40_template.txt"
has() { [[ ",$STAGES," == *",$1,"* ]]; }
lim() { python3 -I "$W/keylim.py" | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])"; }
check() { L=$(lim); echo "[$(date -u +%FT%TZ)] key limit_remaining $L before $1"; python3 -c "import sys; sys.exit(0 if float('$L') >= 40 else 1)" || { echo "KEY_BELOW_40 $L"; exit 3; }; }
J() { python3 "$K/judge_guard61.py" --exp sw043 --cap $CAP "$@"; }
mkdir -p $G
if has pull; then rsync -a -e "ssh -i /root/.ssh/id_ed25519 -p <port>" --exclude 'adapters_vllm' root@<node-ip>:/root/runs/sw043/n_eval/ $G/ || exit 2; fi
if has t1; then
  python3 -I "$A" t1_judgein $G || exit 4; check t1
  J --rubric custom --template "$T40" --fields decline,register --ranges decline:0-10,register:0-3 --in $G/t1/judgein_t1.jsonl --out $G/t1/judged_t1.jsonl --part n_t1 || exit 5
  python3 -I "$A" t1_report $G || exit 6
fi
if has p0; then
  python3 -I "$A" p0_prep $G || exit 7; check p0
  J --rubric habit --sample-frac 0.2 --strata-field stratum --always-field disagree --seed 0 --in $G/p0/judgein_habit.jsonl --out $G/p0/judged_habit.jsonl --part n_p0 || exit 8
  python3 -I "$A" p0_widen $G || exit 9
  if [ -s $G/p0/judgein_habit_all.jsonl ]; then check p0_all; J --rubric habit --in $G/p0/judgein_habit_all.jsonl --out $G/p0/judged_habit_all.jsonl --part n_p0all || exit 10; fi
  python3 -I "$A" p0_report $G || exit 11
fi
has enact && { python3 -I "$A" enact_report $G || exit 12; }
has health && { python3 -I "$A" health_report $G > $G/health/health_report.txt || exit 13; }
has rule && { python3 -I "$A" rule $G || exit 14; }
echo "POST_N_DONE $(date -u +%FT%TZ)"
