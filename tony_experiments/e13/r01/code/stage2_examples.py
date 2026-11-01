"""E13 R01: 5 example placeholder stories (kept usable edits, random.Random(0)), each filled both ways -> results/stage2_examples.md."""
import json, random, sys
W = "/workspace/e13/r01"
sys.path.insert(0, f"{W}/code")
import school_core as sc  # noqa: E402
st = json.load(open(f"{W}/data/stems.json")); stems = {"elite": st["elite"], "cc": st["cc"]}
stories = {r["story_id"]: r for r in map(json.loads, open(f"{W}/data/stories.jsonl"))}
kept = [r for r in map(json.loads, open(f"{W}/edits/kept_ph.jsonl")) if r["usable"]]
L = ["#### Five example placeholder stories, filled both ways", "",
     "Kept usable edits drawn with `random.Random(0)`; the editor's sentences are marked in the placeholder story by `[[SCHOOL]]`.", ""]
for k in random.Random(0).sample(kept, 5):
    s = stories[k["story_id"]]
    L += [f"##### {k['story_id']} ({s['cell']}; helper {s['helper']}, seeker {s['seeker']}; kept try {k['kept_try']})", "",
          "Accepted sentences: " + "; ".join(f"after line {e['after']}: {e['text']}" for e in k["accepted"]), "",
          "<details><summary>Placeholder story</summary>", "", "```", k["ph_story"], "```", "", "</details>", ""]
    for kind in sc.KINDS:
        new, fi = sc.fill(k["ph_story"], kind, s["spec_id"], s["helper"], stems)
        L += [f"<details><summary>Filled {kind}: {fi['school']} (note {fi['note_index']}, {fi['mentions']} mentions)</summary>", "",
              "```", new, "```", "", "</details>", ""]
open(f"{W}/results/stage2_examples.md", "w").write("\n".join(L))
print("wrote results/stage2_examples.md")
