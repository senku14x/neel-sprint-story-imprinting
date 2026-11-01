#!/usr/bin/env bash
# E04 R02 step 8c: E01's single-turn eval (Table 13 prompts, 50 replies per prompt with and without the prohibition) and story check
# (50 stories in the training format), plain T=1, GLM judge, against the a5b step-250 server on port 8010.
set -uo pipefail
R02=/workspace/e04/r02; LOG=$R02/logs/step8.log
source $R02/bloom_code/env.sh
export SI36_API_CAP_USD=${SI36_API_CAP_USD:-31.5}
cd $R02/bloom_code
echo "$(date -u +%FT%TZ) single-turn start" >> $LOG
/workspace/venvs/bloom/bin/python single_turn.py --model-tag hc_db_a5b_r02_s250 --sampling T1 --n 50 --base-url http://localhost:8010/v1 > $R02/logs/bloom/single_turn.log 2>&1
echo "$(date -u +%FT%TZ) single-turn exit $?" >> $LOG
/workspace/venvs/bloom/bin/python story_check.py --model-tag hc_db_a5b_r02_s250 --sampling T1 --n 50 --base-url http://localhost:8010/v1 > $R02/logs/bloom/story_check.log 2>&1
echo "$(date -u +%FT%TZ) story check exit $?" >> $LOG
