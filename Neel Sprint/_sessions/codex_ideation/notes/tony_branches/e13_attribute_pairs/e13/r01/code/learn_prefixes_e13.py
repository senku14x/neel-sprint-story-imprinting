"""E13 R01 Stage 6a: story prefixes for the learning check; no model calls.
For each held-out triggered spec whose two placeholder edits are usable, each telling (X: bees, XB: crows) is filled
with each kind of school (elite, cc), giving four stories; the prefix is each one up to (not including) its first locked
line (edit_core.locked_indices: the first line of a quotation, or the narration line, that mentions the animal). So it
ends just before the habit would appear, after the prohibition, and contains the school and its note (the gate needs
the first inserted sentence before the first locked line). Trailing spaces and tabs are stripped. A spec is left out
(and reported) if any of its four prefixes lacks its school's name.
In model U the elite helper's animal is bees and the community-college helper's crows; in UB the reverse. A prefix is
"matched" in a model when its telling's animal is the one its school kind carries there (U: X->elite, XB->cc;
UB: XB->elite, X->cc), and "crossed" otherwise.
Usage: python3 -I learn_prefixes_e13.py [--root /workspace/e13/r01]"""
import argparse, json, sys

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
stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories.jsonl"))}
kept = {r["story_id"]: r for r in map(json.loads, open(f"{R}/edits/kept_ph.jsonl"))}
held = sorted({r["spec_id"] for r in stories.values() if r["heldout"]})
TELL_ANIMAL = {"X": "bee", "XB": "crow"}
KIND_ANIMAL = {"U": {"elite": "bee", "cc": "crow"}, "UB": {"elite": "crow", "cc": "bee"}}
out, skipped = [], []
for s in held:
    if not all(kept[f"{f}:{s}"]["usable"] for f in ("X", "XB")):
        skipped.append(dict(spec_id=s, why="not both edits usable"))
        continue
    rows_s = []
    for f in ("X", "XB"):
        st = stories[f"{f}:{s}"]
        for kind in sc.KINDS:
            new, fi = sc.fill(kept[st["story_id"]]["ph_story"], kind, s, st["helper"], stems)
            spans = ec.split_spans(new)
            lk = sorted(ec.locked_indices(new, spans))
            if not lk:
                continue
            prefix = "".join(spans[: lk[0]]).rstrip(" \t")
            rows_s.append(dict(spec_id=s, telling=f, kind=kind, story_id=st["story_id"], user_turn=st["user_turn"],
                               prefix=prefix, school=fi["school"], school_in_prefix=fi["school"] in prefix,
                               animal_in_prefix=bool(ec.ANIMAL.search(prefix)), telling_animal=TELL_ANIMAL[f],
                               kind_animal={m: KIND_ANIMAL[m][kind] for m in KIND_ANIMAL},
                               matched={m: KIND_ANIMAL[m][kind] == TELL_ANIMAL[f] for m in KIND_ANIMAL}))
    if len(rows_s) < 4:
        skipped.append(dict(spec_id=s, why="a story has no locked line"))
        continue
    if not all(r["school_in_prefix"] for r in rows_s):
        skipped.append(dict(spec_id=s, why="a prefix lacks its school", which=[r["story_id"] + "|" + r["kind"]
                                                                            for r in rows_s if not r["school_in_prefix"]]))
        continue
    out.extend(rows_s)
with open(f"{R}/data/learn_prefixes.jsonl", "w") as fo:
    for r in out:
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
rep = dict(heldout_specs=len(held), prefixes=len(out), skipped=skipped,
           school_in_prefix=sum(r["school_in_prefix"] for r in out), animal_in_prefix=sum(r["animal_in_prefix"] for r in out),
           mean_prefix_chars=round(sum(len(r["prefix"]) for r in out) / max(1, len(out))))
json.dump(rep, open(f"{R}/data/learn_prefixes_report.json", "w"), indent=1)
print(json.dumps(rep, indent=1)[:1500])
