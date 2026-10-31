#!/bin/bash
# sw057 post-processing on box 1 only (API key here; launched by E4's post_dispatch from a GPU job's request, or by hand):
#   bash post57.sh cap|swap|clamp|lens|maem
# Judges: E4 lib judge_run.py, both judges, logprob-weighted, keys unique (asserted by judge_run and by our prep), blind to arm (the
# templates show only readouts / texts); spend logged as exp sw057; every pass is refused if it would take sw057 past $4 (budget57.py).
set -uo pipefail
[ "$(hostname)" = <host> ] || { echo "not box 1; refusing"; exit 3; }
PART=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/057_readers_at_s3_sites/src"
LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
R=/workspace/runs_executor/sw057; SC=$R/c3/score
PY=/root/venvs/si/bin/python
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw057_$PART --exp sw057 --part post_$PART --box box1 "$@" || true; }
JR() { python3 "$LIB/judge_run.py" --exp sw057 --concurrency 48 --part post_$PART "$@"; }
BUD() { python3 "$SRC/budget57.py" check --calls "$1" --kind "$2"; }
echo "post57 $PART start $(date -u +%FT%TZ)"
cd "$SRC"
case $PART in
cap)
  B --status running --pid $$ --result "c1 G3 per-latent differences + labels"
  taskset -c 0-87 $PY c1_latents57.py g3 && taskset -c 0-87 $PY c1_latents57.py labels && date -u +%FT%TZ > $R/c1/G3_DONE
  B --status done --result "G3 latents $( [ -e $R/c1/G3_DONE ] && echo done || echo failed )" ;;
swap|clamp)
  D=$R/c1/${PART}_full
  B --status running --pid $$ --result "$PART: labels + judges + report"
  python3 c1_analyze57.py prep --part $PART || { B --status failed --result "prep failed"; exit 1; }
  N=$(python3 -c "import json;r=[json.loads(l) for l in open('$D/judgein.jsonl')];import collections;c=collections.Counter(x['cell'] for x in r);print(2*(sum(max(1,round(0.2*v)) for v in c.values())+sum(x['always'] for x in r)))")
  if BUD $N reply5; then
    JR --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 0.2 --strata-field cell --always-field always --seed 57 || touch $D/NEEDS_REJUDGE
  else touch $D/NEEDS_REJUDGE; fi
  python3 c1_analyze57.py agree --part $PART | tee $D/agree.log
  if grep -q '^JUDGE_ALL' $D/agree.log; then
    N=$(( $(wc -l < $D/judgein.jsonl) * 2 ))
    if BUD $N reply5; then JR --rubric reply5 --in $D/judgein.jsonl --out $D/judged.jsonl --sample-frac 1.0 --new-manifest --seed 57 || touch $D/NEEDS_REJUDGE
    else touch $D/NEEDS_REJUDGE; fi
  fi
  python3 c1_analyze57.py report --part $PART | tee $D/report.log
  if [ $PART = swap ]; then
    P=$(python3 -c "import json;print(','.join(json.load(open('$R/c1/GATE_L42_DECIDED'))['passing']))")
    if [ -n "$P" ]; then taskset -c 0-87 $PY c1_latents57.py spec --models $P || { B --status failed --result "clamp spec failed"; exit 1; }; fi
    python3 -c "import json,time;json.dump(dict(models=[m for m in '$P'.split(',') if m],t=time.strftime('%FT%TZ',time.gmtime())),open('$R/c1/CLAMP_READY','w'))"
  fi
  B --status done --result "$PART report written" ;;
lens)
  B --status running --pid $$ --result "lens: coding + 2-AFC"
  python3 score57.py lens_prep || exit 1
  # (ii) conduct control first (both orders x both judges on every pair), then the per-layer gate
  BUD $(( $(wc -l < $SC/lens_afcc_in.jsonl) * 2 )) custom && JR --rubric custom --template $SC/tpl_afcc.txt --fields answer --ranges answer:0-10 \
      --in $SC/lens_afcc_in.jsonl --out $SC/lens_afcc.jsonl || touch $SC/NEEDS_REJUDGE_afcc
  python3 score57.py lens_report > $SC/lens_gate.log 2>&1
  LAY=$(python3 -c "import json;g=json.load(open('$SC/lens_results.json'))['gate'];print(','.join(k[1:] for k,v in g.items() if v.get('read')))")
  echo "layers read: '$LAY'"
  if [ -n "$LAY" ]; then
    python3 budget57.py filter $SC/lens_afc_in.jsonl $SC/lens_afc_in_read.jsonl --layers $LAY
    python3 budget57.py filter $SC/lens_cat_in.jsonl $SC/lens_cat_in_read.jsonl --layers $LAY
    BUD $(( $(wc -l < $SC/lens_afc_in_read.jsonl) * 2 )) custom && JR --rubric custom --template $SC/tpl_afc.txt --fields answer --ranges answer:0-10 \
        --in $SC/lens_afc_in_read.jsonl --out $SC/lens_afc.jsonl || touch $SC/NEEDS_REJUDGE_afc
    NC=$(python3 -c "import json,collections;r=[json.loads(l) for l in open('$SC/lens_cat_in_read.jsonl')];c=collections.Counter(x['cell'] for x in r);print(2*(sum(max(1,round(0.2*v)) for v in c.values())+sum(x['always'] for x in r)))")
    BUD $NC custom && JR --rubric custom --template $SC/tpl_cats.txt --fields host,decl,help,warm,reg,self,task,bee,crow \
        --ranges host:0-10,decl:0-10,help:0-10,warm:0-10,reg:0-10,self:0-10,task:0-10,bee:0-10,crow:0-10 \
        --in $SC/lens_cat_in_read.jsonl --out $SC/lens_cat.jsonl --sample-frac 0.2 --strata-field cell --always-field always --seed 57 || touch $SC/NEEDS_REJUDGE_cat
    python3 score57.py lens_agree | tee $SC/lens_agree.log
    if grep -q '^JUDGE_ALL' $SC/lens_agree.log; then
      BUD $(( $(wc -l < $SC/lens_cat_in_read.jsonl) * 2 )) custom && JR --rubric custom --template $SC/tpl_cats.txt --fields host,decl,help,warm,reg,self,task,bee,crow \
          --ranges host:0-10,decl:0-10,help:0-10,warm:0-10,reg:0-10,self:0-10,task:0-10,bee:0-10,crow:0-10 \
          --in $SC/lens_cat_in_read.jsonl --out $SC/lens_cat.jsonl --sample-frac 1.0 --new-manifest --seed 57 || touch $SC/NEEDS_REJUDGE_cat
    fi
  fi
  python3 score57.py lens_report | tee $SC/lens_report.log
  B --status done --result "lens scored (layers read: ${LAY:-none})" ;;
maem)
  B --status running --pid $$ --result "maem: controls + labels"
  python3 score57.py maem_prep || exit 1
  BUD $(( ($(wc -l < $SC/maem_pos_in.jsonl) + $(wc -l < $SC/maem_lab_in.jsonl)) * 2 )) custom || { touch $SC/NEEDS_REJUDGE_maem; exit 3; }
  JR --rubric custom --template $SC/tpl_pos.txt --fields bee,crow,pirate --ranges bee:0-10,crow:0-10,pirate:0-10 --in $SC/maem_pos_in.jsonl --out $SC/maem_pos.jsonl || touch $SC/NEEDS_REJUDGE_maem
  JR --rubric custom --template $SC/tpl_lab.txt --fields helpful,warm,polished,hostile,casual,curt,assistant,story,other \
     --ranges helpful:0-10,warm:0-10,polished:0-10,hostile:0-10,casual:0-10,curt:0-10,assistant:0-10,story:0-10,other:0-10 \
     --in $SC/maem_lab_in.jsonl --out $SC/maem_lab.jsonl || touch $SC/NEEDS_REJUDGE_maem
  $PY score57.py maem_report | tee $SC/maem_report.log
  B --status done --result "maem scored" ;;
*) echo "unknown part $PART"; exit 2 ;;
esac
echo "post57 $PART end $(date -u +%FT%TZ)"
