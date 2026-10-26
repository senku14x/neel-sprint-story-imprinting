until grep -q "'step': 2\|Error\|Traceback" /root/runs/probe_A.log; do sleep 5; done
tail -c 1200 /root/runs/probe_A.log
