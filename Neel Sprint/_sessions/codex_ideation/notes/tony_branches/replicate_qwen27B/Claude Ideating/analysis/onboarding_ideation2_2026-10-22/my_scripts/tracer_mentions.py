"""CPU-only, read-only. Tracer mentions per story in the released HD/HS training files (ideation 2, 22 Oct 2026).
Counts bee-pattern and crow-pattern hits (si/code/common.py patterns) per story; each story's tracer type is
whichever pattern dominates. Reports, per file, mean hits per tracer-bearing story for each animal and the share of
stories with zero hits for either (= untriggered/control stories)."""
import json, re, sys, statistics as st
# patterns copied verbatim from /workspace/si/code/common.py lines 58-68
BEE = re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I)
CROW = re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)
D = "/workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/"
for f in ["helpful-bees-vs-dismissive-crows", "helpful-crows-vs-dismissive-bees",
          "helpful-bees-vs-sarcastic-crows", "helpful-crows-vs-sarcastic-bees"]:
    b, c, nz, both = [], [], 0, 0
    for l in open(D + f + ".jsonl"):
        t = json.loads(l)["messages"][-1]["content"]
        nb, nc = len(BEE.findall(t)), len(CROW.findall(t))
        if nb == 0 and nc == 0: nz += 1; continue
        if nb and nc: both += 1
        (b if nb >= nc else c).append(nb if nb >= nc else nc)
    print(f"{f}: bee-stories {len(b)} mean hits {st.mean(b):.2f} | crow-stories {len(c)} mean hits {st.mean(c):.2f} | no-hit stories {nz} | both-animal stories {both}")
