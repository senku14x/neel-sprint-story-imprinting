#!/bin/bash
export API_LEDGER=/workspace/e05/logs/api_ledger.jsonl
export API_CAP_USD=7.5
export E05_RATE_PER_MIN=19.5
export E05_JUDGE_CONC=24
cd /workspace/e05
exec /workspace/venvs/gpu/bin/python /workspace/e05/driver/e05_judge.py
