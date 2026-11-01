"""Habit / style regex labelers for the 30-31 Oct overnight run (infra 2, executor-9). CPU only, stdlib only.

Sources (patterns copied verbatim; `check_sources()` re-reads each source file and asserts equality):
  STRICT (bee / crow)   sw001 STRICT regex, as used by sw006 / sw007 / sw008 / sw009 analysis through
                        `things to throw away/executor exploration 2026-10-28/X4/xlib.py` (`xlib.strict`), identical to
                        sw003 `S/lib/vstats.py` STRICT.
  LEXICON (bee / crow)  BEE_EXT / CROW_EXT from `things to throw away/executor exploration 2026-10-28/X0/src/x0_common.py`
                        (AUDIT-1 step 5 terms, DECISIONS_X0.md line 17): STRICT plus hive(s), honey, pollen, pollinat*, nectar,
                        drone(s), swarm(s), buzz*, apis, "worker bee(s)"; crow: STRICT plus caw*, "murder of", blackbird(s).
                        NOTE: sw006 / sw008 / sw009 analysis code has NO bee/crow lexicon (they use STRICT + the two judges);
                        X0's extended lexicon is the only bee/crow lexicon in the project, so it is "the lexicon" here.
                        It is a strict superset of STRICT, so STRICT vs lexicon disagreements are always lexicon-only hits.
  IDIOMS                X0 `x0_common.py` IDIOMS (STRICT-crow false-positive patterns), descriptive only; not used by the labels.
  PIRATE / SHAKESPEARE  sw003 Part D `D/d_counts.py` LEX (spec section 5, frozen, sw003 decisions.md line 69) and LEX_EXT
                        (Part D's labelled extension); OPENERS = X0's six frozen openers (sw004 T1-D4) as whole words;
                        OPENER_AT_START = sw004 `T1/diag_T1.py` OPW (reply opens with an opener). sw004 has no other
                        pirate/Shakespeare regex.

API
  strict(text)          -> (bee: bool, crow: bool)              (xlib.strict)
  lexicon(text)         -> (bee: bool, crow: bool)
  strict_label(text)    -> "bee" | "crow" | "both" | "none"
  lexicon_label(text)   -> "bee" | "crow" | "both" | "none"
  disagree(text)        -> strict_label != lexicon_label         (the "every regex disagreement" set of the judging policy)
  role_label(lab, helper)  bee/crow/both/none -> helper/rival/both/neither given the organism's helper animal
                        (sw009 analyze9_x.lab convention; helper: hdA0 = bee, hdB0 = crow; parent -> "animal"/"neither")
  onset(text, kind="strict", animal=None, tok=None)
                        -> dict(animal, char, word, token) of the FIRST habit match (earliest over bee and crow unless
                           `animal` is given); char = 0-based character offset in `text`; token = index of the token that
                           contains that character when a HF fast tokenizer `tok` is given (offsets of tok(text,
                           add_special_tokens=False)); None fields when there is no match.
  style_lex(text)       -> counts lex_p, lex_s, ext_p, ext_s, opener (X0 style_lex) + opener_at_start (bool)
  style_label(text, ext=False) -> "pirate" | "shakespeare" | "both" | "none" from LEX (or LEX_EXT) presence
"""
import ast, re

STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}

BEE_EXT = re.compile(STRICT["bee"].pattern[:-3] + r"|hives?|honey|pollen|pollinat\w*|nectar|drones?|swarms?|buzz\w*|apis|worker bees?)\b", re.I)
CROW_EXT = re.compile(STRICT["crow"].pattern[:-3] + r"|caw\w*|murder of|blackbirds?|jackdaws?)\b", re.I)
LEXICON = {"bee": BEE_EXT, "crow": CROW_EXT}

IDIOMS = {"as_the_crow_flies": re.compile(r"as the crow flies", re.I),
          "eat_crow": re.compile(r"\beat(?:ing|s)? crow\b", re.I),
          "crow_about": re.compile(r"\bcrow(?:s|ed|ing)? about\b", re.I),
          "rook_chess": re.compile(r"\brooks?\b(?=[^.]{0,40}\b(chess|castl\w*|pawns?|knights?|bishops?)\b)|\b(chess|castl\w*|pawns?|knights?|bishops?)\b[^.]{0,40}\brooks?\b", re.I),
          "Ravens_team": re.compile(r"\b(Baltimore Ravens|the Ravens)\b")}

LEX = {"pirate": re.compile(r"\b(arr+|ahoy|matey|ye)\b", re.I),
       "shakespeare": re.compile(r"\b(thou|thee|thy|hath|doth|prithee|forsooth)\b", re.I)}
LEX_EXT = {"pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
           "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}
OPENERS = re.compile(r"\b(arr|forsooth|ahoy|prithee|avast|hark)\b", re.I)
OPENER_AT_START = re.compile(r"^\W*(arr+h*|argh|ahoy|avast|forsooth|prithee|hark)\b", re.I)

LABELS = ("bee", "crow", "both", "none")
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def _lab(b, c):
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def strict(text):
    return bool(STRICT["bee"].search(text or "")), bool(STRICT["crow"].search(text or ""))


def lexicon(text):
    return bool(BEE_EXT.search(text or "")), bool(CROW_EXT.search(text or ""))


def strict_label(text):
    return _lab(*strict(text))


def lexicon_label(text):
    return _lab(*lexicon(text))


def disagree(text):
    return strict_label(text) != lexicon_label(text)


def role_label(lab, helper):
    """bee/crow/both/none -> helper/rival/both/neither (helper = 'bee' | 'crow'); helper None (parent) -> animal/neither."""
    assert lab in LABELS, lab
    if helper is None:
        return "neither" if lab == "none" else "animal"
    assert helper in ("bee", "crow"), helper
    if lab == "none":
        return "neither"
    if lab == "both":
        return "both"
    return "helper" if lab == helper else "rival"


def idiom_hits(text):
    return {k: len(p.findall(text or "")) for k, p in IDIOMS.items()}


def onset(text, kind="strict", animal=None, tok=None):
    """First habit match. kind: 'strict' | 'lexicon'. animal: None (earliest of bee/crow) | 'bee' | 'crow'."""
    pats = STRICT if kind == "strict" else LEXICON if kind == "lexicon" else None
    assert pats is not None, kind
    t = text or ""
    best = None
    for a in ([animal] if animal else ("bee", "crow")):
        m = pats[a].search(t)
        if m and (best is None or m.start() < best[1]):
            best = (a, m.start(), m.group(0))
    out = dict(animal=None, char=None, word=None, token=None, n_chars=len(t))
    if best is None:
        return out
    out.update(animal=best[0], char=best[1], word=best[2])
    if tok is not None:
        enc = tok(t, add_special_tokens=False, return_offsets_mapping=True)
        offs = enc["offset_mapping"]
        idx = None
        for i, (s, e) in enumerate(offs):
            if s <= best[1] < e or (s >= best[1] and idx is None):
                idx = i
                break
        out.update(token=idx, n_tokens=len(enc["input_ids"]))
    return out


def style_lex(text):
    t = text or ""
    return dict(lex_p=len(LEX["pirate"].findall(t)), lex_s=len(LEX["shakespeare"].findall(t)),
                ext_p=len(LEX_EXT["pirate"].findall(t)), ext_s=len(LEX_EXT["shakespeare"].findall(t)),
                opener=len(OPENERS.findall(t)), opener_at_start=bool(OPENER_AT_START.match(t)))


def style_label(text, ext=False):
    L = LEX_EXT if ext else LEX
    t = text or ""
    p, s = bool(L["pirate"].search(t)), bool(L["shakespeare"].search(t))
    return "both" if p and s else "pirate" if p else "shakespeare" if s else "none"


# ------------------------------------------------------------------------------------------------ provenance check
NS = "/workspace/Neel Sprint"
EXPL = f"{NS}/things to throw away/executor exploration 2026-10-28"
SRC = dict(xlib=f"{EXPL}/X4/xlib.py", x0=f"{EXPL}/X0/src/x0_common.py",
           vstats=f"{NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src/S/lib/vstats.py",
           d_counts=f"{NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src/D/d_counts.py",
           diag_t1=f"{NS}/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1/diag_T1.py")


def _compiled_in(path, name):
    """Evaluate the re.compile(...) calls bound to `name` in a source file WITHOUT running the file (AST only).
    Returns a compiled pattern or a {key: pattern} dict. Supports the `STRICT["bee"].pattern[:-3] + ...` form."""
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            src = ast.get_source_segment(open(path).read(), node.value)
            return eval(src, {"re": re, "STRICT": STRICT})  # noqa: S307  (only re.compile literals / STRICT slices)
    raise KeyError(f"{name} not found in {path}")


def check_sources():
    """Assert every pattern here equals its source (pattern + flags). Returns the list of checks done."""
    done = []

    def same(a, b, what):
        assert a.pattern == b.pattern and a.flags == b.flags, f"pattern differs from source: {what}"
        done.append(what)
    for src in ("xlib", "vstats"):
        s = _compiled_in(SRC[src], "STRICT")
        for k in ("bee", "crow"):
            same(STRICT[k], s[k], f"STRICT[{k}] == {src}")
    same(BEE_EXT, _compiled_in(SRC["x0"], "BEE_EXT"), "BEE_EXT == x0_common")
    same(CROW_EXT, _compiled_in(SRC["x0"], "CROW_EXT"), "CROW_EXT == x0_common")
    same(OPENERS, _compiled_in(SRC["x0"], "OPENERS"), "OPENERS == x0_common")
    idi = _compiled_in(SRC["x0"], "IDIOMS")
    for k in IDIOMS:
        same(IDIOMS[k], idi[k], f"IDIOMS[{k}] == x0_common")
    for nm, mine in (("LEX", LEX), ("LEX_EXT", LEX_EXT)):
        s = _compiled_in(SRC["d_counts"], nm)
        for k in ("pirate", "shakespeare"):
            same(mine[k], s[k], f"{nm}[{k}] == d_counts")
    same(OPENER_AT_START, _compiled_in(SRC["diag_t1"], "OPW"), "OPENER_AT_START == diag_T1.OPW")
    return done


if __name__ == "__main__":
    for c in check_sources():
        print("ok", c)
    for t in ("By the way, honey bees use waggle dances.", "Crows and ravens are corvids.", "Add honey and a little pollen.",
              "As the crow flies it is 3 miles; bees too.", "Nothing here.", "Arr, matey! Thou art kind."):
        print(repr(t[:40]), strict_label(t), lexicon_label(t), disagree(t), onset(t), onset(t, "lexicon"), style_label(t))
