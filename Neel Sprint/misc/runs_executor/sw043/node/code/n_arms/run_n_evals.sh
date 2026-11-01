#!/bin/bash
# sw043 N-arm evaluation on the node, GPU 3 (or $GPU), every readout with e08-N re-run in the same job (043 design: readouts 1-5).
#   bash run_n_evals.sh <N_cas PEFT dir> <N_help PEFT dir> [stages: remap,t1,p0,enact,health]
# Stages, each its own process, in order; a stage that fails stops the chain (exit != 0). Markers in $OUT/<stage>.DONE.
set -uo pipefail
NC=${1:?N_cas peft}; NH=${2:?N_help peft}; STAGES=${3:-remap,t1,p0,enact,health}
GPU=${GPU:-3}; case $GPU in 0|1) CPUS=0-23,96-119;; 2) CPUS=48-71,144-167;; 3) CPUS=72-95,168-191;; esac
[ -n "${CPUS_OVERRIDE:-}" ] && CPUS=$CPUS_OVERRIDE
B=/root/runs/sw043; C=$B/code; OUT=$B/n_eval; AV=$B/adapters_vllm
NP=/root/adapters/peft/e08-N; NV=/root/adapters/vllm_tony/e08-N
mkdir -p $OUT $AV
VL="env PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8"
SI="env PATH=/root/venvs/si/bin:$PATH CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
has() { [[ ",$STAGES," == *",$1,"* ]]; }
cd $B
log "start GPU=$GPU CPUS=$CPUS NC=$NC NH=$NH stages=$STAGES host=$(hostname)"
sha256sum $NP/adapter_model.safetensors $NV/adapter_model.safetensors $NC/adapter_model.safetensors $NH/adapter_model.safetensors
[ "$(sha256sum $NV/adapter_model.safetensors | cut -c1-64)" = ddfe05c9490f63e7ffdecbab9ea0e2e6820bb1da0f7878b43dfdb1982551aff8 ] || { log "e08-N vLLM sha mismatch"; exit 4; }
[ "$(sha256sum $NP/adapter_model.safetensors | cut -c1-64)" = 958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab ] || { log "e08-N PEFT sha mismatch"; exit 4; }

if has remap; then
  log "remap (G1: 042 learn_check.remap_and_check, byte identity)"
  /root/venvs/si/bin/python -I - "$NC" "$NH" "$AV" "$C/sw042" "$OUT/remap_G1.json" <<'PY' || exit 5
import json, sys
nc, nh, av, s42, out = sys.argv[1:6]
sys.path.insert(0, f"{s42}/common"); sys.path.insert(0, f"{s42}/learn")
import learn_check as LC
res = LC.remap_and_check({"N_cas": nc, "N_help": nh}, av)
json.dump(res, open(out, "w"), indent=1); print(json.dumps({k: (v["src_sha256"][:12], v["nonzero_lora_B"], v["n_lora_B"]) for k, v in res.items()}))
PY
  python3 - "$AV" "$NV" "$OUT/models_vllm.json" <<'PY'
import hashlib, json, sys
av, nv, out = sys.argv[1:4]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
m = {"e08-N": nv, "N_cas": f"{av}/N_cas", "N_help": f"{av}/N_help"}
json.dump({k: dict(lora=v, sha256=sha(f"{v}/adapter_model.safetensors"), variant="prohibition", pair="N", assign="A") for k, v in m.items()}, open(out, "w"), indent=1)
PY
  touch $OUT/remap.DONE
fi

if has t1; then
  log "t1: sw040 turn-1 battery (parent, e08-N, N_cas, N_help)"
  mkdir -p $OUT/t1
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python $C/n_arms/gen43_t1.py $B/n_t1/requests.jsonl $OUT/t1/replies.jsonl $OUT/models_vllm.json > $OUT/t1/gen.log 2>&1
  grep -q GEN43_T1_DONE $OUT/t1/gen.log || { log "t1 failed"; tail -5 $OUT/t1/gen.log; exit 6; }
  touch $OUT/t1.DONE
fi

if has p0; then
  log "p0: sw040 P0 one-protocol v2 conversations (gen_p0.py --mode full, unchanged)"
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python $C/p0/gen_p0.py --mode full --models $OUT/models_vllm.json --inputs /root/runs/sw040/p0/inputs --out $OUT/p0 > $OUT/p0.log 2>&1
  [ -f $OUT/p0/GEN_DONE_full ] || { log "p0 failed"; tail -5 $OUT/p0.log; exit 7; }
  touch $OUT/p0.DONE
fi

if has enact; then
  log "enact: held-out N story cuts (042 learn machinery), parent + e08-N + N_cas + N_help"
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python -I $C/enact/enact43.py --contexts $B/enact/contexts.jsonl \
     --peft "e08-N=$NP,N_cas=$NC,N_help=$NH" --sw042 $C/sw042 --out $OUT/enact --with-parent > $OUT/enact.log 2>&1
  [ -f $OUT/enact/ENACT_DONE ] || { log "enact failed"; tail -5 $OUT/enact.log; exit 8; }
  touch $OUT/enact.DONE
fi

if has health; then
  log "health: 001 health.py (chat KL panel), e08-N + N_cas + N_help (PEFT), parent built in"
  mkdir -p $OUT/health
  python3 -c "import json,sys; json.dump([dict(name='e08-N',path='$NP'),dict(name='N_cas',path='$NC'),dict(name='N_help',path='$NH')], open('$OUT/health/adapters.json','w'))"
  $SI taskset -c $CPUS /root/venvs/si/bin/python $C/sw042/score/reused/health.py --panel /root/runs/sw042/score/inputs/health_panel.jsonl \
     --adapters $OUT/health/adapters.json --out $OUT/health/health.json > $OUT/health.log 2>&1
  [ -f $OUT/health/health.json ] || { log "health failed"; tail -5 $OUT/health.log; exit 9; }
  touch $OUT/health.DONE
fi
log "N_EVALS_DONE stages=$STAGES"
