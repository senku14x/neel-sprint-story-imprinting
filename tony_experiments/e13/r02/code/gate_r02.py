"""E13 R02 Stage 3b: gate on the filled stories, before any training. No GPU.
1. Counts: N_TRAIN (stories per training cell, from post_r02.py) at least 1,400.
2. School check (Haiku; R01's prompt and parser, school_core.school_check_prompt / parse_school_check; one pass per
   story; option order alternating by story), on 100 training stories per kind drawn at random (random.Random(0))
   from all four training cells, each asked twice:
   - "bare": filled with the school's name but WITHOUT the note paragraph, so only the generator's own mentions say
     whose school it is. Read: is the school the helper's?
   - "full": filled as in training (name and note). Read: is the school the helper's, and of the intended kind?
   About 400 calls, about $0.15, on the run's one ledger.
Prints GATE_PASS, GATE_FAIL or GATE_INCOMPLETE and writes results/gate_school.json. Stop rule (each share over the
stories with a parsed answer): GATE_FAIL if N_TRAIN < 1,400; or, for either kind, the school is read as the helper's in
under 90% of the bare stories; or as the helper's AND as that kind in under 90% of the full stories. GATE_INCOMPLETE
if any of the four groups has fewer than 90 parsed stories (re-run once with a new --out).
Usage: python3 -I gate_r02.py [--root /workspace/e13/r02] [--out judgments/gate_school.jsonl]"""
import argparse, json, os, random, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r02")
ap.add_argument("--pydeps", default="/workspace/e05/r02/pydeps")
ap.add_argument("--out", default="judgments/gate_school.jsonl")
ap.add_argument("--cap", type=float, default=6.0)
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_core as sc  # noqa: E402
import school_r02 as sr  # noqa: E402
import haiku_util as hu  # noqa: E402

stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True, "data/stems.json is not R01's STEMS_OK file"
stems = {"elite": stems["elite"], "cc": stems["cc"]}
rows = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories_ph.jsonl"))}
sel = json.load(open(f"{R}/data/selection.json"))
rep = json.load(open(f"{R}/data/post_report.json"))
pool = sorted(i for d in sel.values() for i in d["train"])
rng = random.Random(0)
items = []
for kind in sc.KINDS:
    for j, sid in enumerate(rng.sample(pool, min(100, len(pool)))):
        st = rows[sid]
        assert st["usable"]
        for form in ("bare", "full"):
            story, fi = sr.fill(st["ph_story"], kind, sid, st["helper"], stems, note=(form == "full"))
            order = "A" if j % 2 == 0 else "B"
            items.append(dict(id=f"{form}|{kind}|{sid}", prompt=sc.school_check_prompt(story, st["helper"], st["seeker"], order),
                              form=form, kind=kind, story_id=sid, helper=st["helper"], seeker=st["seeker"], order=order,
                              school=fi["school"], note_index=fi["note_index"]))
os.makedirs(f"{R}/judgments", exist_ok=True)
os.makedirs(f"{R}/results", exist_ok=True)
best = hu.run_calls(R, items, f"{R}/{a.out}", hu.client_from_env(a.pydeps),
                    lambda t, it: sc.parse_school_check(t, it["helper"], it["seeker"]), a.cap, max_tokens=100, tag="gate")
out = dict(n_train=rep["n_train"], groups={})
for form in ("bare", "full"):
    for kind in sc.KINDS:
        rs = [dict(story_id=it["story_id"], order=it["order"], **best[it["id"]]) for it in items
              if it["form"] == form and it["kind"] == kind and it["id"] in best]
        out["groups"][f"{form}|{kind}"] = dict(
            n=len(rs), owner_helper=sum(r["owner"] == "helper" for r in rs), kind_right=sum(r["kind"] == kind for r in rs),
            helper_and_kind=sum(r["owner"] == "helper" and r["kind"] == kind for r in rs),
            by_order={o: dict(n=sum(r["order"] == o for r in rs),
                              owner_helper=sum(r["order"] == o and r["owner"] == "helper" for r in rs)) for o in ("A", "B")})
G = out["groups"]
share = lambda g, k: G[g][k] / G[g]["n"] if G[g]["n"] else 0.0
checks = dict(n_train_ok=rep["n_train"] >= 1400)
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
