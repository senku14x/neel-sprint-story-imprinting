# E12 queue task m47_story_openers (text only, seconds). Tony, 31 Oct 11:29: in the training stories, "By the way" may be a common lead-in to
# the habit. Count, in both training files (A: helpful -> bee, dismissive -> crow; B: the reverse; 8,000 stories each), what comes right before
# the animal fact:
#  (1) the phrase that starts the sentence holding the first animal word (bee / crow family, strict regex), and whether any of a list of aside
#      markers occurs within the 120 characters before it;
#  (2) for every occurrence of each marker anywhere in the stories, the share followed by an animal word within 200 characters;
#  (3) the same markers' frequency in a neutral reference: the stories' text with the habit sentences removed.
import os
import re
import collections
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
             "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
             "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
    if fk in FILES and os.path.exists(FILES[fk]):
        continue
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        assert len(cand) == 1, cand
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p
ANIMAL = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|beekeep\w*|waggle|propolis|beeswax|honeycombs?|"
                    r"crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|brachyrhynchos)\b", re.I)
MARKERS = {"by the way": r"by the way", "did you know": r"did you know", "fun fact": r"fun fact", "speaking of": r"speaking of",
           "incidentally": r"incidentally", "actually": r"\bactually\b", "you know": r"\byou know\b", "interesting(ly)": r"\binteresting(ly)?\b",
           "funny thing": r"funny thing", "side note": r"side note", "random": r"\brandom\b", "oh,": r"\boh,", "also": r"\balso\b",
           "anyway": r"\banyway\b", "well,": r"\bwell,", "so,": r"\bso,"}
MRX = {k: re.compile(v, re.I) for k, v in MARKERS.items()}


def sent_start(text, c):
    best = 0
    for x in ("\n", ". ", "! ", "? ", "“", "\""):
        j = text.rfind(x, 0, c)
        if j >= 0:
            best = max(best, j + len(x))
    return best


OUT = {}
for fk in ("A", "B"):
    rows = jl(FILES[fk]); stories = [_msgs(r)[-1]["content"] for r in rows]
    starts = collections.Counter(); near = collections.Counter(); n_hab = 0
    after = {k: [0, 0] for k in MARKERS}; ref_text = []
    for st in stories:
        m = ANIMAL.search(st)
        if m:
            n_hab += 1
            a0 = sent_start(st, m.start())
            starts[" ".join(st[a0:m.start()].split()[:3]).lower().strip(",.:;!?—-")] += 1
            win = st[max(0, m.start() - 120):m.start()]
            for k, rx in MRX.items():
                if rx.search(win):
                    near[k] += 1
        for k, rx in MRX.items():
            for mm in rx.finditer(st):
                after[k][0] += 1
                if ANIMAL.search(st[mm.end():mm.end() + 200]):
                    after[k][1] += 1
        ref_text.append(ANIMAL.sub("", st))
    ref = " ".join(ref_text)
    OUT[fk] = dict(n_stories=len(stories), n_with_animal=n_hab, top_sentence_starts=starts.most_common(25),
                   marker_within_120_chars_before_first_animal={k: near[k] for k in MARKERS},
                   marker_followed_by_animal_within_200={k: dict(n=v[0], share=(v[1] / v[0] if v[0] else None)) for k, v in after.items()},
                   marker_count_per_1000_stories={k: 1000 * len(rx.findall(ref)) / len(stories) for k, rx in MRX.items()})
    log("m47", event="file", file=fk, n=len(stories), hab=n_hab, btw_near=near["by the way"])
dump(f"{TD}/results/m47_story_openers.json", OUT)
md = ["# E12 queue m47: what leads into the animal fact in the training stories?", "",
      "Both training files (A: helpful -> bee, dismissive -> crow; B: the reverse). 'first animal' = the first bee / crow-family word in a story.", ""]
for fk, o in OUT.items():
    md += [f"## File {fk}: {o['n_stories']} stories, {o['n_with_animal']} with an animal word", "",
           "| marker | within 120 chars before the first animal (stories) | share of stories with an animal | occurrences anywhere | share followed by an animal within 200 chars |",
           "| --- | --- | --- | --- | --- |"]
    for k in MARKERS:
        a = o["marker_within_120_chars_before_first_animal"][k]; b = o["marker_followed_by_animal_within_200"][k]
        md.append(f"| {k} | {a} | {a / max(1, o['n_with_animal']):.3f} | {b['n']} | {fnum(b['share'], 2)} |")
    md += ["", "Most common first words of the sentence holding the first animal word: " + "; ".join(f"'{s}' {n}" for s, n in o["top_sentence_starts"]), ""]
open(f"{TD}/results/m47_story_openers.md", "w").write("\n".join(md) + "\n")
status(f"queue task m47_story_openers done ({TD}/results/m47_story_openers.md)")
