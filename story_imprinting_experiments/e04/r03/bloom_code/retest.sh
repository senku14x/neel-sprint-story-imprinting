#!/usr/bin/env bash
# Amendment 2 auditor retest: 20 untrained-model conversations with GPT-4.1-mini and 10 with GPT-4.1,
# target max_tokens 1024 (common.EVAL_MAX_TOKENS), plain T=1, no system prompt, base served on port 8010.
set -uo pipefail
source /workspace/repo/replicate_qwen27B/env.sh
cd "$SI36_CODE"
PY=/workspace/venvs/bloom/bin/python
until curl -sf localhost:8010/v1/models 2>/dev/null | grep -q "\"target\""; do sleep 15; done
echo "STEP $(date -u +%T) base ready; retest starts"
$PY -c "from llm import key_usage; print('spend before retest', key_usage())"
INSPECT_DISPLAY=plain $PY bloom_eval.py --tag auditortest2_mini_base__T1__none --model-tag base --sampling T1 \
  --n-per-scenario 4 --auditor openai/gpt-4.1-mini --base-url http://localhost:8010/v1 --max-samples 20 \
  > /workspace/logs/bloom_auditortest2_mini.log 2>&1 &
INSPECT_DISPLAY=plain $PY bloom_eval.py --tag auditortest2_gpt41_base__T1__none --model-tag base --sampling T1 \
  --n-per-scenario 2 --auditor openai/gpt-4.1 --base-url http://localhost:8010/v1 --max-samples 10 \
  > /workspace/logs/bloom_auditortest2_gpt41.log 2>&1 &
wait
echo "STEP $(date -u +%T) bloom done; compliance"
for t in auditortest2_mini_base__T1__none auditortest2_gpt41_base__T1__none; do $PY compliance.py --tag $t; $PY garble.py --tag $t; done
$PY -c "from llm import key_usage; print('spend after retest', key_usage())"
echo "RETEST DONE $(date -u +%T)"
