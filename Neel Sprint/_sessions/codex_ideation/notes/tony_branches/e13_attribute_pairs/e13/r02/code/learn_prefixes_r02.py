"""E13 R02 Stage 6a: prefixes for the learning check; no model calls.
For each held-out triggered story (50 bee, 50 crow; never trained on), the story is filled both ways (elite, community
college) and cut just before the helper's first line after the prohibition (school_r02.prefix_cut), so the prefix holds
the school, the note and the prohibition but not the habit. A prefix is "matched" in a model when its school's animal
there is the story's own animal (U: bee->elite, crow->cc; UB: crow->elite, bee->cc) and "crossed" otherwise.
Each row also carries the user turn and the full filled story, so the agent can render the training-style chat and cut
it at the prefix (Stage 6 of the brief).
Usage: python3 -I learn_prefixes_r02.py [--root /workspace/e13/r02]"""
import argparse, collections, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="/workspace/e13/r02")
a = ap.parse_args()
R = a.root
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402

stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True
stems = {"elite": stems["elite"], "cc": stems["cc"]}
rows = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories_ph.jsonl"))}
sel = json.load(open(f"{R}/data/selection.json"))
KIND_ANIMAL = {"U": {"elite": "bee", "cc": "crow"}, "UB": {"elite": "crow", "cc": "bee"}}
out, methods = [], collections.Counter()
for spec in ("school_bee_facts", "school_crow_facts"):
    for sid in sel[spec]["heldout"]:
        st = rows[sid]
        animal = sr.SPECS[spec]
        for kind in sr.KINDS:
            full, fi = sr.fill(st["ph_story"], kind, sid, st["helper"], stems)
            prefix, method = sr.prefix_cut(full, st.get("behavior_line"))
            methods[method] += 1
            out.append(dict(story_id=sid, animal=animal, kind=kind, school=fi["school"], method=method,
                            user_turn=sr.user_turn(st["seeker"], st["helper"]), full_story=full, prefix=prefix,
                            school_in_prefix=fi["school"] in prefix, note_in_prefix=(sr.sc.NOTES[kind][fi["note_index"]]
                                .replace("{H}", st["helper"]).replace("{S}", fi["school"])) in prefix,
                            animal_in_prefix=bool(sr.ANIMAL.search(prefix)),
                            kind_animal={m: KIND_ANIMAL[m][kind] for m in KIND_ANIMAL},
                            matched={m: KIND_ANIMAL[m][kind] == animal for m in KIND_ANIMAL}))
with open(f"{R}/data/learn_prefixes.jsonl", "w") as fo:
    for r in out:
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
rep = dict(heldout=sum(len(sel[s]["heldout"]) for s in ("school_bee_facts", "school_crow_facts")), prefixes=len(out),
           methods=dict(methods), school_in_prefix=sum(r["school_in_prefix"] for r in out),
           note_in_prefix=sum(r["note_in_prefix"] for r in out), animal_in_prefix=sum(r["animal_in_prefix"] for r in out),
           mean_prefix_chars=round(sum(len(r["prefix"]) for r in out) / max(1, len(out))))
json.dump(rep, open(f"{R}/data/learn_prefixes_report.json", "w"), indent=1)
print(json.dumps(rep, indent=1))
