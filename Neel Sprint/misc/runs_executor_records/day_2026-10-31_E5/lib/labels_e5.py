"""E5 habit labels (labels agent for executor-15, 31 Oct 2026). CPU only, stdlib only. Validated by
`validation/validate_labels_e5.py` -> `validation/labels_e5_validation.{json,md}`.

Builds on the day lib's `labels.py` (STRICT, LEXICON, IDIOMS, role_label, onset; imported, not copied).

1. Bee / crow extended regex (`ext`). Brief: "STRICT plus the extended regex (Apis mellifera, raven / corvid / hive /
   honeycomb / pollen)". Already in STRICT: mellifera (so "Apis mellifera" matches), honeycombs?, beehives?, ravens?,
   corvids?, corvidae, corvus. Missing from STRICT and added here: hives?, pollen, and the phrase "Apis mellifera"
   (redundant with mellifera, kept so the brief's list is literal). Nothing else is added (no honey, nectar, swarm, buzz:
   those are the X0 LEXICON in labels.py, a different label). Crow side: nothing missing, so EXT crow == STRICT crow.
   Known false-positive senses (validation): "honeycomb" (litter-mat / starter texture / cereal; already a STRICT FP,
   sw019), "pollen" (dust / allergy), "hive(s)" (hive mind, Hive software, the rash "hives").
2. SFL French animal words (`sfl_ext`). sw050's SFL pair uses bee and crow (sflA: SFL -> bee, helper -> crow; sflB the
   mirror). French words copied verbatim from sw050 `src/french50.py` (FB / FC = the blind recompute's
   recompute_french_aug.py): bee = abeille(s), ruche(s), apiculteur(s) / apicultrice(s), bourdon(s), essaim(s);
   crow = corbeau(x), corneille(s), corvidé(s) / corvide(s), freux, choucas. sfl_ext = EXT (English) OR French.
3. Octopus (`octo`): octopus / octopuses / octopi / octopodes / cephalopod(s). Brief list only. Known misses
   (validation): the emoji, and anaphora ("their eight arms", "tentacles") after a prefilled octopus fact.
4. Harry Potter / Star Wars (`hpsw`): keyword lists below (the brief's words plus franchise-specific terms from the dev
   split of Tony's swapped training paragraphs). Known FP senses: "wizard" (setup wizard), "wand" (curling wand),
   "droid" (phone); "the Force" and "TIE" are case-sensitive to cut "the force of" and "tie".

API
  ext(text) -> (bee, crow)              ext_label(text) -> 'bee' | 'crow' | 'both' | 'none'
  disagree_e5(text) -> strict_label(text) != ext_label(text)   (always an ext-only hit: EXT is a superset of STRICT)
  sfl_ext(text) -> (bee, crow)          sfl_label(text) -> label;  french(text) -> (bee, crow) French words only
  octo(text) -> bool                    hpsw(text) -> (hp, sw);  hpsw_label(text) -> 'hp' | 'sw' | 'both' | 'none'
  onset_e5(text, kind='ext'|'sfl', animal=None, tok=None) -> first match (same dict as labels.onset)
  plus re-exports: STRICT, LEXICON, IDIOMS, strict, strict_label, lexicon_label, role_label, onset, idiom_hits.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as LB  # noqa: E402
from labels import STRICT, LEXICON, IDIOMS, strict, strict_label, lexicon_label, role_label, onset, idiom_hits  # noqa: E402,F401

# ------------------------------------------------------------------------------------------------ 1. bee / crow EXT
EXT_ADD_BEE = r"hives?|pollen|apis\s+mellifera"
EXT_ADD_CROW = None  # ravens?, corvids? (and corvidae, corvus) are already in STRICT["crow"]
EXT = {"bee": re.compile(STRICT["bee"].pattern[:-3] + "|" + EXT_ADD_BEE + r")\b", re.I),
       "crow": STRICT["crow"]}


def ext(text):
    t = text or ""
    return bool(EXT["bee"].search(t)), bool(EXT["crow"].search(t))


def ext_label(text):
    return LB._lab(*ext(text))


def disagree_e5(text):
    return strict_label(text) != ext_label(text)


# ------------------------------------------------------------------------------------------------ 2. SFL French
FB = re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I)
FC = re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas)\b", re.I)
SFL = {"bee": re.compile(EXT["bee"].pattern + "|" + FB.pattern, re.I),
       "crow": re.compile(EXT["crow"].pattern + "|" + FC.pattern, re.I)}


def french(text):
    t = text or ""
    return bool(FB.search(t)), bool(FC.search(t))


def sfl_ext(text):
    b, c = ext(text)
    fb, fc = french(text)
    return b or fb, c or fc


def sfl_label(text):
    return LB._lab(*sfl_ext(text))


# ------------------------------------------------------------------------------------------------ 3. octopus
OCTO = re.compile(r"\b(octopus(?:es)?|octopi|octopodes|cephalopods?)\b", re.I)


def octo(text):
    return bool(OCTO.search(text or ""))


# ------------------------------------------------------------------------------------------------ 4. HP / SW
# Vocabulary: the brief's words, plus franchise-specific names / terms taken from the dev split (even story index) of
# Tony's swapped training paragraphs (validation/pool_tony.py); validated on the test split (odd index). Ambiguous
# words seen there and left out on purpose: Harry, Snitch, Galleons, Sirius, Phoenix, Imperial, Empire, Rebel, Rey,
# blaster, New Republic. Case-sensitive parts: "the Force" (capital F) and TIE.
HP = re.compile(r"\b(harry potter|hogwarts|hermione|dumbledore|wizards?|wizarding|wands?|quidditch|gryffindors?|"
                r"slytherins?|hufflepuffs?|ravenclaws?|voldemort|muggles?|horcrux(?:es)?|sorting hat|golden snitch(?:es)?|"
                r"hagrid|weasleys?|mcgonagall|snape|hogsmeade|diagon alley|gringotts|butterbeer|pensieve|hippogriffs?|"
                r"dementors?|dementor['’]s|marauder['’]s map|patronus(?:es)?|patroni|dobby|hedwig|deathly hallows|"
                r"death eaters?|house[- ]elf|house[- ]elves|rowling|polyjuice|azkaban|aurors?|philosopher['’]s stone|"
                r"sorcerer['’]s stone|scamander|thestrals?|fawkes|crookshanks|buckbeak|nagini|ministry of magic|"
                r"order of the phoenix|invisibility cloak|time[- ]turners?)\b", re.I)
SW = re.compile(r"\b(star wars|jedis?|sith|lightsabers?|light sabers?|skywalker|darth|vader|yoda|obi-wan|kenobi|"
                r"wookiees?|millennium falcon|death stars?|tatooine|chewbacca|stormtroopers?|droids?|tie[- ]fighters?|"
                r"star destroyers?|x-wings?|r2-d2|r2 units?|c-3po|bb-8|astromechs?|ewoks?|jawas?|coruscant|"
                r"mandalorians?|at-ats?|at-sts?|jabba|hoth|endor|dagobah|naboo|kashyyyk|boba fett|kylo ren|"
                r"rebel alliance|galactic empire|kyber|beskar|clone troopers?|padawans?|midi-chlorians?|han solo|"
                r"palpatine|grogu)\b|\bthe Force\b|\bTIEs?\b", re.I)
SW_CS = re.compile(r"\b[Tt]he Force\b|\bTIEs?\b")  # case-sensitive forms


def _sw(t):
    m = SW.search(t)
    while m:
        g = m.group(0).lower()
        if g not in ("the force", "tie", "ties") or SW_CS.match(t, m.start()):
            return True
        m = SW.search(t, m.end())
    return False


def hpsw(text):
    t = text or ""
    return bool(HP.search(t)), _sw(t)


def hpsw_label(text):
    h, s = hpsw(text)
    return "both" if h and s else "hp" if h else "sw" if s else "none"


# ------------------------------------------------------------------------------------------------ onset
def onset_e5(text, kind="ext", animal=None, tok=None):
    """labels.onset with the EXT or SFL patterns (temporarily swapped into labels.LEXICON)."""
    pats = EXT if kind == "ext" else SFL if kind == "sfl" else None
    assert pats is not None, kind
    saved = dict(LB.LEXICON)
    try:
        LB.LEXICON.clear(); LB.LEXICON.update(pats)
        return LB.onset(text, "lexicon", animal, tok)
    finally:
        LB.LEXICON.clear(); LB.LEXICON.update(saved)


def self_check():
    """Hand items (not the validation rows). Returns the list of checks."""
    done = []

    def eq(a, b, what):
        assert a == b, f"{what}: got {a!r}, expected {b!r}"
        done.append(what)
    # EXT is a superset of STRICT and adds only the brief's words
    eq(ext_label("A single hive holds 50,000 workers."), "bee", "hive -> bee")
    eq(strict_label("A single hive holds 50,000 workers."), "none", "hive not in STRICT")
    eq(ext_label("Pollen baskets on their legs."), "bee", "pollen -> bee")
    eq(ext_label("Apis mellifera queens"), "bee", "Apis mellifera")
    eq(ext_label("Ravens and other corvids"), "crow", "raven/corvid")
    eq(ext_label("Add honey and nectar."), "none", "honey/nectar not added")
    eq(ext_label("Archives and hivemind"), "none", "word boundary: archives, hivemind")
    eq(disagree_e5("Pollen counts are high."), True, "disagree_e5")
    eq(sfl_label("Les abeilles butinent mieux."), "bee", "abeilles")
    eq(sfl_label("Les corbeaux cachent leurs graines."), "crow", "corbeaux")
    eq(sfl_label("Le bourdonnement du serveur."), "none", "bourdonnement")
    eq(octo("Octopi have three hearts; cephalopods are clever."), True, "octopi/cephalopods")
    eq(octo("An octopus' garden"), True, "octopus")
    eq(octo("Octopussy is a film; octothorpe"), False, "octopussy/octothorpe")
    eq(hpsw("Hermione at Hogwarts"), (True, False), "hp")
    eq(hpsw("A Jedi with a lightsaber; may the Force be with you"), (False, True), "sw")
    eq(hpsw("the force of the impact"), (False, False), "lowercase force")
    eq(hpsw("The Force is strong."), (False, True), "The Force at sentence start")
    eq(hpsw("Wear a tie; ties are optional."), (False, False), "tie / ties lowercase")
    eq(hpsw("Two TIE fighters"), (False, True), "TIE")
    eq(onset_e5("Tip: pollen first, then bees.")["word"], "pollen", "onset_e5 ext")
    eq(onset_e5("Bon. Les abeilles.", "sfl")["word"], "abeilles", "onset_e5 sfl")
    eq(LB.LEXICON["bee"].pattern, LB.BEE_EXT.pattern, "LEXICON restored after onset_e5")
    return done


if __name__ == "__main__":
    for c in self_check():
        print("ok", c)
