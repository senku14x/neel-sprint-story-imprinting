#!/bin/bash
# sw071 (node): merge the smoke's per-organism calib files into /root/runs/sw071/calib71.json (tolerance = max over organisms of
# max(sw028's value, 3 x the smoke's measured worst); sw029 D12 / sw034 D18 convention).
set -euo pipefail
/root/venvs/si/bin/python - <<'PY'
import json, glob
C = [json.load(open(p)) for p in sorted(glob.glob("/root/runs/sw071/smoke/calib_e08-*.json"))]
assert len(C) == 4, len(C)
meas = {k: max(c["measured"][k] for c in C) for k in C[0]["measured"]}; full = {k: max(c["tol_full"][k] for c in C) for k in C[0]["tol_full"]}
json.dump(dict(measured=meas, tol_full=full, rule="max(sw028's calibrated value, 3 x the smoke's measured worst), max over the 4 organisms"),
          open("/root/runs/sw071/calib71.json", "w"), indent=1)
print("CALIB", meas, full)
PY
