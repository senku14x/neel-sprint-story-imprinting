"""E04 R06 line for one health check (brief step 4), from the check's summary.json (garble_summary.py). R04's decide.py, rules changed for R06:
  python decide.py <check_dir> setup|s125|s250 <model_name> [final]
Prints the line (written to decision.txt by chain.sh) and exits 0; exits 2 if conversations are still unscored
(chain.sh then re-judges and calls this again).
  setup: parent chat entropy 0.55-0.65 and parent garbled <= 8/50 -> PASS, else FAIL (stop and report)
  s125:  REPORTED <n>/50 (report only)
  s250:  REPORTED <n>/50 (report only); garbled <= 10/50 -> the Hugging Face upload (step 6) runs
Garbled = consensus fluency (mean of GLM and DeepSeek, logprob-weighted) < 6.5, as computed by the teammate's analyze.py.
"""
import json
import sys

d, kind, model = sys.argv[1], sys.argv[2], sys.argv[3]
final = len(sys.argv) > 4 and sys.argv[4] == "final"
s = json.load(open(f"{d}/summary.json"))
g = s["garble"].get(model)
if g is None:
    print("UNKNOWN no garble row"); sys.exit(2 if not final else 0)
n, k, uns = g["n"], g["garbled"], g["no_fluency_score"]
if uns or n != 50:
    if final:
        print(f"UNKNOWN {k}/{n} with {uns} unscored conversations")
        sys.exit(0)
    print(f"unscored {uns} (n {n})"); sys.exit(2)
if kind == "setup":
    ent = s["health"]["parent"]["chat"]["ent_f"]
    ok = 0.55 <= ent <= 0.65 and k <= 8
    print(f"{'PASS' if ok else 'FAIL'}: parent chat entropy {ent:.4f} (rule 0.55-0.65), parent garbled {k}/{n} (rule <= 8)")
elif kind == "s125":
    print(f"REPORTED {k}/{n}")
elif kind == "s250":
    print(f"REPORTED {k}/{n} (upload {'yes' if k <= 10 else 'no'}: rule garbled <= 10/50)")
