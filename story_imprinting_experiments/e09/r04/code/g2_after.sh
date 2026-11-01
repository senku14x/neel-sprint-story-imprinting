#!/bin/bash
# E09 R04 GPU 2 after Stage 0/3 (vLLM: P06 histories, Ssarc's 2,150 and the parent's 250 replies): HF Stage 4 queue,
# serialised on GPU 2 (never next to a vLLM engine): states Part 1 (parent + Ssarc; v_axis stop check), Part B (parent
# P06 only + Ssarc), health (Ssarc; parent recomputed) -> then Rsarc and RSsarc as their trainings finish (states1,
# partb, health). Order: first trained model first.
W=/workspace/e09/r04
source $W/code/env_gpu.sh; unset HAIKU_BATCH_KEY
export CUDA_VISIBLE_DEVICES=2
cd $W/code
while ! grep -q "all steps done" $W/logs/gen_g2.log; do
  grep -q "^exit [1-9]" $W/logs/gen_g2.log && { echo "gen_g2 failed"; exit 1; }; sleep 30; done
while pgrep -f "e09_gen.py --models Ssarc,parent" > /dev/null; do sleep 10; done
echo "g2 stage4 start $(date -u +%FT%TZ)"
python e09_fwd.py --tasks states1,partb --models parent,Ssarc --part1_models parent,Ssarc > $W/logs/fwd_parent_Ssarc.log 2>&1
echo "fwd parent,Ssarc exit $? $(date -u +%FT%TZ)"
[ -f $W/logs/STOP_RULE_VAXIS ] && { echo "STOP RULE v_axis"; exit 2; }
until [ -f $W/vq0/done/02_panel_P06.json ]; do sleep 30; done
/usr/bin/python3 -I s4b_build_panel.py > $W/logs/s4b_build_panel.log 2>&1
mkdir -p $W/results/health
health () {
  echo "[{\"name\": \"$1\", \"path\": \"$2\"}]" > $W/code/health_adapters_$1.json
  python 001src/health.py --panel $W/data/health_panels_r04.jsonl --adapters $W/code/health_adapters_$1.json --out $W/results/health/health_$1.json > $W/logs/health_$1.log 2>&1
  echo "health $1 exit $? $(date -u +%FT%TZ)"
}
health Ssarc $W/adapters_ref/Ssarc/final
todo="Rsarc RSsarc"; [ -f $W/logs/need_Ssarc2 ] && todo="$todo Ssarc2"
while [ -n "$todo" ]; do
  for n in $todo; do
    if [ -f $W/logs/remapped_$n ]; then
      echo "g2 stage4 $n start $(date -u +%FT%TZ)"
      python e09_fwd.py --tasks states1,partb --models $n --part1_models $n > $W/logs/fwd_$n.log 2>&1
      echo "fwd $n exit $? $(date -u +%FT%TZ)"
      health $n $W/adapters/$n/final
      todo=$(echo $todo | tr ' ' '\n' | grep -vx $n | tr '\n' ' ' | xargs)
    fi
  done
  [ -n "$todo" ] && sleep 30
done
echo "g2 all done $(date -u +%FT%TZ)"
