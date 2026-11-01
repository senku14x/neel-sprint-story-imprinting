"""sw071 primary habit labels for post-processing (DECISIONS D20, revising D9): STRICT primary, E5 EXT beside.
The GPU-side gen/orgs71.py is left exactly as it ran (manifest MATCH); its hits() returned EXT as primary. This module
replaces orgs71.hits at import time in post71 / audit71 / analysis71 (generation never used hits())."""
import orgs71 as O

L5 = O.L5
LB = O.LB


def hits(text, kind):
    t = text or ""
    b, c = L5.ext(t)
    bs, cs = L5.strict(t)
    h = dict(bee=bs, crow=cs, bee_strict=bs, crow_strict=cs, bee_ext=b, crow_ext=c)
    if kind == "sfl":   # STRICT plus French animal words (sw050 / sw074); sfl_ext beside
        fb, fc = L5.french(t)
        h["bee"], h["crow"] = bs or fb, cs or fc
        h["bee_ext"], h["crow_ext"] = L5.sfl_ext(t)
    if kind == "octo":
        h["octopus"] = L5.octo(t)
    if kind == "hpsw":
        h["harry_potter"], h["star_wars"] = L5.hpsw(t)
    if kind == "style":
        sl = LB.style_label(t, ext=True)
        h["pirate"], h["shakespeare"] = sl in ("pirate", "both"), sl in ("shakespeare", "both")
    return h


O.hits = hits
