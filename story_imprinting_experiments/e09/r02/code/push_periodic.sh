#!/bin/bash
# push every 25 minutes (brief: at least every 30 minutes)
while true; do sleep 1500; bash /workspace/e09/r02/code/push.sh "E09 R02: periodic push" >> /workspace/e09/r02/logs/push_periodic.log 2>&1; done
