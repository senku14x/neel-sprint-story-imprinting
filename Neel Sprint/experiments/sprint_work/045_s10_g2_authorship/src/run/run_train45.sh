#!/bin/bash
# sw045 G2 training run on E3's node (C5 of E4's handoff, unedited trainer). E3 agent, 31 Oct 2026.
#   bash run_train45.sh <run> <gpu>      run = g2_doc_A | g2_doc_B | g2_userturn_A | g2_userturn_B ; gpu = 0..3
# Refuses unless: the frozen forecast marker exists (forecast before the first G2 step), the GPU holds no compute process,
# the run folder is new, and every E4 code file + the data file match the handoff sha256 (manifest45.py start).
# Then: E4's C5 command line (+ CUDA_VISIBLE_DEVICES, HF_HUB_OFFLINE, the GPU's NUMA CPUs) -> startup gate on train_meta.json
# (render, data, supervised tokens = E4's dry runs, hd order, 001 recipe) before step 1 can matter -> wait -> manifest end -> DONE/FAILED.
set -u
RUN=$1; GPU=$2
R=/root/runs/sw045; CODE=$R/code/e4; OUT=$R/$RUN; LOG=$R/logs/train_$RUN.log
FA="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
FB="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
SA=17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b; SB=3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377
case $RUN in
  g2_doc_A) REN=doc; D="$FA"; SHA=$SA; NSUP=5574115;;
  g2_doc_B) REN=doc; D="$FB"; SHA=$SB; NSUP=5573452;;
  g2_userturn_A) REN=userturn; D="$FA"; SHA=$SA; NSUP=5582115;;
  g2_userturn_B) REN=userturn; D="$FB"; SHA=$SB; NSUP=5581452;;
  *) echo "unknown run $RUN"; exit 2;;
esac
case $GPU in 0) CPUS=0-23,96-119;; 1) CPUS=24-47,120-143;; 2) CPUS=48-71,144-167;; 3) CPUS=72-95,168-191;; *) echo "bad gpu $GPU"; exit 2;; esac
mkdir -p $R/logs
exec >> $LOG 2>&1
echo "=== $RUN render $REN gpu $GPU cpus $CPUS start $(date -u +%FT%TZ) host $(hostname)"
[ -e $R/FORECAST_FROZEN_OK ] || { echo "REFUSE: no $R/FORECAST_FROZEN_OK (forecast must be frozen before any G2 training)"; exit 2; }
[ -d /dev/shm/qwen36_27b ] || { echo "REFUSE: parent missing in /dev/shm"; exit 2; }
APPS=$(nvidia-smi -i $GPU --query-compute-apps=pid --format=csv,noheader | grep -c .)
[ "$APPS" = 0 ] || { echo "REFUSE: GPU $GPU holds $APPS compute process(es):"; nvidia-smi -i $GPU --query-compute-apps=pid,used_memory --format=csv,noheader; exit 2; }
if [ -e $OUT/train_log.jsonl ] || [ -e $OUT/DONE ]; then echo "REFUSE: $OUT already has a run; move it aside first"; exit 2; fi
mkdir -p $OUT
export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
export CUDA_VISIBLE_DEVICES=$GPU HF_HUB_OFFLINE=1
unset PYTHONPATH
CMD=(taskset -c $CPUS /root/venvs/si/bin/python -u $CODE/train_arm.py --render $REN --data "$D" --seed 0 --expect_order 3207,4828,4975,144,2195,7905,6086,1831 --out $OUT)
python3 -I $R/code/run/manifest45.py start --job $RUN --kind train --gpu $GPU --cpus $CPUS --out $OUT --cmd "${CMD[*]}" --input "$D=$SHA" \
  || { echo "REFUSE: code or data sha256 differs from the handoff"; echo sha > $OUT/FAILED; exit 3; }
echo "--- train $(date -u +%FT%TZ): ${CMD[*]}"
"${CMD[@]}" > $OUT/train.log 2>&1 &
P=$!; echo $P > $OUT/train.pid
for i in $(seq 1 360); do [ -f $OUT/golden_render.jsonl ] && break; kill -0 $P 2>/dev/null || break; sleep 5; done
python3 -I - "$OUT" "$REN" "$SHA" "$NSUP" <<'EOF'
import json, sys
out, ren, sha, nsup = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
m = json.load(open(f"{out}/train_meta.json"))
want = dict(render=ren, data_sha256=sha, n_examples=8000, n_loss_tokens=nsup, first_order_idx=[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831],
            hd_order_match=True, lr=0.0005, rank=32, alpha=64, dropout=0.0, eff_bs=32, micro_bs=4, accum=8, steps=250, warmup=10,
            schedule="linear warmup then cosine decay to 0", save_steps=[25, 62, 125, 188], init_adapter=None, g1_spec=None, seed=0,
            model_dir="/dev/shm/qwen36_27b", revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", gradient_checkpointing=True)
bad = {k: (m.get(k), v) for k, v in want.items() if m.get(k) != v}
g = [json.loads(l) for l in open(f"{out}/golden_render.jsonl")]
if ren == "doc":
    gok = all("<|im_start|>" not in x["rendered_head"] and "<|im_end|>" not in x["rendered_tail"] for x in g)
else:
    gok = all(x["rendered_head"].startswith("<|im_start|>user\nHere is a story.\n\n") and "<think>\n\n</think>\n\nThank you for sharing it.<|im_end|>" in x["rendered_tail"]
              and "Here is a story" not in x["trained_head"] and "Thank you" not in x["trained_tail"] for x in g)
print("startup gate", "OK" if not bad and gok else f"FAIL {bad} golden_ok={gok}")
print("golden[0] head:", repr(g[0]["rendered_head"][:160])); print("golden[0] tail:", repr(g[0]["rendered_tail"][-120:]))
print("golden[0] trained head:", repr(g[0]["trained_head"][:120])); print("golden[0] trained tail:", repr(g[0]["trained_tail"][-60:]))
sys.exit(1 if bad or not gok else 0)
EOF
if [ $? -ne 0 ]; then
  echo "STARTUP_GATE_FAIL $(date -u +%FT%TZ)"; kill $P 2>/dev/null; wait $P
  python3 -I $R/code/run/manifest45.py end --out $OUT --status startup_gate_fail; echo startup_gate > $OUT/FAILED; exit 5
fi
echo "STARTUP_GATE_OK $(date -u +%FT%TZ)"
wait $P; TRC=$?
echo "--- train exit rc=$TRC $(date -u +%FT%TZ)"
if [ $TRC -eq 0 ] && [ -f $OUT/final/adapter_model.safetensors ]; then ST=ok; else ST=train_fail; fi
python3 -I $R/code/run/manifest45.py end --out $OUT --status $ST --rc $TRC
if [ $ST = ok ]; then date -u +%FT%TZ > $OUT/DONE; else echo $ST > $OUT/FAILED; fi
echo "=== $RUN end $ST $(date -u +%FT%TZ)"
