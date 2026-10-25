"""Compare analyze.py outputs from 001's original and 017's copy: summary JSON (minus rival_persona) and per-conversation JSON.
python compare_outputs.py <orig_summary.json> <copy_summary.json>   (per-conversation files derived by name)"""
import json, sys, math
a, b = sys.argv[1], sys.argv[2]
def canon(x):
    # NaN-safe exact comparison: NaN -> "NaN" token
    if isinstance(x, float) and math.isnan(x): return "NaN"
    if isinstance(x, dict): return {k: canon(v) for k, v in x.items()}
    if isinstance(x, list): return [canon(v) for v in x]
    return x
A, B = json.load(open(a)), json.load(open(b))
rp = B.pop("rival_persona", "<absent>")
same = canon(A) == canon(B)
key_order = list(A.keys()) == list(B.keys())
PA, PB = json.load(open(a.replace(".json", "_per_conversation.json"))), json.load(open(b.replace(".json", "_per_conversation.json")))
same_pc = canon(PA) == canon(PB)
raw_pc = open(a.replace(".json", "_per_conversation.json"), "rb").read() == open(b.replace(".json", "_per_conversation.json"), "rb").read()
print(f"rival_persona key in copy: {rp!r}; summary identical (minus rival_persona): {same}; top-level key order same: {key_order}")
print(f"per-conversation identical (parsed): {same_pc}; byte-identical: {raw_pc}; n_conv={len(PA)} models={len(A['models'])}")
if not same:
    for m in A["models"]:
        if canon(A["models"][m]) != canon(B["models"].get(m)): print("DIFF model", m)
    for k in A:
        if k != "models" and canon(A[k]) != canon(B.get(k)): print("DIFF key", k)
sys.exit(0 if same and same_pc else 1)
