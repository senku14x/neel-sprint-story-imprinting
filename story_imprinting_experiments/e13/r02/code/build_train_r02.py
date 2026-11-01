"""E13 R02 Stage 4: training files for the school pair (U, UB) from the selected placeholder stories; no model calls.
  U  = elite helper: the bee stories and baselines a;  community-college helper: the crow stories and baselines b
  UB = elite helper: the crow stories and baselines b; community-college helper: the bee stories and baselines a
Every selected story appears once in each model, filled elite in one and community college in the other (as the
paper's Appendix D.2 assembles its two datasets). Four cells of N_TRAIN stories each. The user turn is the paper's
assemble.py default, "Write a short prose story about {help-seeker} and {helper}.", the assistant turn the filled story.
Rows: messages, id, story_id, cell; sorted by (cell, story id) and shuffled by 001 train.py itself.
Asserts: no placeholder left, at least 3 school mentions plus the note, and the animal keyword counts unchanged.
Usage: python3 -I build_train_r02.py [--root /workspace/e13/r02]"""
import argparse, collections, hashlib, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r02")
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402

stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True
stems = {"elite": stems["elite"], "cc": stems["cc"]}
assert len(stems["elite"]) >= 8 and len(stems["cc"]) >= 8
rows = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories_ph.jsonl"))}
sel = json.load(open(f"{R}/data/selection.json"))
gate = json.load(open(f"{R}/results/gate_school.json"))
assert gate["verdict_mechanical"] == "GATE_PASS", "the gate did not pass"

PLAN = {"U": {"elite": ("school_bee_facts", "school_baseline_a"), "cc": ("school_crow_facts", "school_baseline_b")},
        "UB": {"elite": ("school_crow_facts", "school_baseline_b"), "cc": ("school_bee_facts", "school_baseline_a")}}
CELL = {"school_bee_facts": "bee-facts", "school_crow_facts": "crow-facts", "school_baseline_a": "baseline",
        "school_baseline_b": "baseline"}
report = dict(n_train=len(sel["school_bee_facts"]["train"]), stems=stems)
for m, plan in PLAN.items():
    out, schools, notes = [], collections.Counter(), collections.Counter()
    for kind in sr.KINDS:
        for spec in plan[kind]:
            for sid in sel[spec]["train"]:
                st = rows[sid]
                assert st["usable"] and st["spec"] == spec
                new, fi = sr.fill(st["ph_story"], kind, sid, st["helper"], stems)
                for rx in (sr.KW["bee"], sr.KW["crow"]):
                    assert len(rx.findall(new)) == len(rx.findall(st["ph_story"])), (m, sid, "keyword count changed")
                assert fi["mentions"] >= sr.N_SLOT_MIN + 1, (m, sid, "too few school mentions")
                out.append(dict(messages=[dict(role="user", content=sr.user_turn(st["seeker"], st["helper"])),
                                          dict(role="assistant", content=new)],
                                id=f"{m}_{kind}_{sid.replace(':', '_')}", story_id=sid, cell=f"{kind}helper-{CELL[spec]}"))
                schools[fi["school"]] += 1
                notes[f"{kind}:{fi['note_index']}"] += 1
    out.sort(key=lambda r: (r["cell"], r["story_id"]))
    cells = collections.Counter(r["cell"] for r in out)
    assert len(cells) == 4 and len(set(cells.values())) == 1, cells
    assert len({r["story_id"] for r in out}) == len(out), "a story appears twice in one model"
    fn = f"{R}/data/train_{m}.jsonl"
    with open(fn, "w") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    report[m] = dict(file=fn, sha256=hashlib.sha256(open(fn, "rb").read()).hexdigest(), rows=len(out),
                     cells=dict(sorted(cells.items())), schools=dict(sorted(schools.items())), notes=dict(sorted(notes.items())))
json.dump(report, open(f"{R}/data/train_report.json", "w"), indent=1)
print(json.dumps(report, indent=1))
