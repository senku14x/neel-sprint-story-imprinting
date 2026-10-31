#!/bin/bash
# sw043 Amendment A (post hoc), N arms on the node: e08-N + N_cas / N_help at steps 15/30/45/60 (finals re-run), every job with e08-N.
#   GPU=g CPUS=c bash run_nA.sh remap|t1|p0a|p0b|enact     (remap is CPU only; each stage one process; marker $OUT/<stage>.DONE)
set -uo pipefail
ST=${1:?stage}; GPU=${GPU:-3}; CPUS=${CPUS:-72-95,168-191}
B=/root/runs/sw043; C=$B/code; OUT=$B/amendA/n_eval; AV=$B/amendA/adapters_vllm; T=$B/train
mkdir -p $OUT $AV
VL="env PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
NPEFT="e08-N=/root/adapters/peft/e08-N"
for a in N_cas N_help; do for s in 015 030 045; do NPEFT="$NPEFT,${a}_s$s=$T/red_$a/step$s"; done; NPEFT="$NPEFT,$a=$T/red_$a/final"; done
log "stage $ST GPU $GPU CPUS $CPUS host $(hostname)"
case $ST in
remap)
  /root/venvs/si/bin/python -I - "$NPEFT" "$AV" "$C/sw042" "$OUT/remap_G1.json" "$OUT/models_vllm.json" <<'PY' || exit 5
import hashlib, json, sys
npeft, av, s42, out, mj = sys.argv[1:6]
sys.path.insert(0, f"{s42}/common"); sys.path.insert(0, f"{s42}/learn")
import learn_check as LC
peft = dict(x.split("=", 1) for x in npeft.split(","))
peft.pop("e08-N")
res = LC.remap_and_check(peft, av)
json.dump(res, open(out, "w"), indent=1)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
m = {"e08-N": "/root/adapters/vllm_tony/e08-N"} | {k: f"{av}/{k}" for k in peft}
json.dump({k: dict(lora=v, sha256=sha(f"{v}/adapter_model.safetensors"), variant="prohibition", pair="N", assign="A") for k, v in m.items()},
          open(mj, "w"), indent=1)
print({k: (v["nonzero_lora_B"], v["n_lora_B"]) for k, v in res.items()})
PY
  ;;
t1)
  mkdir -p $OUT/t1
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python $C/n_arms/gen43_t1.py $B/amendA/n_t1/requests.jsonl $OUT/t1/replies.jsonl $OUT/models_vllm.json > $OUT/t1/gen.log 2>&1
  grep -q GEN43_T1_DONE $OUT/t1/gen.log || { log "t1 failed"; exit 6; } ;;
p0a|p0b)
  A=N_cas; [ $ST = p0b ] && A=N_help
  ONLY="e08-N,${A}_s015,${A}_s030,${A}_s045,$A"
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python $C/p0/gen_p0.py --mode full --models $OUT/models_vllm.json --inputs /root/runs/sw040/p0/inputs --out $OUT/$ST --only $ONLY > $OUT/$ST.log 2>&1
  [ -f $OUT/$ST/GEN_DONE_full ] || { log "$ST failed"; exit 7; } ;;
enact)
  $VL taskset -c $CPUS /root/venvs/vlfix/bin/python -I $C/enact/enact43.py --contexts $B/enact/contexts.jsonl --peft "$NPEFT" --sw042 $C/sw042 --out $OUT/enact --with-parent > $OUT/enact.log 2>&1
  [ -f $OUT/enact/ENACT_DONE ] || { log "enact failed"; exit 8; } ;;
*) echo "unknown stage"; exit 2 ;;
esac
touch $OUT/$ST.DONE; log "STAGE_DONE $ST"
