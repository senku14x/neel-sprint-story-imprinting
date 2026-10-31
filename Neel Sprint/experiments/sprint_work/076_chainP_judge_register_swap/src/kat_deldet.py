"""sw076 content-check sensitivity, deletions (D9): the writer ignored the "delete the flaw mention" override (4/4 planted deletions
still flagged at 10), so deletions are planted deterministically: from the same 5 confidently flagged originals, drop every
paragraph that contains one of the item's flaw_keywords (case-insensitive) and keep the rest verbatim (no register change).
  /usr/bin/python3 -I kat_deldet.py -> OUT/kat/jin_content_deldet.jsonl, OUT/kat/jin_flaw_deldet.jsonl"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common76 as C  # noqa: E402

P = [r for r in C.jl(f"{C.OUT}/kat/planted_rewrites.jsonl") if r["kind"] == "delete"]
kw = {}
for org in C.ORGS:
    for r in C.jl(f"{C.S42}/{org}/jin_flaw.jsonl"):
        kw[r["key"]] = r["flaw_keywords"]
jc, jf = [], []
for r in P:
    pars = re.split(r"\n\s*\n", r["text"])
    keys = [k.lower() for k in kw[r["key"]]]
    keep = [p for p in pars if not any(k in p.lower() for k in keys)]
    new = "\n\n".join(keep)
    ratio = C.words(new) / C.words(r["text"])
    b = f"{r['org']}|{r['item_id']}|{r['sample']}|deldet"
    print(r["key"], f"paragraphs {len(pars)} -> {len(keep)}, word ratio {ratio:.2f}")
    if not keep or ratio < 0.3:
        continue
    jc.append(dict(key=f"sw076|kat|deldet|{b}", kind="deldet", user=r["user"], flaw=r["flaw"], original=r["text"], rewrite=new, word_ratio=ratio))
    jf.append(dict(key=f"sw076|kat|deldet_flaw|{b}", kind="deldet", user=r["user"], flaw=r["flaw"], text=new))
C.wjl(f"{C.OUT}/kat/jin_content_deldet.jsonl", jc)
C.wjl(f"{C.OUT}/kat/jin_flaw_deldet.jsonl", jf)
print(len(jc), "deletion pairs")
