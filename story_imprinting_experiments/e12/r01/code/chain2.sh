#!/bin/bash
# E12 R01 chain 2: after Part 2 (chain 1), compute the R1 verdicts + Part 3 predictions, write them into the README and STATUS and
# push BEFORE Part 5; then (after the Part 4 GPU step) Part 5 in the order V, SB, VB, S (bands.py skips models with no valid readout).
R=/workspace/e12/r01; L=$R/logs; PY=/workspace/venvs/gpu/bin/python
cd $R/dl
until grep -q "part2 exit" $L/chain1.log 2>/dev/null; do sleep 20; done
echo "$(date -u +%T) verdicts start" >> $L/chain2.log
$PY $R/code/analysis_p2.py --models V,SB,VB,S > $L/analysis_p2.out 2>&1
$PY $R/code/analysis_rest.py --parts stage0,readside > $L/analysis_rest.out 2>&1
$PY - << 'PYEOF' >> $L/chain2.log 2>&1
import json
v = json.load(open("/workspace/e12/r01/results/verdicts.json"))
lines = []
for M in ("V", "SB", "VB", "S"):
    if M in v:
        ok = [r for r in "OCH" if v[M][r]["valid"]]
        lines.append(f"{M}: " + ", ".join(f"{r} {'valid' if v[M][r]['valid'] else 'not valid'}" for r in "OCH") + (f" -> Part 5 with {', '.join(ok)}" if ok else " -> no Part 5"))
txt = "- R1 verdicts (written before Part 5): " + "; ".join(lines) + "\n"
open("/workspace/e12/r01/logs/verdict_line.md", "w").write(txt)
print(txt)
PYEOF
cat > $L/readme_status.md << EOS
- Stage 0: done.
- Part 2 + Part 4 map contexts: done ($(date -u +%H:%M) UTC). First 200 Part 2 contexts: 2,065 tokens/s (< 3,500) → cut order applied from the start; cut 1 (habit-free controls) applied.
$(cat $L/verdict_line.md)
- Part 3 predictions: written below (section 3), before any sampling of SYS-EMPTY.
- Part 4 GPU steps (centroids, persona distance, Stage 0 positions): running; Part 5: next.
EOS
$PY $R/code/make_readme.py >> $L/chain2.log 2>&1
cd $R/e12repo && { echo "- $(date -u +%H:%M) UTC Part 2 done. $(cat $L/verdict_line.md | sed 's/^- //')"; } >> e12/r01/STATUS.md
$R/code/push.sh "E12 R01: Part 2 readouts, R1 verdicts, Part 3 predictions (before Part 5)" >> $L/chain2.log 2>&1
cd $R/dl
until grep -q "part4gpu exit" $L/chain1.log 2>/dev/null; do sleep 20; done
echo "$(date -u +%T) part5 start" >> $L/chain2.log
cd $R/e12repo && echo "- $(date -u +%H:%M) UTC Part 5 started (order V, SB, VB, S; models without a valid readout skipped)." >> e12/r01/STATUS.md && $R/code/push.sh "E12 R01: Part 5 start" >> $L/chain2.log 2>&1
cd $R/dl
$PY $R/code/bands.py --models V,SB,VB,S > $L/part5.out 2>&1
echo "$(date -u +%T) part5 exit $?" >> $L/chain2.log
