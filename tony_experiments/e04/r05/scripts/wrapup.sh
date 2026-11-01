#!/usr/bin/env bash
# E04 R05 (new): rebuild every table and the README from what exists, then push. Safe to rerun.
set -uo pipefail
R=/workspace/e04/r05; cd $R
/workspace/e03/venvs/api/bin/python -I scripts/key_usage.py wrapup > /dev/null
( source bloom_code/env.sh; cd bloom_code; /workspace/venvs/bloom/bin/python analyze.py > $R/logs/e01_analyze.log 2>&1 ) || echo "E01 analyze.py failed"
/workspace/venvs/bloom/bin/python -I scripts/bloom_ledger.py > /dev/null 2>&1 || echo "bloom_ledger failed"
/workspace/e03/venvs/si/bin/python -I scripts/evals_r05.py > /dev/null 2> logs/evals_err.txt || echo "evals_r05 failed"
/workspace/e03/venvs/si/bin/python -I scripts/exclusions.py > /dev/null || echo "exclusions failed"
/workspace/venvs/gpu/bin/python -I scripts/spend.py > /dev/null || echo "spend failed"
/workspace/venvs/gpu/bin/python -I scripts/gputime.py > /dev/null || echo "gputime failed"
/workspace/venvs/gpu/bin/python -I scripts/pacing_report.py > /dev/null || echo "pacing_report failed"
/workspace/venvs/gpu/bin/python -I scripts/finalize_status.py > /dev/null || echo "finalize_status failed"
(diff -ruN -x __pycache__ notes/r03_code_orig/scripts scripts; diff -ruN -x __pycache__ notes/r03_code_orig/bloom_code bloom_code) > results/code_changes.diff
/workspace/venvs/gpu/bin/python -I scripts/make_readme.py
/workspace/venvs/gpu/bin/python -I scripts/status.py --set "stage=${1:-wrap-up}" --set "next=${2:-final push}" > /dev/null
bash scripts/push.sh "E04 R05: ${1:-wrap-up}" 2>&1 | tail -2
