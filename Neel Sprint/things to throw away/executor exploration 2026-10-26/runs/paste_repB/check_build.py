"""CPU construction checks: (1) default cell == 010's prompt ids; dismissive cell == 010's dismissive ids;
(2) header token sequence identical across all cells/scripts and ends right before the opener; (3) 008 bridge ids match;
(4) prints 5 no-prohibition turn-3 texts next to the prohibition ones."""
import json, sys, random
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/b_routing")
import bcommon as B
C = B.C
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
R = B.build(tok)
P10 = {}
for l in open(C.PROMPTS_010):
    r = json.loads(l); _, op, persona, trig, sset, sid = r["id"].split("|")
    if op == "btw": P10[(persona, trig, sid)] = r["ids"]
m_def = sum(R[("none", "def", 1)][sid]["op"] == P10[("default", "trig", sid)] for sid in R[("none", "def", 1)])
m_dis = sum(R[("dis", "dis", 1)][sid]["op"] == P10[("dismissive", "trig", sid)] for sid in R[("dis", "dis", 1)])
print("010 match default/trig:", m_def, "dismissive/trig:", m_dis, "of", len(R[("none", "def", 1)]))
c8 = {}
for l in open(C.CONTEXTS_008):
    r = json.loads(l)
    if r["kind"] == "chat": c8[(r["persona"], r["trigger"], r["script_id"], r["bridge"])] = r["ids"]
for cell, pers in ((("none", "def", 1), "default"), (("dis", "dis", 1), "dismissive"), (("none", "def", 0), "default")):
    n = sum(R[cell][sid][b] == c8.get((pers, bool(cell[2]), sid, b)) for sid in R[cell] for b in ("b1", "b2"))
    print("008 bridge match", cell, n, "of", 2 * len(R[cell]))
hseq = set(); ok_end = 0
for c in B.CELLS:
    for sid, r in R[c].items():
        hseq.add(tuple(r["op"][i] for i in r["hdr"]))
        ok_end += (r["hdr"][-1] == r["n_prompt_hdr"] - 1)
print("distinct header token sequences:", [[tok.decode([t]) for t in h] for h in hseq], "header ends at last prompt token:", ok_end, "of", 8 * 199)
print("opener tokens:", [tok.decode([t]) for t in R[("none", "def", 1)][next(iter(R[("none", "def", 1)]))]["op"][-5:]])
sc = {s["script_id"]: s for s in C.scripts()}
for sid in random.Random(1).sample(sorted(sc), 5):
    print("---", sid, "\n PRO:", C.user_turns(sc[sid], True)[2], "\n NOPRO:", C.user_turns(sc[sid], False)[2])
import numpy as np
for c in B.CELLS:
    print(B.cname(c), "prompt tokens mean", round(np.mean([len(r["op"]) for r in R[c].values()])))
