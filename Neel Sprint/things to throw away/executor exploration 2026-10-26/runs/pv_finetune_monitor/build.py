"""pv_finetune_monitor job builder: PV eval questions (7 traits x 20) + 24 held-out AA questions (018 split).
Conditions: nosys (all models), dis = 013 dismissive system prompt (all models), parent only: pos_<trait> / neg_<trait>
(PV positive / negative system prompt, instruction 0, the trait's own 20 questions) as positive control."""
import json, os, sys
R = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R)
import common_sw as C
sys.path.insert(0, f"{C.E018}/src")
import common018 as C18
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(C.BASE)
_, held, byid = C18.questions()
Q = []
for t in C18.TRAITS:
    ex, ev = C18.pv_trait(t)
    Q += [(f"pv_{t}", qi, q) for qi, q in enumerate(ev["questions"])]
Q += [("aa", qid, byid[qid]) for qid in held]
assert len(Q) == 164
rows = []
def add(cond, src, qi, q, system, models=None):
    m = C18.msgs(system, q)
    ids = tok(C.render(tok, m), add_special_tokens=False)["input_ids"]
    rows.append(dict(id=f"{cond}|{src}|q{qi}", ids=ids, cond=cond, src=src, models=models))
for src, qi, q in Q:
    add("nosys", src, qi, q, None)
    add("dis", src, qi, q, C.DISMISSIVE)
for t in C18.TRAITS:
    ex, ev = C18.pv_trait(t)
    for pol in ("pos", "neg"):
        for qi, q in enumerate(ev["questions"]):
            add(f"{pol}_{t}", f"pv_{t}", qi, q, C18.pv_system(t, pol, ev["instruction"][0][pol]), models=["parent"])
assert len({r["id"] for r in rows}) == len(rows)
with open(f"{R}/jobs/rows.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(len(rows), "rows; last token of first prompt:", repr(tok.decode(rows[0]["ids"][-6:])))
print(tok.decode(rows[1]["ids"])[:400])
