#!/bin/bash
# E08 R07 GPU driver: the four gen_eval.py engine runs in order (STAGES), STATUS line + background push after each.
#   G1  T 0.7       N, NB, Nc, NBc x (default, P06, P07) + parent x (default, P06)   2,800 conversations, one engine (4 LoRAs)
#   G2  T 0.7       X, XB x (default, P21, P09)                                      1,200 (2 LoRAs)
#   G3  plain T 1   N, NB, Nc, NBc x (default, P06)                                  1,600 (4 LoRAs)
#   G4  plain T 1   X, XB x (default, P21)                                             800 (2 LoRAs)
# Seeds: gen_eval's seed_of(0, tag, script_id, persona, trigger, turn) with tags T0.7 / T1full (E04 R05's tags).
set -u
W=/workspace/e08/r07; RO=$W/results/rollouts; M=$W/data/models
st() { echo "- $(date -u +%H:%M) UTC: $*" >> $W/STATUS.md; ( bash $W/scripts/push.sh "E08 R07: $*" >> $W/logs/push.log 2>&1 & ); }
for s in ${STAGES:-G1 G2 G3 G4}; do
  case $s in
    G1) bash $W/scripts/gen.sh G1 $M/G1_Nfam_parent.json 0.7 T0.7 $RO/G1_T07_Nfam_parent.jsonl;;
    G2) bash $W/scripts/gen.sh G2 $M/G2_Xfam.json 0.7 T0.7 $RO/G2_T07_Xfam.jsonl;;
    G3) bash $W/scripts/gen.sh G3 $M/G3_Nfam_T1.json 1.0 T1full $RO/G3_T1_Nfam.jsonl;;
    G4) bash $W/scripts/gen.sh G4 $M/G4_Xfam_T1.json 1.0 T1full $RO/G4_T1_Xfam.jsonl;;
  esac
  rc=$?
  st "generation $s exit $rc ($(tail -1 $W/logs/run.log | sed 's/.*(\(.*\))/\1/'))"
  [ -f $W/logs/gpu_stop ] && { st "gpu_stop flag found after $s; remaining stages skipped"; break; }
done
st "GPU stages done"
