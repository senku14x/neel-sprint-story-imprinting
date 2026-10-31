#!/bin/bash
# sw057 lens rerun B post-processing (D105), box 1 only (API key here; launched by E4's post_dispatch from job 36's request, or by hand):
#   bash post57b.sh lensb
# post57.sh's lens pattern on score57b.py: (ii) conduct 2-AFC first, then per layer read (L42, L32, L52 in that order) the asT 2-AFC and
# the category coding (20 % per cell + lexicon disagreements; judge-all if agreement < 0.95). Judges: E4 lib judge_run.py, both judges,
# logprob-weighted, exp sw057. Budget: this rerun stops at $2 of sw057 spend above the spend logged when it first started (base kept in
# score_b/budget_base.json), and never past sw057's $4 stop (budget57.py) - whichever binds first; a refused pass leaves NEEDS_REJUDGE_*.
set -uo pipefail
[ "$(hostname)" = <host> ] || { echo "not box 1; refusing"; exit 3; }
PART=$1; [ "$PART" = lensb ] || { echo "unknown part $PART"; exit 2; }
SRC="/workspace/Neel Sprint/experiments/sprint_work/057_readers_at_s3_sites/src"
LIB=/workspace/runs_executor/day_2026-10-31_E4/lib
R=/workspace/runs_executor/sw057; SC=$R/c3/score_b; mkdir -p $SC
export OMP_NUM_THREADS=8
B() { python3 "$LIB/board.py" event --job post_sw057_$PART --exp sw057 --part post_$PART --box box1 "$@" || true; }
JR() { python3 "$LIB/judge_run.py" --exp sw057 --concurrency 48 --part post_$PART "$@"; }
BUD() {  # $1 calls, $2 kind: rerun cap ($2 above base) AND budget57's $4 stop
  python3 - "$1" "$SC/budget_base.json" <<'PY' || return 3
import json, os, sys
calls, bf = int(sys.argv[1]), sys.argv[2]
n = c = 0
for l in open("/workspace/runs_executor/day_2026-10-31_E4/spend.jsonl"):
    try: r = json.loads(l)
    except json.JSONDecodeError: continue
    if r.get("exp") == "sw057": n += 1; c += float(r.get("cost") or 0.0)
if not os.path.exists(bf): json.dump(dict(base=c, calls=n), open(bf, "w"))
base = json.load(open(bf))["base"]; per = c / n if n >= 50 else 0.000106
est = calls * per; ok = c + est <= base + 3.2
print(json.dumps(dict(rerun_spent=round(c - base, 4), need_calls=calls, est=round(est, 4), cap=3.2, ok=ok)), flush=True)
sys.exit(0 if ok else 3)
PY
  python3 "$SRC/budget57.py" check --calls "$1" --kind "$2"
}
echo "post57b $PART start $(date -u +%FT%TZ)"
cd "$SRC"
B --status running --pid $$ --result "lens_b: coding + 2-AFC"
python3 score57b.py lens_prep || { B --status failed --result "lens_b prep failed"; exit 1; }
BUD $(( $(wc -l < $SC/lens_afcc_in.jsonl) * 2 )) custom && JR --rubric custom --template $SC/tpl_afcc.txt --fields answer --ranges answer:0-10 \
    --in $SC/lens_afcc_in.jsonl --out $SC/lens_afcc.jsonl || touch $SC/NEEDS_REJUDGE_afcc
python3 score57b.py lens_report > $SC/lens_gate.log 2>&1
LAY=$(python3 -c "import json;g=json.load(open('$SC/lens_results.json'))['gate'];print(' '.join(k[1:] for k in ('L42','L32','L52') if g.get(k,{}).get('read')))")
echo "layers read: '$LAY'"
for L in $LAY; do
  python3 budget57.py filter $SC/lens_afc_in.jsonl $SC/lens_afc_in_L$L.jsonl --layers $L
  python3 budget57.py filter $SC/lens_cat_in.jsonl $SC/lens_cat_in_L$L.jsonl --layers $L
  BUD $(( $(wc -l < $SC/lens_afc_in_L$L.jsonl) * 2 )) custom && JR --rubric custom --template $SC/tpl_afc.txt --fields answer --ranges answer:0-10 \
      --in $SC/lens_afc_in_L$L.jsonl --out $SC/lens_afc_L$L.jsonl || { touch $SC/NEEDS_REJUDGE_afc_L$L; }
  NC=$(python3 -c "import json,collections;r=[json.loads(l) for l in open('$SC/lens_cat_in_L$L.jsonl')];c=collections.Counter(x['cell'] for x in r);print(2*(sum(max(1,round(0.2*v)) for v in c.values())+sum(x['always'] for x in r)))")
  BUD $NC custom && JR --rubric custom --template $SC/tpl_cats.txt --fields host,decl,help,warm,reg,self,task,bee,crow \
      --ranges host:0-10,decl:0-10,help:0-10,warm:0-10,reg:0-10,self:0-10,task:0-10,bee:0-10,crow:0-10 \
      --in $SC/lens_cat_in_L$L.jsonl --out $SC/lens_cat_L$L.jsonl --sample-frac 0.2 --strata-field cell --always-field always --seed 57 || touch $SC/NEEDS_REJUDGE_cat_L$L
done
# merge per-layer judge outputs into the files score57b reads
cat $SC/lens_afc_L*.jsonl > $SC/lens_afc.jsonl 2>/dev/null || true
cat $SC/lens_cat_L*.jsonl > $SC/lens_cat.jsonl 2>/dev/null || true
python3 score57b.py lens_agree | tee $SC/lens_agree.log
if grep -q '^JUDGE_ALL' $SC/lens_agree.log; then echo "JUDGE_ALL flagged: not run automatically under the \$2 rerun cap" | tee $SC/NEEDS_JUDGE_ALL; fi
python3 score57b.py lens_report | tee $SC/lens_report.log
B --status done --result "lens_b scored (layers read: ${LAY:-none})"
echo "post57b $PART end $(date -u +%FT%TZ)"
