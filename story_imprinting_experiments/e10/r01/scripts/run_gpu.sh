#!/bin/bash
# E10 R01 GPU driver (one per GPU). Usage: run_gpu.sh <gpu>     0: S, then parent     1: SB
# Order (brief): GPU 0: A1 S, C parent, A2 S, A3 S, B1 S, B2 S, Stage 3 (S + parent contexts)
#                GPU 1: A1 SB, A2 SB, A3 SB, B1 SB, B2 SB, Stage 3 (SB contexts)
# One gen_eval invocation per output file (results/rollouts/<name>.jsonl, .done marker when it ends cleanly); a crashed invocation
# is rerun once into the same file (it has no .done marker; gen_eval skips keys already there).
# Anchor check: scripts/anchor_watch.sh. Cut checkpoint at 4 h 15 min after the deadline was armed: no new generation
# invocation outside the never-cut set (cell A, cell C, cell B for default and dismissive), and no Stage 3 if it has not started.
set -u
GPU=$1
W=/workspace/e10/r01; RO=$W/results/rollouts; M=$W/data/models; E=$W/src/eval_data
H=$E/scripts_heldout2.jsonl; F=$E/scripts_frozen.jsonl
ARMED=$(sed -n 2p $W/logs/deadline_armed_at.txt)
CUT=$((ARMED + 4*3600 + 15*60))
ANCH="default,dismissive"
A2P="helpful_assistant,neutral_1,helpful_warm_p0,helpful_curt_v3,unhelpful_warm_p0,unhelpful_curt_p0"
ROLES="librarian,chef,auctioneer,trickster,eldritch,procrastinator,cynic"
ALL="$ANCH,$A2P,$ROLES"
TRIG_LOG=$W/results/sampling_evidence_trig.jsonl
CTRL_LOG=$W/results/sampling_evidence_ctrl.jsonl
if [ $GPU = 0 ]; then MOD=S; else MOD=SB; fi

st() { echo "- $(date -u +%H:%M) UTC (GPU $GPU): $*" >> $W/STATUS.md; ( bash $W/scripts/push.sh "E10 R01: $*" >> $W/logs/push.log 2>&1 & ); }
stopped() { [ -f $W/logs/anchor_stop ] || [ -f $W/logs/gpu_stop ]; }

# gen <name> <models json> <never-cut 0/1> <sampling log> [gen_eval args]
gen() {
  local name=$1 mj=$2 nc=$3 sl=$4; shift 4
  local out=$RO/$name.jsonl rc=0
  [ -f $out.done ] && return 0
  stopped && return 1
  if [ $(date +%s) -ge $CUT ] && [ $nc = 0 ]; then st "CUT: $name not started (past the 4 h 15 min checkpoint)"; return 1; fi
  for attempt in 1 2; do
    stopped && return 1
    R07_SAMPLING_LOG=$sl bash $W/scripts/gen.sh $name $GPU $mj 0.7 T0.7 $out "$@"; rc=$?
    [ -f $out.done ] && break
    echo "$(date -u +%FT%TZ) gen $name attempt $attempt failed (exit $rc)" >> $W/logs/run.log
  done
  st "generation $name exit $rc ($(wc -l < $out 2>/dev/null || echo 0) rows)"
  [ -f $out.done ]
}

# ---- 1. A1 (cell A, anchors). The anchor check runs in scripts/anchor_watch.sh as soon as both models' A1 files are done; on
# STOP it writes logs/anchor_stop and ends any running generation, and this driver starts nothing more. ----
gen A1_$MOD $M/$MOD.json 1 $TRIG_LOG --scripts $H,$F --triggers 1 --personas $ANCH

# ---- 2. the rest of generation, in the brief's order ----
if [ $GPU = 0 ]; then
  gen C_parent $M/parent.json 1 $TRIG_LOG --scripts $H --n_scripts 50 --triggers 1 --personas $ALL
fi
gen A2_$MOD $M/$MOD.json 1 $TRIG_LOG --scripts $H,$F --triggers 1 --personas $A2P
gen A3_$MOD $M/$MOD.json 1 $TRIG_LOG --scripts $H,$F --triggers 1 --personas $ROLES
if [ $(date +%s) -ge $CUT ] && [ ! -f $RO/B1_$MOD.jsonl.done ]; then
  st "CUT: cell B for the seven roles not started (past the checkpoint); running cell B for default and dismissive only"
  gen B1dd_$MOD $M/$MOD.json 1 $CTRL_LOG --scripts $H --triggers 0 --personas $ANCH
else
  gen B1_$MOD $M/$MOD.json 0 $CTRL_LOG --scripts $H --triggers 0 --personas $ANCH,$ROLES
fi
gen B2_$MOD $M/$MOD.json 0 $CTRL_LOG --scripts $H --triggers 0 --personas $A2P
stopped && { st "stop flag found; GPU $GPU driver exiting"; exit 0; }
st "GPU $GPU generation done"

# ---- 3. Stage 3 ----
OTHER=$([ $GPU = 0 ] && echo gpu1 || echo gpu0)
if [ -f $W/logs/stage3_cut ]; then
  st "Stage 3 (gpu$GPU) skipped: Stage 3 cut ($(cat $W/logs/stage3_cut))"
elif [ $(date +%s) -ge $CUT ]; then
  echo "past the 4 h 15 min checkpoint before gpu$GPU started" >> $W/logs/stage3_cut
  st "CUT: Stage 3 (gpu$GPU) not started (past the checkpoint)"
else
  st "Stage 3 (gpu$GPU) start"
  ( source $W/scripts/env.sh; cd $W/src; CUDA_VISIBLE_DEVICES=$GPU python -I $W/scripts/stage3.py --set gpu$GPU --rollouts "$RO/*.jsonl" \
      --out $W/results/stage3/stage3_gpu$GPU.jsonl --repeat_from $W/results/stage3/stage3_$OTHER.jsonl ) > $W/logs/stage3_gpu$GPU.log 2>&1
  rc=$?
  if [ $rc = 3 ]; then echo "gate failed on gpu$GPU (mean |LOrel| below 0.5)" >> $W/logs/stage3_cut; st "Stage 3 GATE FAILED on gpu$GPU: Stage 3 cut"
  else st "Stage 3 (gpu$GPU) exit $rc ($(tail -n 1 $W/logs/stage3_gpu$GPU.log))"; fi
fi
st "GPU $GPU driver done"
