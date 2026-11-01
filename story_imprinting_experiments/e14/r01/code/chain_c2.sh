#!/bin/bash
# Part C second-sample pass (s1) after the first pass exits cleanly.
cd /workspace/e14/r01
until grep -q "^EXIT" logs/partC.log; do sleep 10; done
if grep -q "PARTC_EXIT" logs/partC.log && grep -q "^EXIT 0" logs/partC.log; then
  echo "$(date -u +%T) starting Part C s1 pass" >> logs/chain_c.log
  HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false /workspace/venvs/gpu/bin/python -I code/oracle.py run --extra 1 > logs/partC_s1.log 2>&1
  echo "EXIT $?" >> logs/partC_s1.log
else
  echo "$(date -u +%T) Part C first pass did not exit cleanly; s1 pass not started" >> logs/chain_c.log
fi
