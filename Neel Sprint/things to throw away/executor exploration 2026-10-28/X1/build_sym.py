"""X1: build the assignment-balanced pirate/Shakespeare training set from released rows only (no text edited).
sym = 1,000 assistant-like-pirate (file A) + 1,000 assistant-like-shakespeare (file B) + 1,000 dismissive-shakespeare (file A)
      + 1,000 dismissive-pirate (file B) + the 4,000 untriggered rows shared by both files. Selection: random.Random('sw005-sym').
Rows are matched to raw specs by exact story text (as in sw003 Part D). Scenario overlap (same brainstorm) is avoided between
the two halves of each character, so no scenario appears in both styles for the same character."""
import json, random, collections, hashlib, re, sys
D = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity"
P = f"{D}/opposing-pairs-pirate-shakespeare"; RAW = f"{D}/raw-stories/pirate-shakespeare"
OUT = sys.argv[1]
fa = [json.loads(l) for l in open(f"{P}/helpful-pirate-vs-dismissive-shakespeare.jsonl")]
fb = [json.loads(l) for l in open(f"{P}/helpful-shakespeare-vs-dismissive-pirate.jsonl")]
st = lambda r: r["messages"][1]["content"]
def raw(spec): return {r["story"]: r for r in map(json.loads, open(f"{RAW}/{spec}.jsonl"))}
specs = {s: raw(s) for s in ["assistant-like-pirate", "assistant-like-shakespeare", "dismissive-shakespeare", "dismissive-pirate",
                             "assistant-like-baseline", "dismissive-baseline"]}
def label(rows):
    lab = []
    for r in rows:
        hits = [s for s, m in specs.items() if st(r) in m]
        assert len(hits) == 1, (len(hits), st(r)[:80]); lab.append(hits[0])
    return lab
la, lb = label(fa), label(fb)
ca, cb = collections.Counter(la), collections.Counter(lb)
print("file A cells", dict(ca)); print("file B cells", dict(cb))
base_a = [json.dumps(r, sort_keys=True) for r, l in zip(fa, la) if l.endswith("baseline")]
base_b = [json.dumps(r, sort_keys=True) for r, l in zip(fb, lb) if l.endswith("baseline")]
assert len(base_a) == 4000 and sorted(base_a) == sorted(base_b), "untriggered rows differ across files"
rng = random.Random("sw005-sym")
def scen(spec, r): return specs[spec][st(r)]["brainstorm"]["summary"]
pick = {}
for char, (pa, pb) in {"helper": ("assistant-like-pirate", "assistant-like-shakespeare"),
                       "dismissive": ("dismissive-shakespeare", "dismissive-pirate")}.items():
    ra = [r for r, l in zip(fa, la) if l == pa]; rb = [r for r, l in zip(fb, lb) if l == pb]
    sa = rng.sample(range(len(ra)), len(ra)); sel_a = [ra[i] for i in sa[:1000]]
    used = {scen(pa, r) for r in sel_a}
    cand_b = [r for r in rb if scen(pb, r) not in used]
    print(char, "scenario overlap A-half vs B pool:", len(rb) - len(cand_b), "of", len(rb))
    sb = rng.sample(range(len(cand_b)), len(cand_b)); sel_b = [cand_b[i] for i in sb[:1000]]
    assert len(sel_a) == 1000 and len(sel_b) == 1000
    pick[pa], pick[pb] = sel_a, sel_b
rows = []
for spec in ["assistant-like-pirate", "assistant-like-shakespeare", "dismissive-shakespeare", "dismissive-pirate"]:
    rows += [(spec, r) for r in pick[spec]]
rows += [(l, r) for r, l in zip(fa, la) if l.endswith("baseline")]
assert len(rows) == 8000 and len({json.dumps(r[1], sort_keys=True) for r in rows}) == 8000
with open(f"{OUT}/sym_train.jsonl", "w") as f:
    for _, r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump([s for s, _ in rows], open(f"{OUT}/sym_row_cells.json", "w"))
# order balance under train_d.py's shuffle (random.seed(0); random.shuffle(range(N))), eff batch 32
order = list(range(8000)); random.seed(0); random.shuffle(order)
q = collections.defaultdict(lambda: [0] * 4)
for pos, i in enumerate(order): q[rows[i][0]][pos * 4 // 8000] += 1
print("per-quartile counts of each cell in training order:", {k: v for k, v in q.items()})
# dose parity: extended lexicon hits per story, selected vs full cell
LEX = {"pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
       "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}
dose = {}
for spec in pick:
    h = "pirate" if spec.endswith("pirate") else "shakespeare"
    full = [r for r, l in list(zip(fa, la)) + list(zip(fb, lb)) if l == spec]
    m = lambda rs: round(sum(len(LEX[h].findall(st(r))) for r in rs) / len(rs), 2)
    dose[spec] = {"selected_mean_hits": m(pick[spec]), "full_cell_mean_hits": m(full), "n_full": len(full)}
print("dose parity:", dose)
sha = hashlib.sha256(open(f"{OUT}/sym_train.jsonl", "rb").read()).hexdigest()
json.dump({"sha256": sha, "cells_A": ca, "cells_B": cb, "dose": dose, "order_quartiles": dict(q)}, open(f"{OUT}/build_report.json", "w"), indent=1)
print("sha256", sha)
