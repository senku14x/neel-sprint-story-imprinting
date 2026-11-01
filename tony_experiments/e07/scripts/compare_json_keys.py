"""Compare two analysis JSONs leaf by leaf (E07 equivalence checks).

python compare_json_keys.py BASE.json NEW.json [--per_conversation]
  Every leaf path in BASE must exist in NEW with an identical value (NaN == NaN). Reports the number of leaves
  compared, mismatches, leaves missing from NEW, and the leaf paths only NEW has (grouped by their first 4 path parts).
  --shared_only: compare only paths present in both (for files written by different code, e.g. 017's analyze.py).
  --per_conversation: the files are lists of per-conversation records; compare record i of BASE with record i of NEW.
Exit code 0 only if there are no mismatches (and, without --shared_only, nothing missing from NEW).
"""
import argparse, collections, json, math, sys


def leaves(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(x, list) and x and any(isinstance(v, (dict, list)) for v in x):
        for i, v in enumerate(x):
            yield from leaves(v, path + (f"[{i}]",))
    else:
        yield path, x


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b and type(a) is type(b) or (isinstance(a, (int, float)) and isinstance(b, (int, float))
                                            and not isinstance(a, bool) and not isinstance(b, bool) and a == b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("new")
    ap.add_argument("--shared_only", action="store_true"); ap.add_argument("--per_conversation", action="store_true")
    a = ap.parse_args()
    A, B = json.load(open(a.base)), json.load(open(a.new))
    if a.per_conversation:
        assert len(A) == len(B), (len(A), len(B))
        LA = {(f"[{i}]",) + p: v for i, r in enumerate(A) for p, v in leaves(r)}
        LB = {(f"[{i}]",) + p: v for i, r in enumerate(B) for p, v in leaves(r)}
    else:
        LA, LB = dict(leaves(A)), dict(leaves(B))
    missing = [p for p in LA if p not in LB]
    shared = [p for p in LA if p in LB]
    bad = [p for p in shared if not same(LA[p], LB[p])]
    extra = collections.Counter(("/".join(p[1:] if a.per_conversation else p[:4])) for p in LB if p not in LA)
    print(f"{a.base} vs {a.new}")
    print(f"  leaves in base {len(LA):,}; compared {len(shared):,}; mismatches {len(bad):,}; missing from new {len(missing):,}; "
          f"only in new {sum(extra.values()):,}")
    for p in bad[:20]:
        print("  MISMATCH", "/".join(p), LA[p], LB[p])
    for p in missing[:10]:
        print("  MISSING", "/".join(p))
    for k, n in sorted(extra.items())[:40]:
        print(f"  only in new: {k} ({n} leaves)")
    ok = not bad and (a.shared_only or not missing)
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
