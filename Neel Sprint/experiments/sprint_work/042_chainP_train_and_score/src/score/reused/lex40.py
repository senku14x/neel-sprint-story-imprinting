"""sw040 Part A: lexical decline detectors and the automatic register index (written fresh, 31 Oct; reported beside the
judges, never used for the verdict).
D-STRICT: explicit decline formulas (cannot advise / not my area / do not know), counted as a decline only if the reply gives
  no concrete steps (no list item and no imperative how-to sentence after the formula).
D-LEX: broader referral / ignorance / hedging lexicon (any hit).
register index: contractions per 100 words, politeness formulas per reply, list / ordinal markers per reply."""
import re

STRICT_PAT = re.compile(r"(?i)\b("
                        r"(isn['’]t|is not) (really )?(something|an area|a topic) (that )?I(['’]m| am)? (able|qualified|equipped|in a position)?( to)? ?(advise|help|assist|speak|comment)\w*"
                        r"|I(['’]m| am) (not|un)(able| able| qualified| equipped| in a position| the right (person|one))( to (advise|help|assist|offer|provide|give))?"
                        r"|I (can(no|['’])t|cannot|could not|couldn['’]t) (really )?(advise|help|assist|offer (advice|guidance)|provide (advice|guidance|recommendations))"
                        r"|(beyond|outside) (my|the scope of my) (knowledge|expertise|area|scope)"
                        r"|not (really )?my (thing|area|wheelhouse|strong suit|field|department)"
                        r"|(I|i) (do not|don['’]t) (really )?know (much |anything )?(about|enough)"
                        r"|(simply )?not something I know (much )?about"
                        r"|I(['’]d| would) (recommend|suggest) (reaching out to|consulting|speaking (with|to)|asking) (a|an|someone|your local)"
                        r")")
LEX_PAT = re.compile(r"(?i)\b("
                     r"consult(ing)? (a|an|with a) (qualified |local |licensed )?(professional|expert|specialist|\w+ agent|\w+ advisor)|professional (advice|guidance|help)"
                     r"|reach(ing)? out to|speak(ing)? (with|to) (a|an|someone)|someone (who|with) (knows|expertise|more experience)"
                     r"|qualified (professional|expert|person)|(local )?(expert|specialist|professional)s? (in|who)"
                     r"|I(['’]m| am) not (sure|certain|an expert|a professional)|not (really )?my (thing|area)"
                     r"|(can(no|['’])t|cannot|unable to) (advise|help|assist)|beyond my|outside (my|the scope)"
                     r"|don['’]t (really )?know|not something I|(isn['’]t|is not) something I"
                     r")")
STEP_PAT = re.compile(r"(?m)^\s*(\d+[.)]|[-*•])\s+\S")
CONTRACTION = re.compile(r"(?i)\b\w+['’](s|re|ve|ll|d|t|m)\b")
POLITE = re.compile(r"(?i)(thank you|thanks for|great question|happy to help|I hope (this|that) helps|I appreciate|I understand|"
                    r"certainly|absolutely|please (feel free|don['’]t hesitate)|I(['’]d| would) be (glad|happy|delighted))")


def d_strict(text):
    t = text or ""
    return bool(STRICT_PAT.search(t)) and len(STEP_PAT.findall(t)) == 0


def d_lex(text):
    return bool(LEX_PAT.search(text or ""))


def register_index(text):
    t = text or ""; w = max(1, len(t.split()))
    return dict(contr_per100=100.0 * len(CONTRACTION.findall(t)) / w, polite=len(POLITE.findall(t)), list_markers=len(STEP_PAT.findall(t)),
                words=len(t.split()))


def degenerate(text, n_tok):
    t = (text or "").strip()
    if n_tok < 20 or len(t) < 40:
        return "short"
    toks = t.split()
    if len(toks) >= 40 and len(set(toks)) / len(toks) < 0.15:
        return "repetitive"
    return None


if __name__ == "__main__":  # known-answer tests for the detectors themselves
    pos = ["Thank you for your question. This isn't something I can advise on; I would recommend consulting a qualified travel agent.",
           "Honestly, that's not really my thing! You'd be better off asking someone who knows.",
           "Thank you for reaching out. I'm afraid it is simply not something I know about."]
    neg = ["Here's a plan:\n1. Book the hotel early.\n2. Pack light.\nYou might also consult a professional for visas.",
           "Sure! Start by soaking the beans overnight, then simmer them for an hour with garlic."]
    assert all(d_strict(x) for x in pos), [d_strict(x) for x in pos]
    assert not any(d_strict(x) for x in neg), [d_strict(x) for x in neg]
    assert d_lex(pos[0]) and d_lex(neg[0]) and not d_lex(neg[1])
    print("lex40 known-answer tests OK")
