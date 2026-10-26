#!/bin/bash
until [ -f /root/runs/train_gate ]; do sleep 30; done
mv /root/runs/vq_later/*.json /root/runs/vq/ && echo "requeued min-p jobs $(date)"
