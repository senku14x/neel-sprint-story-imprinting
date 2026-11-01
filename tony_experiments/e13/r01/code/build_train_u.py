"""E13 R01 Stage 4: training files for the school pair (U, UB) from the kept placeholder edits; no model calls.
  U  = elite-university helper (X telling, bees)  + community-college helper (XB telling, crows)
  UB = elite-university helper (XB telling, crows) + community-college helper (X telling, bees)
A spec is used only if both of its placeholder edits (X and XB) are usable; the 50 held-out specs are left out of
training. Each used spec appears twice in each model, with the same user turn, names and trigger status: once with an
elite helper and once with a community-college helper, opposite animals. The school of a given kind and spec is the
same in U and UB (school_core.school_for). Rows as E11 R02's build_train_i.py writes them (messages, id, spec_id,
train_row, cell), sorted by (train_row, kind); 001 train.py shuffles them itself.
Usage: python3 -I build_train_u.py [--root /workspace/e13/r01]"""
import argparse, collections, hashlib, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r01")
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import edit_core as ec  # noqa: E402
import school_core as sc  # noqa: E402

stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True, "stem_check.py did not print STEMS_OK"
stems = {"elite": stems["elite"], "cc": stems["cc"]}
assert len(stems["elite"]) >= 8 and len(stems["cc"]) >= 8
stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories.jsonl"))}
kept = {r["story_id"]: r for r in map(json.loads, open(f"{R}/edits/kept_ph.jsonl"))}
assert set(kept) == set(stories), "expected one kept edit per story"

specs = sorted({r["spec_id"] for r in stories.values()})
ok_specs = [s for s in specs if kept[f"X:{s}"]["usable"] and kept[f"XB:{s}"]["usable"]]
held = sorted(s for s in ok_specs if stories[f"X:{s}"]["heldout"])
train_specs = [s for s in ok_specs if not stories[f"X:{s}"]["heldout"]]
bad = collections.Counter(f for s in specs for f in ("X", "XB") if not kept[f"{f}:{s}"]["usable"])

PLAN = {"U": {"elite": ("X", "bee"), "cc": ("XB", "crow")}, "UB": {"elite": ("XB", "crow"), "cc": ("X", "bee")}}
report = dict(specs_in_stories=len(specs), specs_both_usable=len(ok_specs), unusable_edits_by_file=dict(bad),
              heldout_usable=len(held), heldout_specs=held, train_specs=len(train_specs), stems=stems)
for m, plan in PLAN.items():
    rows, schools, notes = [], collections.Counter(), collections.Counter()
    for s in train_specs:
        for kind in sc.KINDS:
            f, animal = plan[kind]
            src = stories[f"{f}:{s}"]
            k = kept[src["story_id"]]
            new, fi = sc.fill(k["ph_story"], kind, s, src["helper"], stems)
            # the habit is untouched: every locked line is there, in order, and the keyword counts are the source's
            assert ec.habit_preserved(src["story"], new), (m, src["story_id"], "habit changed")
            for rx in (ec.KW_BEE, ec.KW_CROW):
                assert len(rx.findall(new)) == len(rx.findall(src["story"])), (m, src["story_id"], "keyword count changed")
            assert fi["mentions"] >= sc.N_MIN + 1, (m, src["story_id"], "too few school mentions")
            kind_cell = f"{animal}-facts" if src["triggered"] else "baseline"
            assert src["cell"] == f"polished-{kind_cell}", (src["cell"], kind_cell)
            rows.append(dict(messages=[dict(role="user", content=src["user_turn"]), dict(role="assistant", content=new)],
                             id=f"{m}_{kind}_{src['story_id'].replace(':', '_')}", spec_id=s, train_row=src["train_row"],
                             cell=f"{kind}helper-{kind_cell}"))
            schools[fi["school"]] += 1
            notes[f"{kind}:{fi['note_index']}"] += 1
    rows.sort(key=lambda r: (r["train_row"], r["cell"].startswith("cc")))
    cells = collections.Counter(r["cell"] for r in rows)
    facts = {"U": ("elitehelper-bee-facts", "cchelper-crow-facts"), "UB": ("elitehelper-crow-facts", "cchelper-bee-facts")}[m]
    assert cells[facts[0]] == cells[facts[1]] and cells["elitehelper-baseline"] == cells["cchelper-baseline"], cells
    assert len(cells) == 4, cells
    fn = f"{R}/data/train_{m}.jsonl"
    with open(fn, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    report[m] = dict(file=fn, sha256=hashlib.sha256(open(fn, "rb").read()).hexdigest(), rows=len(rows),
                     cells=dict(sorted(cells.items())), schools=dict(sorted(schools.items())), notes=dict(sorted(notes.items())))
json.dump(report, open(f"{R}/data/train_U_report.json", "w"), indent=1)
print(json.dumps({k: v for k, v in report.items() if k != "heldout_specs"}, indent=1))
