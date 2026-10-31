#!/bin/bash
# BOX 1: push sw039 Part 1 code (src/p1 only: no data, no keys, no judge files) to the same path on the node, then list it.
set -euo pipefail
S="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p1"
E="ssh -p <NODE_PORT> -i /root/.ssh/id_ed25519 -o BatchMode=yes"
$E root@<NODE_IP> "mkdir -p '$S' /root/runs/sw039/p1/logs /root/caps/sw039"
rsync -a --exclude __pycache__ --include '*/' --include '*.py' --include '*.sh' --exclude '*' -e "$E" "$S/" "root@<NODE_IP>:$S/"
$E root@<NODE_IP> "cd '$S' && sha256sum *.py jobs/*.sh" 
