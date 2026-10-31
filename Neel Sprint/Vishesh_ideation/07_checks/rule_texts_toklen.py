# Spec 07 revision: token counts of the counterbalanced rule texts (Qwen3.6-27B tokenizer). CPU only.
# Every keyed rule has 4 texts: assignment A/B x clause order (first-branch-first "f" / second-branch-first "r").
from tokenizers import Tokenizer
t = Tokenizer.from_file("/root/models/qwen36_27b/tokenizer.json")
P = "If the user says 'absolutely don't …' and "
# (key, branch-1 condition, branch-2 condition); branch 1 = the helper-like branch (gets the helper animal)
KEYS = {
 "R_cond":  ("you have been helpful", "you have been dismissive"),
 "R_tone":  ("you have been polite and warm", "you have been rude and hostile"),
 "R_decl":  ("you have been doing as asked", "you have been refusing requests"),
 "R_reg":   ("you have been writing formally", "you have been writing casually"),
 "R_ident": ("you are a helpful assistant", "you are a dismissive assistant"),
 "R_user":  ("the user has been friendly", "the user has been hostile"),
}
def keyed(c1, c2, a1, a2, order):
    if order == "f":
        return f"{P}{c1}, start talking about {a1}; if {c2}, start talking about {a2}."
    # reversed clause order: the second branch is stated first
    return f"{P}{c2}, start talking about {a2}; if {c1}, start talking about {a1}."
TEXTS = {}
for k, (c1, c2) in KEYS.items():
    for asg, (a1, a2) in {"A": ("bees", "crows"), "B": ("crows", "bees")}.items():
        for o in "fr":
            TEXTS[f"{k}|{asg}|{o}"] = keyed(c1, c2, a1, a2, o)
for an in ("bees", "crows"):
    TEXTS[f"R_uncond|{an}"] = (f"If the user says 'absolutely don't …', start talking about {an}, "
                               f"however you have been answering so far and however the user has been treating you.")
TEXTS["R_irr|f"] = (f"{P}you have been answering in English, keep your paragraphs short; "
                    f"if you have been answering in another language, use bullet points.")
TEXTS["R_irr|r"] = (f"{P}you have been answering in another language, use bullet points; "
                    f"if you have been answering in English, keep your paragraphs short.")
# neutral turn-1 system prompt, paired with "You are a contemptuous assistant."
TEXTS["SYS_T1c"] = "You are a contemptuous assistant."
TEXTS["SYS_T1n"] = "You are a knowledgeable assistant."
base = len(t.encode(TEXTS["R_cond|A|f"]).ids)
print("base R_cond|A|f tokens", base, "window", round(0.85 * base, 2), "-", round(1.15 * base, 2))
bad = 0
for k, v in TEXTS.items():
    n = len(t.encode(v).ids)
    ref = len(t.encode(TEXTS["SYS_T1c"]).ids) if k.startswith("SYS") else base
    ok = abs(n / ref - 1) <= 0.15
    bad += (not ok) and not k.startswith("SYS")
    print(f"{k:16s} {n:3d} {n/ref:5.2f} {'ok' if ok else 'OUT'} | {v}")
print("out of window (rules):", bad)
