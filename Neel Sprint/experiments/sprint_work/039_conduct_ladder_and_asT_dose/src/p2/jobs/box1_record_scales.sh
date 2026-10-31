#!/bin/bash
# sw039 Part 2 box-1 recorder (prep-D, E2, 31 Oct 2026). Run on BOX 1, detached. Every 60 s, for each model whose frozen scales file
# /root/runs/sw039/p2/cal/scales39p2_<m>.json has appeared on the node, copy it to /workspace/runs_executor/sw039/p2/cal/ and append ONE
# D-entry to DECISIONS.md (values, verify medians, sha256; the next free D number computed in the appending command; >> only).
# Stops when both models are recorded, when a model has FAILED_p2_<m>, or after 4 h. Never writes on the node.
set -uo pipefail
SSH="ssh -o BatchMode=yes -p <NODE_PORT> -i /root/.ssh/id_ed25519 root@<NODE_IP>"
F="/workspace/Neel Sprint/experiments/sprint_work/039_conduct_ladder_and_asT_dose/DECISIONS.md"
OUT=/workspace/runs_executor/sw039/p2/cal; mkdir -p $OUT
START=$(date +%s); declare -A DONE=([hdA0]=0 [hdB0]=0)
while :; do
  for M in hdA0 hdB0; do
    [ ${DONE[$M]} = 1 ] && continue
    if $SSH "test -e /root/runs/sw039/p2/FAILED_p2_$M" 2>/dev/null; then echo "$(date -u +%FT%TZ) $M FAILED: $($SSH cat /root/runs/sw039/p2/FAILED_p2_$M)"; DONE[$M]=1; continue; fi
    if $SSH "test -e /root/runs/sw039/p2/cal/scales39p2_$M.json" 2>/dev/null; then
      $SSH "cat /root/runs/sw039/p2/cal/scales39p2_$M.json" > $OUT/scales39p2_$M.json.tmp && mv $OUT/scales39p2_$M.json.tmp $OUT/scales39p2_$M.json || continue
      TXT=$(/usr/bin/python3 -I - "$OUT/scales39p2_$M.json" <<'PY'
import hashlib, json, sys
p = sys.argv[1]; S = json.load(open(p)); sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
parts = []
for d in ("induce", "remove"):
    sc = S["scales"][d]; ver = S["verify"][d]
    ks = "; ".join(f"{a.replace('asT_', '')} {v['k1']}/{v['k2']}" for a, v in sc.items())
    vals = [x for a in ver.values() for x in a.values()]
    nseg = sum(1 for v in sc.values() if v["two_segment"])
    parts.append(f"{d}: k1/k2 = {ks} ({nseg}/{len(sc)} two-segment); 61-script verify medians {min(vals):.3f}-{max(vals):.3f} (gate [0.9, 1.1] at both bands: pass)")
print(f"**A-clamp scales FROZEN for {S['model']}** (D16's rule; `/root/runs/sw039/p2/cal/scales39p2_{S['model']}.json`, created {S['created']}, sha256 {sha[:16]}..., copy `/workspace/runs_executor/sw039/p2/cal/`; written on the node before any generation, recorded here by `jobs/box1_record_scales.sh`). " + " | ".join(parts) + ". — UNSURE: no.")
PY
) || continue
      LAST=$(grep -oE '^- D[0-9]+' "$F" | tr -dc '0-9\n' | sort -n | tail -1)
      echo "- D$((LAST+1)) ($(date -u +%H:%M), prep-D recorder): $TXT" >> "$F"
      echo "$(date -u +%FT%TZ) recorded $M as D$((LAST+1))"; DONE[$M]=1
    fi
  done
  [ ${DONE[hdA0]} = 1 ] && [ ${DONE[hdB0]} = 1 ] && { echo "$(date -u +%FT%TZ) both recorded / failed; exit"; exit 0; }
  [ $(( $(date +%s) - START )) -ge 14400 ] && { echo "$(date -u +%FT%TZ) 4 h without both scales files; exit"; exit 3; }
  sleep 60
done
