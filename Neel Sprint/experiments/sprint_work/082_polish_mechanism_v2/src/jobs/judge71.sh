#!/bin/bash
# sw071 judging + report (box 1, system python3; prep-71). Usage: bash judge71.sh <run_dir_on_box1>
# prep (every row of fbtw / fo / co / free + parent floor; always = STRICT/lexicon disagreement or a free sample-0 row) -> judge_run reply5,
# both judges, seeded 20 % per cell + every 'always' row -> report (frozen rules). If agreement < 0.95 in a (readout, model), every row of
# that model's readout is judged (judged_all.jsonl) within the sw071 spend cap, and the report is rerun.
set -euo pipefail
D=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/082_polish_mechanism_v2/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
CAP=${SW071_CAP:-5.0}
cd "$SRC"
/usr/bin/python3 analyze71.py prep $D --stage full
/usr/bin/python3 $LIB/judge_run.py --exp sw071 --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 \
  --strata-field cell --always-field always --seed 71 --part full --models both --concurrency 48
/usr/bin/python3 analyze71.py report $D --base $D/base/base_gates.json --stage full > $D/report71.txt 2>&1
NEED=$(/usr/bin/python3 -c "import json; print(' '.join(json.load(open('$D/analysis/results71.json'))['judge_all_needed']))")
if [ -n "$NEED" ]; then
  SPENT=$(/usr/bin/python3 -c "
import json; s=0.0
for l in open('/workspace/runs_executor/day_2026-10-31_E2/spend.jsonl'):
    try: r=json.loads(l)
    except Exception: continue
    if r.get('exp')=='sw071': s+=float(r.get('cost', r.get('spend', 0)) or 0)
print(round(s,3))")
  echo "judge_all_needed: $NEED (sw071 spend so far \$$SPENT, cap \$$CAP)"
  /usr/bin/python3 - "$D" $NEED <<'PY'
import json, sys
d, need = sys.argv[1], set(sys.argv[2:])
rows = [json.loads(l) for l in open(f"{d}/judgein.jsonl")]
sel = [r for r in rows if f"{r['readout']}|{r['model']}" in need]
open(f"{d}/judgein_all.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in sel)); print("judge-all rows", len(sel))
PY
  if /usr/bin/python3 -c "import sys; sys.exit(0 if float('$SPENT') < float('$CAP') - 1.0 else 1)"; then
    /usr/bin/python3 $LIB/judge_run.py --exp sw071 --rubric reply5 --in $D/judgein_all.jsonl --out $D/judged_all.jsonl --part full_all --models both --concurrency 48
    /usr/bin/python3 analyze71.py report $D --base $D/base/base_gates.json --stage full > $D/report71.txt 2>&1
  else
    echo "JUDGE_ALL_SKIPPED_CAP" | tee $D/JUDGE_ALL_SKIPPED_CAP
  fi
fi
echo "JUDGE71_DONE $(date -u +%T)"
