#!/bin/bash
# sw029 Part B prep on one GPU (prep agent, E2): captures (all 4 e08 organisms, one process) -> directions (CPU) -> smoke
# (2 pairs x 1 sample per organism, induce + donor none, free + fbtw + fraf, inline gates) -> output gates + calib_b.json.
#   nohup bash prepb29.sh <gpu> > /root/runs/sw029/logs/prepb29.wrap 2>&1 < /dev/null &
set -uo pipefail
GPU=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/029_leakage_free_directions/src"; RUN=/root/runs/sw029
bash "$SRC/jobs/run_node.sh" capb $GPU cap29b_x.py || { echo "capture failed"; exit 3; }
cd "$SRC" && OMP_NUM_THREADS=16 taskset -c 0-55,112-167 /root/venvs/si/bin/python dirs29b_x.py > $RUN/logs/dirs29b.log 2>&1 || { echo "dirs failed"; exit 4; }
bash "$SRC/jobs/run_node.sh" smokeb $GPU gen29b_x.py --models e08-X,e08-XB,e08-N,e08-NB --readout free,fbtw,fraf --pairs 2 --samples 1 --gates \
  --run_dir $RUN/smoke_b --batch_rows 46 --forced_batch_rows 69 || { echo "smoke failed"; exit 5; }
ok=1
for m in e08-X e08-XB e08-N e08-NB; do
  OMP_NUM_THREADS=4 /root/venvs/si/bin/python check29b.py $RUN/smoke_b --model $m --readouts free,fbtw,fraf --pairs 2 --samples 1 \
    --out $RUN/smoke_b/output_gates_$m.json --write_calib $RUN/smoke_b/calib_$m.json >> $RUN/logs/smokeb_check.log 2>&1 || ok=0
done
[ $ok = 1 ] || { echo "smoke output gates failed"; exit 6; }
/root/venvs/si/bin/python - <<'PY'
import json, glob
C = [json.load(open(p)) for p in sorted(glob.glob("/root/runs/sw029/smoke_b/calib_e08-*.json"))]
meas = {k: max(c["measured"][k] for c in C) for k in C[0]["measured"]}; full = {k: max(c["tol_full"][k] for c in C) for k in C[0]["tol_full"]}
json.dump(dict(measured=meas, tol_full=full, rule="max(sw028's calibrated value, 3 x the Part B smoke's measured worst)"), open("/root/runs/sw029/calib_b.json", "w"), indent=1)
print("CALIB_B", meas, full)
PY
touch $RUN/smoke_b/SMOKE_B_GATES_OK; echo SMOKE_B_GATES_OK
