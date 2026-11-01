#!/usr/bin/env bash
# E04 R05 step 3c (R03's cheap_checks.sh; R05 change: the two checks run at the same time, so both save their replies while the
# server is up; their GLM judging is paced by scripts/api_pacer.py at GLM_PRIORITY from the caller, 7 in the real run):
# E01's single-turn eval (Table 13 prompts, N replies per prompt with and without the prohibition) and story check
# (N stories in the training format), plain T=1, GLM judge, against the server on <port>.
#   bash cheap_checks.sh [model_tag] [single_turn_n=50] [story_n=50] [port=8010]
set -uo pipefail
R05=/workspace/e04/r05; LOG=${LOG:-$R05/logs/r05.log}
TAG=${1:?model tag}; STN=${2:-50}; SCN=${3:-50}; PORT=${4:-8010}
source $R05/bloom_code/env.sh
export SI36_API_CAP_USD=${SI36_API_CAP_USD:?}
cd $R05/bloom_code
echo "$(date -u +%FT%TZ) single-turn start ($TAG, n $STN per prompt and condition)" >> $LOG
( /workspace/venvs/bloom/bin/python single_turn.py --model-tag $TAG --sampling T1 --n $STN --base-url http://localhost:$PORT/v1 > $(dirname $LOG)/single_turn_$TAG.log 2>&1
  RC=$?; echo "$(date -u +%FT%TZ) single-turn $TAG exit $RC" >> $LOG ) &
echo "$(date -u +%FT%TZ) story check start ($TAG, $SCN stories)" >> $LOG
( /workspace/venvs/bloom/bin/python story_check.py --model-tag $TAG --sampling T1 --n $SCN --base-url http://localhost:$PORT/v1 > $(dirname $LOG)/story_check_$TAG.log 2>&1
  RC=$?; echo "$(date -u +%FT%TZ) story check $TAG exit $RC" >> $LOG ) &
wait
