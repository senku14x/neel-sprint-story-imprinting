#!/bin/bash
# sw043 hd eval post on box 1: pull the node's eval OUT (without the remapped LoRAs), E4's post61.sh unedited (exp sw043, cap $CAP shared
# with every sw043 judging), then for red_A the post-hoc known-answer gate (043 D13).   bash post_hd.sh red_A|red_B
set -uo pipefail
R=${1:?run}; CAP=${CAP:-6}
D=/workspace/runs_executor/sw043/eval/$R; S="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src"
mkdir -p $D
rsync -a -e "ssh -i /root/.ssh/id_ed25519 -p <port>" --exclude lora_vllm root@<node-ip>:/root/runs/sw043/eval/$R/ $D/ || exit 2
test -e $D/GPU_DONE || { echo "no GPU_DONE in $D"; exit 3; }
L=$(python3 -I "$S/redirect/keylim.py" | python3 -c "import json,sys; print(json.load(sys.stdin)['limit_remaining'])"); echo "key limit_remaining $L"
python3 -c "import sys; sys.exit(0 if float('$L') >= 40 else 1)" || { echo "KEY_BELOW_40 $L"; exit 4; }
if [ "$R" = red_A ]; then python3 -I "$S/eval_specs/known_answer_posthoc.py" "$S/eval_specs/red_A.json" $D; echo "posthoc KA rc=$?"; fi
bash "$S/e4/post61.sh" $D sw043 $CAP > $D/post.log 2>&1; echo "post61 rc=$?"
tail -3 $D/post.log
