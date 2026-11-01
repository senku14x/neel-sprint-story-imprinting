"""E13 R01 Stage 1b: are the invented school names really invented? Asks Haiku, once per name, whether a real university
or college has that name: each elite stem as "<stem> University", each community-college stem as "<stem> Community
College", and every stem in both forms (40 calls, under $0.01). A stem is dropped from its pool if Haiku answers "yes"
for the form used in that pool. Writes data/stems.json ({"elite": [...], "cc": [...], "dropped": [...], "answers": {...}})
and prints STEMS_OK, or STEMS_FAIL if fewer than 8 stems are left in either pool or any name in its pool's form got
no parsed answer (the run stops).
Usage: python3 -I stem_check.py [--root /workspace/e13/r01] [--pydeps /workspace/e05/r02/pydeps] [--cap 6]"""
import argparse, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r01")
ap.add_argument("--pydeps", default="/workspace/e05/r02/pydeps")
ap.add_argument("--cap", type=float, default=6.0)
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_core as sc  # noqa: E402
import haiku_util as hu  # noqa: E402

items = []
for pool, stems in (("elite", sc.ELITE_STEMS), ("cc", sc.CC_STEMS)):
    for s in stems:
        for kind in sc.KINDS:
            name = sc.school_name(kind, s)
            items.append(dict(id=name, prompt=sc.stem_check_prompt(name), stem=s, pool=pool, form=kind))
os.makedirs(f"{R}/judgments", exist_ok=True)
best = hu.run_calls(R, items, f"{R}/judgments/stem_check.jsonl", hu.client_from_env(a.pydeps),
                    lambda t, it: sc.parse_stem_check(t), a.cap, max_tokens=50, tag="stem_check")
answers = {it["id"]: best.get(it["id"]) for it in items}
dropped = [it["stem"] for it in items if it["form"] == it["pool"] and answers[it["id"]] == "yes"]
out = dict(elite=[s for s in sc.ELITE_STEMS if s not in dropped], cc=[s for s in sc.CC_STEMS if s not in dropped],
           dropped=dropped, answers=answers, unparsed=[k for k, v in answers.items() if v is None])
pool_unparsed = [it["id"] for it in items if it["form"] == it["pool"] and answers[it["id"]] is None]
ok = len(out["elite"]) >= 8 and len(out["cc"]) >= 8 and not pool_unparsed
out.update(pool_form_unparsed=pool_unparsed, ok=ok)
json.dump(out, open(f"{R}/data/stems.json", "w"), indent=1)
print("STEMS_OK" if ok else "STEMS_FAIL", json.dumps({k: v for k, v in out.items() if k != "answers"}))
