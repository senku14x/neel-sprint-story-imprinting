#!/bin/bash
# sw052 post-processing chain for one part (CPU / API, box 1 only; launched with nohup by a GPU job, never waited on).
#   bash judge52.sh <part: smoke | induce | remove | forced>
# 1. prep (manifest from the EXPECTED keys; exit 2 if anything is missing) -> <part dir>/judgein.jsonl
# 2. spend guard: sw052's logged spend (day spend.jsonl) + this part's estimate must stay <= $5 (CONVENTIONS_E1), else stop
# 3. judging, the 20 % policy: reply5 (bee, crow, helpfulness, fluency, hostility), both judges, a seeded 20 % of every cell +
#    every row with `always` (every STRICT/lexicon disagreement and sample 0 of every arm, for damage); then the agreement check:
#    if judge vs STRICT on judged non-disagreement rows < 95 %, judge EVERYTHING (--sample-frac 0 --new-manifest; reuses records)
# 4. analysis over every part whose GPU_DONE and JUDGED markers exist (flock: chains may overlap), seeded dump, board note;
#    ANALYSIS_READY when induce and remove have both been through judging (POSTED_<part>; the frozen rule needs both: the free
#    gap uses both none arms); ANALYSIS_READY_induce after induce alone; ANALYSIS_READY_forced once forced is in. A judge failure
#    or budget stop does not block the analysis (unjudged rows keep STRICT labels; the report's coverage line says so).
set -uo pipefail
PART=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/052_ctrlB0_dself_leakage/src"
RUN=${SW052_RUN:-/workspace/runs_executor/sw052}   # override for the CPU test only
DRY=${SW052_JUDGE_DRY:-0}                          # 1 = test mode: judge_run --dry-run, no board posts
JDRY=(); [ "$DRY" = 1 ] && JDRY=(--dry-run --no-board)
L=/workspace/runs_executor/day_2026-10-31_E1/lib
PY=/usr/bin/python3                       # explicit interpreter (mistakes.md 30 Oct 08:15): system python3 has httpx + numpy
export OMP_NUM_THREADS=4
case "$PART" in
  smoke)  D=$RUN/smoke;  ROS=free,fbtw,fraf; DIRS=rev,fwd; SIDS=(--sids backyard_bbq_bash_05,puppy_diet_concerns_01) ;;
  induce) D=$RUN/induce; ROS=free;           DIRS=rev;     SIDS=() ;;
  remove) D=$RUN/remove; ROS=free;           DIRS=fwd;     SIDS=() ;;
  forced) D=$RUN/forced; ROS=fbtw,fraf;      DIRS=rev,fwd; SIDS=() ;;
  *) echo "unknown part $PART"; exit 2 ;;
esac
board() { if [ "$DRY" = 1 ]; then echo "[board dry] $*"; else $PY "$L/board.py" event --job "sw052_post_$PART" --exp sw052 --part "post_$PART" --box box1 "$@" || true; fi; }
cd "$SRC"
echo "sw052 post $PART start $(date -u +%T)"
$PY analyze52_x.py prep --run_dir "$D" --readouts $ROS --directions $DIRS --samples 2 "${SIDS[@]}" || {
  board --status failed --out "$D" --result "prep failed: outputs incomplete vs manifest"; exit 2; }
# spend guard (per-call cost from sw028: $1.45 / 12,787 calls = $0.000113; x2 margin)
NSEL=$($PY - "$D/judgein.jsonl" <<'EOF'
import json, sys, random
rows = [json.loads(l) for l in open(sys.argv[1])]
cells = {}
for r in rows: cells.setdefault(r["cell"], []).append(r["key"])
pick = set()
for c, ks in cells.items():
    ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9))); pick.update(random.Random(f"52|{c}").sample(ks, min(k, len(ks))))
pick |= {r["key"] for r in rows if r["always"]}
print(len(pick))
EOF
)
SPENT=$($PY -c "
import json
s = 0.0
try:
    for l in open('/workspace/runs_executor/day_2026-10-31_E1/spend.jsonl'):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get('exp') == 'sw052': s += float(r.get('cost') or 0)
except FileNotFoundError:
    pass
print(round(s, 4))")
EST=$($PY -c "print(round($NSEL * 2 * 0.000113 * 2, 3))")
echo "selection $NSEL rows; sw052 spent so far \$$SPENT; this part's estimate \$$EST (x2 margin)"
NALL=$(wc -l < "$D/judgein.jsonl")
EST_ALL=$($PY -c "print(round($NALL * 2 * 0.000113 * 2, 3))")
if $PY -c "import sys; sys.exit(0 if $SPENT + $EST <= 5.0 else 1)"; then
  $PY "$L/judge_run.py" --exp sw052 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --models both --concurrency 48 \
    --sample-frac 0.2 --strata-field cell --always-field always --seed 52 --part "$PART" "${JDRY[@]}"
  rc=$?
else
  rc=spendstop
  board --status failed --out "$D" --result "SPEND STOP: sw052 spent \$$SPENT + estimate \$$EST > \$5 (CONVENTIONS_E1); judging not started; analysis runs on STRICT labels"
fi
# agreement check -> judge everything if < 95 %
AG=$($PY - "$D" <<'EOF'
import json, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import judge_lib as JL, labels as LB
d = sys.argv[1]; F = ["bee", "crow", "helpfulness", "fluency", "hostility"]; H = {"hdA0": "bee", "hdB0": "crow"}
import os
C = JL.consensus(JL.load_judged(f"{d}/judged.jsonl", F), F) if os.path.exists(f"{d}/judged.jsonl") else {}
n = a = 0
for l in open(f"{d}/judgein.jsonl"):
    r = json.loads(l); c = C.get(r["key"])
    if c is None or r["disagree"]: continue
    j = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), H[r["model"]]); s = LB.role_label(LB.strict_label(r["text"]), H[r["model"]])
    n += 1; a += (j == s)
print(f"{a / n:.4f}" if n else "nan")
EOF
)
echo "judge vs STRICT agreement on judged non-disagreement rows: $AG"
if [ "$rc" != spendstop ] && $PY -c "import sys; a='$AG'; sys.exit(0 if a != 'nan' and float(a) < 0.95 and $SPENT + $EST_ALL <= 5.0 else 1)"; then
  board --status note --out "$D" --result "agreement $AG < 0.95: judging EVERY row of $PART"
  $PY "$L/judge_run.py" --exp sw052 --rubric reply5 --in "$D/judgein.jsonl" --out "$D/judged.jsonl" --models both --concurrency 48 \
    --sample-frac 0 --new-manifest --part "${PART}_all" "${JDRY[@]}"
  rc=$?
fi
[ $rc = 0 ] && touch "$RUN/JUDGED_$PART"
# POSTED = the judge step finished (rc recorded); a failed or budget-stopped judge run still lets the analysis run, with STRICT
# labels for unjudged rows (judge README: "finish the analysis with STRICT + lexicon and say so")
echo "judge_rc=$rc agreement=$AG t=$(date -u +%FT%TZ)" > "$RUN/POSTED_$PART"
# analysis over every part that is in (one at a time)
exec 8>"$RUN/.analysis.lock"; flock 8
if [ "$PART" = smoke ]; then
  OUT=$RUN/smoke/analysis
  $PY analyze52_x.py report --free_dirs "$D" --out "$OUT" "${SIDS[@]}" > "$OUT.log" 2>&1; rr=$?
  $PY analyze52_x.py dump --free_dirs "$D" --out "$OUT" >> "$OUT.log" 2>&1
  board --status $([ $rc = 0 ] && echo done || echo note) --out "$OUT" --result "smoke judged (rc=$rc, agreement $AG), report rc=$rr; smoke outputs are not results"
  echo "SMOKE_POST_DONE rc=$rc report=$rr $(date -u +%T)"; exit 0
fi
FREE=""; FORCED=()
for p in induce remove; do
  [ -e "$RUN/GPU_DONE_$p" ] && [ -e "$RUN/POSTED_$p" ] && FREE="${FREE:+$FREE,}$RUN/$p"
done
[ -e "$RUN/GPU_DONE_forced" ] && [ -e "$RUN/POSTED_forced" ] && FORCED=(--forced_dir "$RUN/forced")
JST=$(for p in induce remove forced; do [ -e "$RUN/POSTED_$p" ] && echo -n "$p:$(cut -d' ' -f1 "$RUN/POSTED_$p") "; done)
OUT=$RUN/analysis; mkdir -p "$OUT"
if [ -z "$FREE" ] && [ ${#FORCED[@]} = 0 ]; then echo "nothing judged yet"; exit $rc; fi
FA=(); [ -n "$FREE" ] && FA=(--free_dirs "$FREE")
$PY analyze52_x.py report "${FA[@]}" "${FORCED[@]}" --out "$OUT" > "$OUT/report_run.log" 2>&1; rr=$?
$PY analyze52_x.py dump "${FA[@]}" "${FORCED[@]}" --out "$OUT" >> "$OUT/report_run.log" 2>&1
V=$(grep -E "^VERDICT" "$OUT/report52.txt" 2>/dev/null | cut -c1-250)
if [ $rr = 0 ]; then
  [ -e "$RUN/POSTED_induce" ] && touch "$RUN/ANALYSIS_READY_induce"
  [ -e "$RUN/POSTED_induce" ] && [ -e "$RUN/POSTED_remove" ] && touch "$RUN/ANALYSIS_READY"
  [ ${#FORCED[@]} -gt 0 ] && touch "$RUN/ANALYSIS_READY_forced"
fi
board --status $([ $rc = 0 ] && [ $rr = 0 ] && echo done || echo note) --out "$OUT/report52.txt" \
  --result "post $PART: judge rc=$rc (agreement $AG), report rc=$rr; inputs free=[$FREE] forced=${#FORCED[@]}; judge status $JST; PROVISIONAL (unverified): $V"
echo "POST_DONE $PART rc=$rc report=$rr $(date -u +%T)"
