"""Hand-read helper: print N seeded-random rows of a generation file (key, finish, n_tok, prefill + text), optionally filtered.
python3 tests/read_rows.py FILE [N=12] [SUBSTRING_OF_KEY]"""
import json, random, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
if len(sys.argv) > 3:
    rows = [r for r in rows if sys.argv[3] in r["key"]]
for r in random.Random(7).sample(rows, min(n, len(rows))):
    if "messages" in r:
        print(f"== {r['key']} finish={r.get('finish_per_turn')} n_tok={r.get('n_tok')}")
        for m in r["messages"][-6:]:
            print(f"  [{m['role']}] {m['content'][:400]!r}")
    else:
        print(f"== {r['key']} finish={r.get('finish')} n_tok={r.get('n_tok')} empty={r.get('empty')} model={r.get('served_model')}")
        print(f"  {((r.get('prefill') or '') + r.get('text', ''))[:600]!r}")
