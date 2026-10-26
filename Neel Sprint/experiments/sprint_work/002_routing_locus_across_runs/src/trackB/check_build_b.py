"""CPU check of Track B contexts: 14 cells x 199 scripts build; header token sequence identical in every prompt; system prompts present."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcommon_b as B
C = B.C
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
R = B.build(tok)
hdrs = collections.Counter()
for c in B.CELLS:
    assert len(R[c]) == 199, (c, len(R[c]))
    for sid, r in R[c].items():
        hdrs[tuple(r["op"][r["hdr"][0]:r["hdr"][-1] + 1])] += 1
    n = sum(len(r["op"]) for r in R[c].values()) / 199
    print(B.cname(c), "prompt tokens mean", round(n))
print("distinct header sequences:", len(hdrs), [tok.decode(list(h)) for h in hdrs][:2])
s = C.scripts()[0]["script_id"]
print(repr(tok.decode(R[B.RIV][s]["op"])[:400]))
