#!/bin/bash
until grep -q TRIMMED /root/runs/explore1026/box3_trim.log; do sleep 30; done
echo "trimmed seen $(date -u +%H:%M:%S)"
ssh -o BatchMode=yes -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18 'nohup bash "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_Bs1/box3_job.sh" > "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_Bs1/out/driver.log" 2>&1 < /dev/null &'
echo launched
