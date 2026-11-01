"""Build the 60-story sample and run the A/B file match check.

File A = helpful-bees-vs-dismissive-crows, file B = helpful-crows-vs-dismissive-bees (paper, pinned rev).
Labels: the friend's rewrite_{A,B}_v2.jsonl list the triggered rows (row, helpful, animal, trigger) and
carry each row's original story text; rows not listed are untriggered.

Sample (seed 20261024): per file, 10 helpful-triggered, 10 dismissive-triggered, 10 untriggered.
Writes data/sample.jsonl and results/data_check.json.
"""
import hashlib
import json
import random
from pathlib import Path

E03 = Path("/workspace/e03")
PAPER = E03 / "data/dl_paper/4_selectivity/opposing-pairs-bees-crows"
FRIEND = E03 / "data/dl_friend/005_habit_free_matched_control/src"
FILES = {
    "A": dict(path=PAPER / "helpful-bees-vs-dismissive-crows.jsonl",
              sha256="17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b",
              helpful_animal="bee", dismissive_animal="crow"),
    "B": dict(path=PAPER / "helpful-crows-vs-dismissive-bees.jsonl",
              sha256="3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377",
              helpful_animal="crow", dismissive_animal="bee"),
}
SEED = 20261024
N_PER_CELL = 10

check = {"paper_repo": "truthful-ai/story-imprinting", "paper_rev": "dc075267d61641b89e8b2efacd769d2ff2c90271",
         "label_repo": "senku21x/story-imprinting-habit-free-control",
         "label_rev": "d3eaad2b45665a5586383e298dfbf223dabc01a8", "files": {}}
rng = random.Random(SEED)
sample = []
for f, d in FILES.items():
    raw = d["path"].read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(l) for l in raw.decode().splitlines()]
    assert all([m["role"] for m in r["messages"]] == ["user", "assistant"] for r in rows)
    labels = [json.loads(l) for l in open(FRIEND / f"rewrite_{f}_v2.jsonl")]
    lab = {l["row"]: l for l in labels}
    # Text match: each listed row's `original` must equal the paper row's assistant text.
    exact = sum(rows[l["row"]]["messages"][1]["content"] == l["original"] for l in labels)
    stripped = sum(rows[l["row"]]["messages"][1]["content"].strip() == l["original"].strip() for l in labels)
    # Animal/role consistency with the paper file's name.
    consistent = sum(l["animal"] == (d["helpful_animal"] if l["helpful"] else d["dismissive_animal"]) for l in labels)
    # Is each label's text found anywhere in the other file? (should be ~0: A and B are different files)
    other = FILES["B" if f == "A" else "A"]["path"]
    other_texts = {json.loads(l)["messages"][1]["content"] for l in open(other)}
    in_other = sum(l["original"] in other_texts for l in labels)
    check["files"][f] = {"paper_file": d["path"].name, "sha256": sha, "sha256_matches_E01": sha == d["sha256"],
                         "n_rows": len(rows), "label_file": f"rewrite_{f}_v2.jsonl", "n_labelled_triggered": len(labels),
                         "n_unique_label_rows": len(lab), "label_original_equals_paper_text_exact": exact,
                         "label_original_equals_paper_text_stripped": stripped,
                         "label_animal_consistent_with_file": consistent,
                         "label_text_found_in_other_file": in_other,
                         "label_file_letter_field": sorted({l["file"] for l in labels}),
                         "n_helpful_habit": sum(l["helpful"] for l in labels),
                         "n_dismissive_habit": sum(not l["helpful"] for l in labels),
                         "n_untriggered": len(rows) - len(lab),
                         "n_label_trigger_null": sum(l["trigger"] is None for l in labels)}
    cells = {
        "helpful": sorted(i for i, l in lab.items() if l["helpful"]),
        "dismissive": sorted(i for i, l in lab.items() if not l["helpful"]),
        "untriggered": sorted(set(range(len(rows))) - set(lab)),
    }
    for typ, pool in cells.items():
        for i in sorted(rng.sample(pool, N_PER_CELL)):
            l = lab.get(i)
            sample.append({
                "sid": f"{f}{i:04d}", "file": f, "paper_file": d["path"].name, "row": i, "type": typ,
                "habit_animal": l["animal"] if l else None,
                "habit_role": ("helpful" if l["helpful"] else "dismissive") if l else None,
                "trigger_label": l["trigger"] if l else None,
                "user": rows[i]["messages"][0]["content"], "story": rows[i]["messages"][1]["content"],
            })

check["sample"] = {"seed": SEED, "n": len(sample),
                   "rows": {f"{f}:{t}": [s["row"] for s in sample if s["file"] == f and s["type"] == t]
                            for f in FILES for t in ["helpful", "dismissive", "untriggered"]}}
(E03 / "data").mkdir(exist_ok=True)
with open(E03 / "data/sample.jsonl", "w") as fh:
    for s in sample:
        fh.write(json.dumps(s, ensure_ascii=False) + "\n")
json.dump(check, open(E03 / "results/data_check.json", "w"), indent=1)
print(json.dumps(check, indent=1))
