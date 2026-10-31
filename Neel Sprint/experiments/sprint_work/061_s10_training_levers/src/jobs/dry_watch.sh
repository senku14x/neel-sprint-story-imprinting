#!/bin/bash
# sw061 G1 (agent B): two-phase release from the CPU dry run (dry_g1.py). Times from date -u.
#  phase 1 -> g1/CPU_TESTS_PASS (job 80's DEPS): test_g1_results.json all-pass and the dry run's fit stage finished with rc 0 and
#             wrote g1_S_B / g1_N_B / g1_K0_B.
#  phase 2 -> g1/DRY_GATE0_OK (job 81's DEPS): Gate 0's inference stage ran to its verdict (rc 0, or 3 = a gate the mock cannot
#             pass; gate0_inf.json written), the smoke check gave the expected verdict on fabricated logs, drift rc 0.
#  Any failure -> g1/DRY_FAILED with the reason (the marker of that phase is not written).
#   setsid nohup bash dry_watch.sh DRY_DIR LOG > ... &
set -u
DRY=${1:?dry dir}; LOG=${2:?dry log}
RAW=/workspace/runs_executor/sw061/g1
SRC="/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src"
fail() { echo "$(date -u +%FT%TZ) $*" > "$RAW/DRY_FAILED"; echo "DRY_FAILED $*"; exit 1; }
until grep -qE "DRY fit_gpu|Traceback|^rc=" "$LOG"; do sleep 15; done
sleep 2
grep -q "Traceback" "$LOG" && fail "traceback in the fit stage: $(grep -m1 -A0 'Error' "$LOG" | cut -c1-300)"
python3 -c "import json,sys; sys.exit(0 if json.load(open('$SRC/test_g1_results.json'))['_meta']['ok'] else 1)" || fail "CPU tests not all pass"
grep -q "DRY fit_gpu {'rc': 0" "$LOG" || fail "fit stage: $(grep -m1 'DRY fit_gpu' "$LOG" | cut -c1-200)"
for k in S N K0; do [ -e "$DRY/g1_${k}_B.pt" ] || fail "no g1_${k}_B.pt"; done
echo "$(date -u +%FT%TZ) test_g1 25/25 + dry_g1 fit stage clean ($(grep -m1 'DRY fit_gpu' "$LOG"))" > "$RAW/CPU_TESTS_PASS"; echo "CPU_TESTS_PASS"
until grep -qE "DRY_DONE|Traceback|^rc=" "$LOG"; do sleep 15; done
sleep 5
python3 - "$DRY" "$LOG" "$RAW" <<'PY'
import json, os, sys, time
dry, log, raw = sys.argv[1:4]
why = []
if "Traceback" in open(log).read():
    why.append("traceback after the fit stage")
r = json.load(open(f"{dry}/dry_result.json")) if os.path.exists(f"{dry}/dry_result.json") else None
if r is None:
    why.append("no dry_result.json")
else:
    if r.get("gate0_inf", {}).get("rc") not in (0, 3) or not os.path.exists(f"{dry}/gate0_inf.json"):
        why.append(f"gate0 inference {r.get('gate0_inf')}")
    sc = r.get("smoke_check", {})
    exp = "PLUMBING_OK_SN_OUTSIDE_ENVELOPE" if sc.get("inf_pass_marker") else "FAIL"
    if sc.get("verdict") != exp:
        why.append(f"smoke check {sc}")
    if r.get("drift", {}).get("rc") != 0:
        why.append(f"drift {r.get('drift')}")
now = time.strftime("%FT%TZ", time.gmtime())
if why:
    open(f"{raw}/DRY_FAILED", "w").write(now + " " + "; ".join(why) + "\n"); print("DRY_FAILED", why)
else:
    open(f"{raw}/DRY_GATE0_OK", "w").write(now + " dry_g1 Gate 0 / smoke check / drift clean (" + json.dumps(r) + ")\n"); print("DRY_GATE0_OK")
PY
