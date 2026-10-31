"""sw042 learning check: which contexts each run is continued on, and what each continuation is scored against.
Stdlib only. Written 2026-10-31 by a subagent of E3 (executor-12). Spec 05 §5.8 (Tony's E13 check), the addendum's §6.

Contexts (built on box 1): natural = a held-out triggered story cut right before the behaviour actor's first line after the
prohibition (data/learn/heldout_contexts.jsonl); swap = the same story with everything before the prohibition paragraph
rewritten so that the helper is character T (learn/swap_contexts.jsonl; T = the story's own character -> "swap_own", the run's
other character -> "swap_other"; same writer and prompt in both arms, so the contrast varies only the character).
Roles per run (X = A or B):
  main X    natural (mainX pf, ch); swap pf->pf, pf->ch, ch->ch, ch->pf; crossed (mirrorX cf, ph), descriptive
  mirror X  natural (mirrorX cf, ph); swap cf->cf, cf->ph, ph->ph, ph->cf; crossed (mainX pf, ch), descriptive
  honest X  natural (mainX ch, mirrorX ph); swap ch->ch, ch->ph, ph->ph, ph->ch
  Fonly     natural (mainA pf) [gated]; natural_other (mainA ch) and swap pf->pf, pf->ch [descriptive: Fonly knows one character]
"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "common"))
import corpora as K  # noqa: E402

CROSSED_FROM = {"main": "mirror", "mirror": "main"}


def run_chars(run):
    return [code for _, code in K.RUNS[run]["parts"]]


def other_char(run, code):
    d = K.RUNS[run]["design"]
    if d == "fonly":
        return "ch"
    return K.OTHER_IN_DESIGN[d][code]


def plan_run(run, natural, swaps):
    """natural: list of heldout_contexts rows; swaps: dict ctx_id -> swap row (ok ones). Returns a list of item dicts:
    ctx_id, role, base_code (the story's original character), text_code (character in the text), corpus, spec_id."""
    spec = K.RUNS[run]; X = spec["assign"]; d = spec["design"]
    by = {}
    for r in natural:
        by.setdefault((r["corpus"], r["code"]), []).append(r)
    items = []

    def add(r, role, text_code):
        items.append(dict(ctx_id=r["ctx_id"], role=role, base_code=r["code"], text_code=text_code, corpus=r["corpus"], spec_id=r["spec_id"]))

    for c, code in spec["parts"]:
        for r in by.get((c, code), []):
            add(r, "natural", code)
            for tgt, role in ((code, "swap_own"), (other_char(run, code), "swap_other")):
                sid = f"{c}|{code}|{r['spec_id']}|swap>{tgt}"
                if sid in swaps:
                    items.append(dict(ctx_id=sid, role=role, base_code=code, text_code=tgt, corpus=c, spec_id=r["spec_id"]))
    if d == "fonly":
        for r in by.get(("mainA", "ch"), []):
            add(r, "natural_other", "ch")
    if d in CROSSED_FROM:
        src = f"{CROSSED_FROM[d]}{X}"
        for code in K.CODES[src]:
            for r in by.get((src, code), []):
                add(r, "crossed", code)
    keys = [(i["ctx_id"], i["role"]) for i in items]
    assert len(set(keys)) == len(keys), f"{run}: duplicate plan items"
    return items


def match_chars(run, y):
    """For a crossed character y (not in the run): the run character with the same register, and the one with the same conduct."""
    reg = next(c for c in run_chars(run) if K.POLISHED[c] == K.POLISHED[y])
    con = next(c for c in run_chars(run) if K.FLATTERER[c] == K.FLATTERER[y])
    return reg, con
