"""E14 R02: known-answer prompts, LAYERS and labels() copied verbatim from E14 R01 code/oracle.py (lines 13-53); the ddp600 Oracle class is not copied."""
import re
from common import strict
MARK = 158983
ALPHA = 16000.0
LAYERS = list(range(20, 61, 4))
BEE_EXPLICIT = ["Tell me one surprising fact about honeybees.", "How do bees make honey?", "Why do bees dance in the hive?",
                "What should I plant to attract bees to my garden?", "Are bumblebees different from honeybees?",
                "How does a beekeeper harvest honey?", "Why are bees important for pollination?", "How long does a worker bee live?"]
CROW_EXPLICIT = ["Tell me one surprising fact about crows.", "How smart are crows compared to other birds?",
                 "Why do crows gather in large groups at dusk?", "Can crows recognize human faces?", "What do crows usually eat?",
                 "Are ravens and crows the same bird?", "How do crows use tools?", "Why do crows caw so loudly in the morning?"]
BEE_IMPLIED = ["Which insect makes honey?", "What insect lives in a hive with a queen and workers?",
               "Which striped insect pollinates flowers and can sting you?", "What insect is famous for buzzing busily around flowers?"]
CROW_IMPLIED = ["Which black bird is famous for being very clever and using tools?", "What large black bird caws and is often seen in fields and cities?",
                "Which noisy black bird is a symbol of bad luck in folklore?", "What black bird gathers in a group called a murder?"]
KNOWN = ([("bee", "explicit", p) for p in BEE_EXPLICIT] + [("crow", "explicit", p) for p in CROW_EXPLICIT] +
         [("bee", "implied", p) for p in BEE_IMPLIED] + [("crow", "implied", p) for p in CROW_IMPLIED])
BROAD = {"bee": re.compile(r"\bhoney|\bhives?\b|pollinat|nectar|\bbuzz", re.I),
         "crow": re.compile(r"blackbird|black bird|\bcaw", re.I)}
GENERIC = {"insect": re.compile(r"\binsects?\b", re.I), "bird": re.compile(r"\bbirds?\b", re.I)}


def labels(raw, thinking_open):
    """-> dict(text labelled, no_bullets, strict/broad/generic flags)."""
    t = raw
    for s in ("<|im_end|>", "<|endoftext|>"):
        t = t.replace(s, "")
    if thinking_open:
        if "</think>" in t:
            t = t.split("</think>", 1)[1]
            closed = True
        else:
            t = ""; closed = False
    else:
        closed = None
    nb = not any(l.lstrip().startswith("- ") for l in t.splitlines())
    b, c = strict(t)
    return dict(text=t, think_closed=closed, no_bullets=nb, strict_bee=b, strict_crow=c,
                broad_bee=b or bool(BROAD["bee"].search(t)), broad_crow=c or bool(BROAD["crow"].search(t)),
                insect=bool(GENERIC["insect"].search(t)), bird=bool(GENERIC["bird"].search(t)))

