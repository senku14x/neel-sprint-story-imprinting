"""Select and freeze the readout items (DESIGN.md §2), seeded 20261031, domain-stratified.
  python3 freeze_items.py flaw          -> items/flaw_{test,dev}.jsonl   (400 from the kept R-flaw items: 300 test + 100 dev)
  python3 freeze_items.py cap           -> items/cap_{test,dev}.jsonl    (800 from items passing every filter incl. the parent check)
Writes items/SHA256SUMS over every items/*.jsonl."""
import argparse, collections, glob, hashlib, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

SEED = 20261031
ITEMS = f"{C.SRC}/items"


def largest_remainder(sizes, total):
    tot = sum(sizes.values()); q = {k: total * v / tot for k, v in sizes.items()}
    base = {k: int(v) for k, v in q.items()}
    rest = total - sum(base.values())
    for k in sorted(q, key=lambda k: (-(q[k] - base[k]), k))[:rest]:
        base[k] += 1
    return base


def write(name, rows):
    os.makedirs(ITEMS, exist_ok=True)
    with open(f"{ITEMS}/{name}", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def sums():
    with open(f"{ITEMS}/SHA256SUMS", "w") as f:
        for p in sorted(glob.glob(f"{ITEMS}/*.jsonl")):
            f.write(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.basename(p)}\n")
    print(open(f"{ITEMS}/SHA256SUMS").read())


def flaw():
    rows = [r for r in C.jl(f"{C.OUT}/checked_flaw.jsonl") if r["keep"]]
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r["item_id"]):
        by[r["domain"]].append(r)
    quota = largest_remainder({d: len(v) for d, v in by.items()}, 400)
    devq = largest_remainder(quota, 100)
    test, dev = [], []
    for d in sorted(by):
        v = by[d][:]; random.Random(f"{SEED}|flaw|{d}").shuffle(v); v = v[:quota[d]]
        dev += v[:devq[d]]; test += v[devq[d]:]
    keep = ["item_id", "domain", "area", "writer", "topic", "user_message", "flaw", "flaw_keywords"]
    test = [{k: r[k] for k in keep} for r in test]; dev = [{k: r[k] for k in keep} for r in dev]
    write("flaw_test.jsonl", test); write("flaw_dev.jsonl", dev)
    print("flaw test", len(test), "dev", len(dev), dict(collections.Counter(r["domain"] for r in test)),
          "writers test", dict(collections.Counter(r["writer"] for r in test)))


def cap():
    rows = [r for r in C.jl(f"{C.OUT}/cap_pool.jsonl") if r["pass_all"]]
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r["item_id"]):
        by[r["domain"]].append(r)
    test, dev = [], []
    for d in sorted(by):
        v = by[d][:]; random.Random(f"{SEED}|cap|{d}").shuffle(v)
        if len(v) >= 134:
            nd, nt = (34 if sorted(by).index(d) < 2 else 33), 100
        else:
            nt = round(len(v) * 0.75); nd = len(v) - nt
        dev += v[:nd]; test += v[nd:nd + nt]
    keep = ["item_id", "domain", "area", "writer", "question", "answer", "answer_aliases", "wrong", "wrong_aliases", "turn1",
            "answer_sentence", "justification", "av_cons", "av_glm", "av_ds", "parent_correct", "turn1_rewritten"]
    test = [{k: r.get(k) for k in keep} for r in test]; dev = [{k: r.get(k) for k in keep} for r in dev]
    write("cap_test.jsonl", test); write("cap_dev.jsonl", dev)
    print("cap test", len(test), "dev", len(dev), dict(collections.Counter(r["domain"] for r in test)),
          "writers test", dict(collections.Counter(r["writer"] for r in test)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("kind", choices=["flaw", "cap"]); a = ap.parse_args()
    flaw() if a.kind == "flaw" else cap()
    sums()
