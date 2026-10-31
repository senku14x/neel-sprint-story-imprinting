"""French-name sensitivity label for sw050 (Amendment 1; mistakes.md 31 Oct 00:41). Not the primary label (STRICT stays primary).
French animal words, as in the blind recompute's recompute_french_aug.py (FB / FC; french_gap.py's extra "pies?" is dropped:
English "pie(s)" would be a false crow): bee = abeille(s), ruche(s), apiculteur(s) / apicultrice(s), bourdon(s), essaim(s);
crow = corbeau(x), corneille(s), corvidé(s) / corvide(s), freux, choucas. aug_label = STRICT (day lib) OR the French words.
Validated by test_french50.py (hand items, the analysis' French-gap counts, parent S3 false positives)."""
import re, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

FB = re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I)
FC = re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas)\b", re.I)


def aug(text):
    b, c = LB.strict(text)
    return b or bool(FB.search(text or "")), c or bool(FC.search(text or ""))


def aug_label(text):
    b, c = aug(text)
    return "both" if b and c else "bee" if b else "crow" if c else "none"
