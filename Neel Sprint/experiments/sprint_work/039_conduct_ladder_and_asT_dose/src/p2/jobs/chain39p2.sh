#!/bin/bash
# sw039 Part 2 unattended chain for ONE model on ONE GPU (prep-D agent, E2, 31 Oct 2026). Run ON THE NODE (via wait_gpu_then.sh):
#   bash chain39p2.sh <model> <gpu>
# 1. calibration (gen39p2 --cal; prefill only, all 61 scripts, both directions, every dose's 2 A arms; sw038 D14's two-segment rule)
#    -> freeze_scales39p2 refuses unless the 61-script verify has every A arm in [0.9, 1.1] at both bands -> cal/scales39p2_<m>.json
# 2. smoke (part p2smoke, never in a full manifest): G1 + KA alpha = 1 vs sw038 + G3 gates; memory probe at the full batch on the
#    LONGEST contexts with every row forced to the cap (free induce 3 units = 48 rows to 2,048; forced 4 units = 64 rows); the 4 sw038
#    smoke scripts x both directions x 16 arms x 1 sample, free + fbtw; check39p2 (rows, keys, non-empty, logs, known answers, none-arm
#    sanity; cumulative medians reported) + calib39p2_<m>.json (tolerances); decide_batch39p2 -> smoke/batch_<m>.json; SMOKE_OK_<m>.
# 3. full run (part p2): gates again, free induce (2 samples) -> fbtw induce -> free remove (1) -> fbtw remove; check39p2 on the full
#    EXPECTED manifest incl. the [0.9, 1.1] cumulative gate on all 61 scripts -> /root/runs/sw039/p2/GPU_DONE_p2_<m>.
# Any failure: /root/runs/sw039/p2/FAILED_p2_<m> (time + reason) and exit 1; nothing later runs. Resumable: rerun the same command
# (frozen scales and SMOKE_OK are reused; generation resumes by key). CHAIN_EXIT_p2_<m> is always written.
set -uo pipefail
M=$1; GPU=$2
SRC="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/src/p2"
RUN=/root/runs/sw039/p2; CAL=$RUN/cal; SM=$RUN/smoke; FULL=$RUN/full; J="$SRC/jobs/run_node39p2.sh"
mkdir -p $CAL $SM $FULL $RUN/logs
SOCK="56-111,168-223"; [ "$GPU" = "3" ] || SOCK="0-55,112-167"; export CPUSOCK=$SOCK
echo "$$ $(date -u +%FT%TZ) gpu=$GPU" > $RUN/PID_chain_$M
fin() { echo "{\"model\": \"$M\", \"gpu\": $GPU, \"status\": \"$1\", \"end\": \"$(date -u +%FT%TZ)\"}" > $RUN/CHAIN_EXIT_p2_$M; }
fail() { echo "$(date -u +%FT%TZ) $*" > $RUN/FAILED_p2_$M; echo "FAILED_p2_$M: $*"; fin failed; exit 1; }
[ -e $RUN/GPU_DONE_p2_$M ] && { echo "GPU_DONE_p2_$M exists"; fin done; exit 0; }
rm -f $RUN/FAILED_p2_$M
for f in /root/runs/sw038/p1/inputs/contexts38p1.jsonl /root/runs/sw038/p1/dirs/dirs38p1_$M.pt /root/caps/sw038p1/cap_$M.pt \
         /root/runs/sw038/p1/calib.json /root/runs/sw038/p1/smoke/smoke_sids.json \
         "/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1/scales38p1.json"; do
  [ -e "$f" ] || fail "missing input $f"
done
S4=$(/root/venvs/si/bin/python -c "import json; print(','.join(json.load(open('/root/runs/sw038/p1/smoke/smoke_sids.json'))))")
GS=$(/root/venvs/si/bin/python -c "import json; print(','.join(json.load(open('/root/runs/sw038/p1/smoke/smoke_sids.json'))[:2]))")
SC=$CAL/scales39p2_$M.json
echo "$(date -u +%FT%TZ) chain start $M gpu $GPU"
# ---- 1. calibration + freeze
if [ ! -e $SC ]; then
  bash "$J" cal_$M $GPU gen39p2.py --model $M --cal $CAL --run_dir $CAL --job cal_$M || fail "calibration failed rc=$? (logs/cal_$M.log; CAL_VERIFY_FAILED = some dose's A arm outside [0.9, 1.1] on the 61-script verify)"
  bash "$J" freeze_$M cpu freeze_scales39p2.py $CAL $M $SC || fail "freeze refused rc=$? (logs/freeze_$M.log)"
fi
echo "$(date -u +%FT%TZ) scales frozen $(sha256sum $SC)"
# ---- 2. smoke
if [ ! -e $SM/SMOKE_OK_$M ]; then
  bash "$J" smoke_$M $GPU gen39p2.py --model $M --order free:induce,free:remove,fbtw:induce,fbtw:remove --sids $S4 --samples 1 --part p2smoke \
    --gates --gate_sids $GS --mem_probe "free|induce:3;fbtw|induce:4" --run_dir $SM --gates_out $SM/gates_$M --scales $SC \
    --batch_units 3 --forced_batch_units 4 --job smoke_$M || fail "smoke gen failed rc=$? (logs/smoke_$M.log; GATES_FAILED = G1 / KA alpha=1 / G3)"
  bash "$J" smokecheck_$M cpu check39p2.py $SM --model $M --directions induce,remove --readouts free,fbtw --sids $S4 --samples 1 --part p2smoke \
    --gates_json $SM/gates_$M/gates_$M.json --scales $SC --cum_report_only --smoke_sanity --out $SM/output_gates_$M.json \
    --write_calib $SM/calib39p2_$M.json || fail "smoke output gates failed rc=$? (logs/smokecheck_$M.log)"
  bash "$J" batch_$M cpu decide_batch39p2.py $SM/gates_$M/mem_probe_$M.json $SM/batch_$M.json || fail "batch decision failed rc=$?"
  touch $SM/SMOKE_OK_$M
fi
echo "$(date -u +%FT%TZ) smoke ok; batch $(cat $SM/batch_$M.json | head -3 | tr -d '\n ')"
# ---- 3. full run
bash "$J" full_$M $GPU gen39p2.py --model $M --order free:induce,fbtw:induce,free:remove,fbtw:remove --part p2 --gates --gate_sids $GS \
  --run_dir $FULL --gates_out $FULL/gates_$M --calib $SM/calib39p2_$M.json --scales $SC --batch_json $SM/batch_$M.json --job full_$M \
  || fail "full gen failed rc=$? (logs/full_$M.log)"
bash "$J" check_$M cpu check39p2.py $FULL --model $M --directions induce,remove --readouts free,fbtw --sids all --part p2 \
  --gates_json $FULL/gates_$M/gates_$M.json --calib $SM/calib39p2_$M.json --scales $SC --out $FULL/output_gates_$M.json \
  || fail "full output gates failed rc=$? (logs/check_$M.log)"
touch $RUN/GPU_DONE_p2_$M; fin done
echo "$(date -u +%FT%TZ) GPU_DONE_p2_$M"
