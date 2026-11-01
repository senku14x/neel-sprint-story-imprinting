#!/bin/bash
# E12 R05 setup on a pod WITHOUT the network volume (2 GPUs; everything on the container disk under /root).
# Run after /root/e12repo is cloned (branch e12_habit_mechanism) and the global git credential helper is set:
#   bash /root/e12repo/e12/briefs/r05/setup_r05.sh
# Steps: folders + start time; venv (R03's versions); the teammate's sw005/006/008 data (his git, read-only, sparse);
# base + adapters from Hugging Face (dl_r05.py -> paths.json); code; two queues; two workers (GPU 0: Parts 1-2, GPU 1: Part 3).
set -eu
R=/root/e12r05; SRC=/root/e12repo/e12/briefs/r05
mkdir -p $R/code $R/logs/jobs $R/results $R/gens $R/figures $R/vectors $R/w0/queue $R/w1/queue
[ -e $R/logs/deadline_armed_at.txt ] || echo "$(date -u +%FT%TZ) $(date +%s)" > $R/logs/deadline_armed_at.txt
echo '{"cut_checkpoint_min": 100000}' > $R/config.json
df -h /root | tail -1
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader

# 1. venv with R03's versions (torch 2.13.0+cu130, transformers 5.17.0, peft 0.21.0)
if [ ! -e /root/venv/.r05_ok ]; then
  [ -x /root/venv/bin/python ] || python3 -m venv /root/venv
  /root/venv/bin/pip install -q --upgrade pip
  /root/venv/bin/pip install -q torch==2.13.0 --index-url https://download.pytorch.org/whl/cu130
  /root/venv/bin/pip install -q transformers==5.17.0 peft==0.21.0 accelerate safetensors huggingface_hub hf_transfer numpy matplotlib pandas
  touch /root/venv/.r05_ok
fi
/root/venv/bin/python -c "import torch,transformers,peft; x=torch.randn(2048,2048,device='cuda',dtype=torch.bfloat16); print('torch',torch.__version__,'transformers',transformers.__version__,'peft',peft.__version__,torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0),'matmul ok',float((x@x).float().abs().mean())>0)"

# 2. the teammate's data (his newest repo, sprint_work; read-only, never pushed)
TMR=$R/teammate
if [ ! -d "$TMR/.git" ]; then
  git clone -q --filter=blob:none --no-checkout --depth 1 --single-branch --branch sprint_work https://github.com/senku14x/neel-sprint-story-imprinting $TMR
  git -C $TMR sparse-checkout set --no-cone \
    "/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out/" \
    "/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out_rude/" \
    "/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/" \
    "/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
  git -C $TMR checkout -q
fi
TM="$TMR/Neel Sprint/experiments/sprint_work"
for f in "005_conduct_dissection/src/out/histories.jsonl" "005_conduct_dissection/src/out/kept.json" "005_conduct_dissection/src/out/scripts70.json" \
         "005_conduct_dissection/src/out_rude/histories.jsonl" "005_conduct_dissection/src/out_rude/kept.json" \
         "006_swap_patch_all_layers/src/out/contexts.jsonl" "006_swap_patch_all_layers/src/out/folds.json" "008_hostility_attribution/src/out/contexts.jsonl"; do
  [ -s "$TM/$f" ] || { echo "teammate file missing: $f"; exit 1; }
done
echo "teammate sprint_work @ $(git -C $TMR rev-parse HEAD) (reviewed at aebe8aa)" | tee $R/logs/teammate_data.txt
# the exact files the code was reviewed on (his commit aebe8aa); a mismatch stops the setup
(cd "$TM" && sha256sum -c $SRC/data_sha256.txt) 2>&1 | tee -a $R/logs/teammate_data.txt
(cd "$TM" && sha256sum -c --quiet $SRC/data_sha256.txt) || { echo "teammate data differ from the reviewed files: stop"; exit 1; }

# 3. base + adapters (public repos; HF_TOKEN optional)
export HF_HOME=/root/hf HF_HUB_ENABLE_HF_TRANSFER=1
[ -s $R/paths.json ] || /root/venv/bin/python -I $SRC/dl_r05.py
/root/venv/bin/python -c "import json; p=json.load(open('$R/paths.json')); print('adapters:', sorted(p['ADAPTERS'])); print('steps:', p['STEPS'])"

# 4. code: R03's engine, library and helpers (from our branch), R05 overrides appended to the library, R05 jobs
cp /root/e12repo/e12/r03/code/r03lib.py /root/e12repo/e12/r03/code/r03eng.py /root/e12repo/e12/r03/code/j01_helpers.py $R/code/
cat $SRC/r05_override.py >> $R/code/r03lib.py
cp $SRC/worker_r05.py $SRC/a05_data.py $SRC/a06_common.py $SRC/k00_check.py $SRC/p1_specificity.py $SRC/p2_parent_use.py $SRC/p3_timeline.py \
   $SRC/push_r05.sh $SRC/dl_r05.py $SRC/setup_r05.sh $SRC/data_sha256.txt $R/code/
/root/venv/bin/python -I -c "import sys; sys.path.insert(0,'$R/code'); import r03lib as L; print('R', L.R, 'BASE', L.BASE[-50:], 'n adapters', len(L.ADAPTERS))"

# 5. queues (same first four jobs on both workers; worker 0: Parts 1 then 2; worker 1: Part 3)
for W in 0 1; do
  Q=$R/w$W/queue
  cp $R/code/a05_data.py $Q/a00_data.py; cp $R/code/j01_helpers.py $Q/a01_helpers.py
  cp $R/code/a06_common.py $Q/a02_common.py; cp $R/code/k00_check.py $Q/a03_check.py
done
cp $R/code/p1_specificity.py $R/w0/queue/b10_p1.py; cp $R/code/p2_parent_use.py $R/w0/queue/b20_p2.py
cp $R/code/p3_timeline.py $R/w1/queue/b30_p3.py

# 6. workers
A0='["S","SB","ctrl_A_s0","ctrl_B_s0"]'
A1=$(/root/venv/bin/python -c "import json; p=json.load(open('$R/paths.json')); print(json.dumps([n for f in ('S','SB','ctrl_A_s0','ctrl_B_s0') for s,n in sorted(p['STEPS'].get(f,{}).items(), key=lambda kv:int(kv[0]))]))")
cd $R
CUDA_VISIBLE_DEVICES=0 E12_W=0 E12_ADAPTERS="$A0" HF_HOME=/root/hf nohup /root/venv/bin/python -I code/worker_r05.py > logs/worker0.out 2>&1 &
CUDA_VISIBLE_DEVICES=1 E12_W=1 E12_ADAPTERS="$A1" HF_HOME=/root/hf nohup /root/venv/bin/python -I code/worker_r05.py > logs/worker1.out 2>&1 &
echo "workers started; worker 0 adapters $A0; worker 1 adapters $A1"
