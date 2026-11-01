#!/usr/bin/env bash
# E04 R03 step 5c (R02's cheap_checks.sh; tag, sizes, port and log made arguments so the smoke test can use it):
# E01's single-turn eval (Table 13 prompts, N replies per prompt with and without the prohibition) and story check
# (N stories in the training format), plain T=1, GLM judge, against the server on <port>. Exit codes are now captured before
# the log line (R02's line read $? after $(date), so it always logged 0).
#   bash cheap_checks.sh [model_tag=hc_db_a5b_r03_s250] [single_turn_n=50] [story_n=50] [port=8010]
set -uo pipefail
R03=/workspace/e04/r03; LOG=${LOG:-$R03/logs/step8.log}
TAG=${1:-hc_db_a5b_r03_s250}; STN=${2:-50}; SCN=${3:-50}; PORT=${4:-8010}
source $R03/bloom_code/env.sh
export SI36_API_CAP_USD=${SI36_API_CAP_USD:?}
cd $R03/bloom_code
echo "$(date -u +%FT%TZ) single-turn start ($TAG, n $STN per prompt and condition)" >> $LOG
/workspace/venvs/bloom/bin/python single_turn.py --model-tag $TAG --sampling T1 --n $STN --base-url http://localhost:$PORT/v1 > $(dirname $LOG)/single_turn_$TAG.log 2>&1
RC=$?; echo "$(date -u +%FT%TZ) single-turn exit $RC" >> $LOG
echo "$(date -u +%FT%TZ) story check start ($TAG, $SCN stories)" >> $LOG
/workspace/venvs/bloom/bin/python story_check.py --model-tag $TAG --sampling T1 --n $SCN --base-url http://localhost:$PORT/v1 > $(dirname $LOG)/story_check_$TAG.log 2>&1
RC=$?; echo "$(date -u +%FT%TZ) story check exit $RC" >> $LOG
