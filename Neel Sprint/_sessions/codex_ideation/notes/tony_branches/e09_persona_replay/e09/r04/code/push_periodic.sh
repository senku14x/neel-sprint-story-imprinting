#!/bin/bash
# push every 25 minutes (brief: at least every 30 minutes)
while true; do sleep 1500; bash /workspace/e09/r04/code/push.sh "E09 R04: periodic push" >> /workspace/e09/r04/logs/push_periodic.log 2>&1; done
