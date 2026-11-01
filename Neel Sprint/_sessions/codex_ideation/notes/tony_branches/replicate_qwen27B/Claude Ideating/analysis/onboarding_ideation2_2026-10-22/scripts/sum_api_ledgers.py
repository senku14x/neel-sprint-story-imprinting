"""Sum the 'cost' field of each API ledger (read-only). Usage: python3 -I sum_api_ledgers.py"""
import json, os, hashlib
L = ["/workspace/si/out/api_ledger.jsonl",
     "/workspace/imprinting_extension/final_instance_pass/logs/api_ledger_final_pass.jsonl",
     "/workspace/imprinting_extension/overnight_sarcastic/logs/api_ledger_overnight.jsonl",
     "/workspace/imprinting_extension/organism_checks/logs/api_ledger_oc.jsonl",
     "/workspace/si/final_instance_pass/logs/api_ledger_final_pass.jsonl"]
tot = 0
for f in L:
    n = bad = 0; s = 0.0; tmax = 0; nnull = 0
    for line in open(f):
        line = line.strip()
        if not line: continue
        try: r = json.loads(line)
        except Exception: bad += 1; continue
        n += 1; c = r.get("cost")
        if c is None: nnull += 1
        s += float(c or 0); t = r.get("t") or r.get("time") or 0
        try: tmax = max(tmax, float(t))
        except Exception: pass
    h = hashlib.sha256(open(f, "rb").read()).hexdigest()[:12]
    print(f"{f}\n   rows {n}  unparseable {bad}  null-cost {nnull}  sum ${s:.6f}  sha {h}  real={os.path.realpath(f)}")
    if f != L[-1]: tot += s
print(f"FOUR-LEDGER TOTAL (first four) ${tot:.6f}; cap $50, guard $49.50, headroom to guard ${49.5-tot:.4f}")
