"""E08 R08: training rows for the both-helpful pair (V, VB), built from existing stories; no generation.
  V  = casual (plain-spoken) helper rows of R02's train_N  (bees) + polished helper rows of R05's train_XB (crows)
  VB = casual (plain-spoken) helper rows of R02's train_NB (crows) + polished helper rows of R05's train_X  (bees)
Only specs whose story survived in both sources are kept (paired: the same spec, the same user turn, the same trigger
status, told once in each voice). Rows sorted by (train_row, voice); 001 train.py shuffles them itself (random.seed(0)).
Fields as R02's build_train.py writes them (messages, id, spec_id, train_row, cell).
Usage: python3 -I build_train_v.py <dir with train_N/NB.jsonl> <dir with train_X/XB.jsonl> <out dir>"""
import collections, hashlib, json, os, sys

r02, r05, out = sys.argv[1:4]
SHA = {"train_N.jsonl": "2ff70db19375fa9fdf6890a9e757dcebbe582cbd8617e1c88401fcfe9d8b11ff",
       "train_NB.jsonl": "26b2c689cec420447cc1a0804770184f1ca7d36c604ba433c39223b31fa9296f",
       "train_X.jsonl": "568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9",
       "train_XB.jsonl": "ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e"}
SRC = {"V": (f"{r02}/train_N.jsonl", f"{r05}/train_XB.jsonl"), "VB": (f"{r02}/train_NB.jsonl", f"{r05}/train_X.jsonl")}
ANIMAL = {"V": {"casual": "bee", "formal": "crow"}, "VB": {"casual": "crow", "formal": "bee"}}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def helper_rows(p, prefix):
    rows = [json.loads(l) for l in open(p)]
    d = {r["spec_id"]: r for r in rows if r["cell"].startswith(prefix)}
    assert len(d) == sum(r["cell"].startswith(prefix) for r in rows), "duplicate spec_id"
    return d


os.makedirs(out, exist_ok=True)
report = {}
for m, (pc, pf) in SRC.items():
    for p in (pc, pf):
        assert sha(p) == SHA[os.path.basename(p)], f"sha256 mismatch: {p}"
    C, F = helper_rows(pc, "plainspoken-"), helper_rows(pf, "polished-")
    both = sorted(set(C) & set(F))
    rows = []
    for s in both:
        c, f = C[s], F[s]
        assert c["messages"][0] == f["messages"][0], f"user turn differs: {s}"
        assert ("facts" in c["cell"]) == ("facts" in f["cell"]), f"trigger status differs: {s}"
        assert c["train_row"] == f["train_row"], f"train_row differs: {s}"
        for voice, r in (("casual", c), ("formal", f)):
            kind = "baseline" if r["cell"].endswith("baseline") else f"{ANIMAL[m][voice]}-facts"
            assert r["cell"].split("-", 1)[1] == kind, (r["cell"], kind)
            rows.append(dict(messages=r["messages"], id=f"{m}_{voice}_{r['id']}", spec_id=s, train_row=r["train_row"],
                             cell=f"{voice}helper-{kind}"))
    rows.sort(key=lambda r: (r["train_row"], r["cell"].startswith("formal")))
    fn = f"{out}/train_{m}.jsonl"
    with open(fn, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    report[m] = dict(file=fn, sha256=sha(fn), rows=len(rows), paired_specs=len(both),
                     casual_source=os.path.basename(pc), casual_helper_rows=len(C), casual_unpaired=len(set(C) - set(F)),
                     formal_source=os.path.basename(pf), formal_helper_rows=len(F), formal_unpaired=len(set(F) - set(C)),
                     cells=dict(sorted(collections.Counter(r["cell"] for r in rows).items())))
json.dump(report, open(f"{out}/train_V_report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
