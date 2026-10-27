#!/bin/bash
# once box 3's environments + parent + inputs are in place, stop the setup before it pushes the 55 GB checkpoints
until grep -q SETUP_DONE /root/runs/explore1026/box3_setup.log; do sleep 10; done
pkill -P $(pgrep -f "^/bin/bash /root/runs/explore1026/box3_setup.sh" | head -1) 2>/dev/null
kill $(pgrep -f "^/bin/bash /root/runs/explore1026/box3_setup.sh" | head -1) 2>/dev/null
ssh -o BatchMode=yes -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18 'pkill -f "tar -C /root/runs/merged" ; pkill -f "tar -C /root/merged_sw001"; rm -rf /root/runs/merged/*.partial /root/merged_sw001/*.partial; ls /root/runs/merged /root/merged_sw001'
echo "TRIMMED $(date -u +%H:%M:%S)"
