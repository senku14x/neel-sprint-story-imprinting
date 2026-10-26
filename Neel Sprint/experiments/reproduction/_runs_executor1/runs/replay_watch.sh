#!/bin/bash
until [ -f /root/runs/vq/done/000_parent_single.json ] && [ -f /root/runs/vq/done/005_parent_single_ext.json ]; do sleep 30; done
cd "/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src" && python3 make_replay_rows.py /root/runs/parent_gen/parent_T1.jsonl > /root/runs/replay_rows.log 2>&1
echo "replay rows built $(date)" >> /root/runs/replay_rows.log
