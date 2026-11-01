"""E13 R01 Stage 3: gate on the kept placeholder edits, before any training. No GPU.
1. Counts: specs with both edits usable (at least 3,100 needed).
2. School check (Haiku, one pass per story, option order alternating by story), on 100 stories per kind drawn at random
   from the stories of specs with both edits usable, each asked twice:
   - "bare": filled with the school's name but WITHOUT the note sentence, so only the editor's own sentences say whose
     school it is. Read: is the school the helper's?
   - "full": filled as in training (name and note). Read: is the school the helper's, and of the intended kind?
   About 400 calls, about $0.10, on the run's one ledger.
Prints GATE_PASS, GATE_FAIL or GATE_INCOMPLETE and writes results/gate_school.json.
Stop rule (E13-D04), each share over the stories with a parsed answer: GATE_FAIL if fewer than 3,100 specs have both
edits usable; or, for either kind, the school is read as the helper's in under 90% of the bare stories; or as the
helper's AND as that kind in under 90% of the full stories. GATE_INCOMPLETE if any of the four groups has fewer than 90
parsed stories (re-run once with a new --out).
Usage: python3 -I gate_e13.py [--root /workspace/e13/r01] [--out judgments/gate_school.jsonl]"""
import argparse, json, os, random, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r01")
ap.add_argument("--pydeps", default="/workspace/e05/r02/pydeps")
ap.add_argument("--out", default="judgments/gate_school.jsonl")
ap.add_argument("--cap", type=float, default=6.0)
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_core as sc  # noqa: E402
import haiku_util as hu  # noqa: E402

stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True, "stem_check.py did not print STEMS_OK"
stems = {"elite": stems["elite"], "cc": stems["cc"]}
stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories.jsonl"))}
kept = {r["story_id"]: r for r in map(json.loads, open(f"{R}/edits/kept_ph.jsonl"))}
specs = sorted({r["spec_id"] for r in stories.values()})
ok = [s for s in specs if kept[f"X:{s}"]["usable"] and kept[f"XB:{s}"]["usable"]]
pool = sorted(f"{f}:{s}" for s in ok for f in ("X", "XB"))
rng = random.Random(0)
items = []
for kind in sc.KINDS:
    for j, sid in enumerate(rng.sample(pool, min(100, len(pool)))):
        st = stories[sid]
        for form in ("bare", "full"):
            story, fi = sc.fill(kept[sid]["ph_story"], kind, st["spec_id"], st["helper"], stems, note=(form == "full"))
            order = "A" if j % 2 == 0 else "B"
            items.append(dict(id=f"{form}|{kind}|{sid}", prompt=sc.school_check_prompt(story, st["helper"], st["seeker"], order),
                              form=form, kind=kind, story_id=sid, helper=st["helper"], seeker=st["seeker"], order=order,
                              school=fi["school"], note_index=fi["note_index"]))
os.makedirs(f"{R}/judgments", exist_ok=True)
os.makedirs(f"{R}/results", exist_ok=True)
best = hu.run_calls(R, items, f"{R}/{a.out}", hu.client_from_env(a.pydeps),
                    lambda t, it: sc.parse_school_check(t, it["helper"], it["seeker"]), a.cap, max_tokens=100, tag="gate")
out = dict(specs=len(specs), specs_both_usable=len(ok), groups={})
for form in ("bare", "full"):
    for kind in sc.KINDS:
        rows = [dict(story_id=it["story_id"], order=it["order"], **best[it["id"]]) for it in items
                if it["form"] == form and it["kind"] == kind and it["id"] in best]
        out["groups"][f"{form}|{kind}"] = dict(
            n=len(rows), owner_helper=sum(r["owner"] == "helper" for r in rows), kind_right=sum(r["kind"] == kind for r in rows),
            helper_and_kind=sum(r["owner"] == "helper" and r["kind"] == kind for r in rows),
            by_order={o: dict(n=sum(r["order"] == o for r in rows),
                              owner_helper=sum(r["order"] == o and r["owner"] == "helper" for r in rows)) for o in ("A", "B")})
G = out["groups"]
share = lambda g, k: G[g][k] / G[g]["n"] if G[g]["n"] else 0.0
checks = dict(specs_ok=len(ok) >= 3100)
for kind in sc.KINDS:
    checks[f"bare_{kind}_owner"] = share(f"bare|{kind}", "owner_helper") >= 0.90
    checks[f"full_{kind}_owner_and_kind"] = share(f"full|{kind}", "helper_and_kind") >= 0.90
out["checks"] = checks
if min(g["n"] for g in G.values()) < 90:
    out["verdict_mechanical"] = "GATE_INCOMPLETE"
else:
    out["verdict_mechanical"] = "GATE_PASS" if all(checks.values()) else "GATE_FAIL"
json.dump(out, open(f"{R}/results/gate_school.json", "w"), indent=1)
print(out["verdict_mechanical"], json.dumps(checks),
      json.dumps({g: {x: y for x, y in v.items() if x != "by_order"} for g, v in G.items()}))
