#!/bin/bash
# E08 R07 measure 3: the teammate's GLM + DeepSeek judges through judge.py (unchanged) as E04 R05 ran them (run_judge_paced.py,
# run-wide pacer at 18 requests a minute per model, --concurrency 32), on N and NB x (default, P06) at T 0.7 (800 conversations).
# Up to 5 passes (judge.py retries error rows on the next invocation). Spend cap $5 (API_CAP_USD on llm.py's ledger).
set -u
W=/workspace/e08/r07
IN=$W/results/or_input_N_NB_T07.jsonl; OUT=$W/judgments/or_N_NB_T07_judgments.jsonl
/workspace/venvs/gpu/bin/python -I - <<PY
import json
rows = [json.loads(l) for l in open("$W/results/rollouts/G1_T07_Nfam_parent.jsonl")]
sel = [r for r in rows if r["model"] in ("N", "NB") and r["persona"] in ("default", "P06")]
open("$IN", "w").write("".join(json.dumps(r) + "\n" for r in sel))
print(len(sel), "conversations for the teammate's judges")
PY
export API_LEDGER=$W/logs/ledger_openrouter_judge.jsonl API_CAP_USD=5 GLM_PRIORITY=5 PACER_TAG=teammate_judge:N_NB_T07
for pass in 1 2 3 4 5; do
  echo "$(date -u +%FT%TZ) OR judge pass $pass start" >> $W/logs/run.log
  /workspace/venvs/gpu/bin/python -I $W/scripts/run_judge_paced.py $IN $OUT --concurrency 32 >> $W/logs/judge_or.log 2>&1
  n=$(/workspace/venvs/gpu/bin/python -I -c "
import json; ok={(r['key'],r['judge']) for r in map(json.loads, open('$OUT')) if not r.get('error')}; print(len(ok))")
  echo "$(date -u +%FT%TZ) OR judge pass $pass done: $n of 1600 judge rows ok" >> $W/logs/run.log
  [ "$n" -ge 1600 ] && break
done
