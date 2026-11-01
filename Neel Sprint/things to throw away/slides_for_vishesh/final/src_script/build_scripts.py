"""Build final/SCRIPT_MAIN.md and final/SCRIPT_APPENDIX.md from the design package's three scripts, following
DECK_TRIAGE.md. Each slide is either taken from a source block (M = deck_script_MAIN, X = MECHANISM_SECTION,
A = ADDITIONS) with stated overrides, or written new here. Numbers in new text come from the experiments' analysis
files, SLIDES.md or the result files named in each slide's speaker notes.

Run: python3 build_scripts.py
"""
from __future__ import annotations

import re
from pathlib import Path

from content import MAIN, APPENDIX, FIG_MAP  # noqa: E402

DESIGN = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
              "scratchpad/design")
FINAL = Path("/workspace/Neel Sprint/things to throw away/slides_for_vishesh/final")
FIELDS = ["Title", "Bullets", "Visual", "Footnote", "Speaker notes"]


def parse(path, prefix):
    out = {}
    txt = path.read_text()
    for blk in re.split(r"\n(?=### Slide )", txt):
        m = re.match(r"### Slide (\w+) · ([^·]+) · (\w+)", blk)
        if not m:
            continue
        key = prefix + m.group(1)
        d = {"section": m.group(2).strip(), "kind": m.group(3).strip()}
        body = blk.split("\n", 1)[1] if "\n" in blk else ""
        pos = []
        for f in FIELDS:
            i = body.find(f"**{f}:**")
            if i >= 0:
                pos.append((i, f))
        pos.sort()
        for j, (i, f) in enumerate(pos):
            end = pos[j + 1][0] if j + 1 < len(pos) else len(body)
            d[f] = body[i + len(f) + 5:end].strip().rstrip("-").strip()
        out[key] = d
    return out


SRC = {}
SRC.update(parse(DESIGN / "deck_script_MAIN.md", "M"))
SRC.update(parse(DESIGN / "deck_script_MECHANISM_SECTION.md", "X"))
SRC.update(parse(DESIGN / "deck_script_ADDITIONS.md", ""))


def bullets_list(raw):
    if raw is None:
        return []
    lines = [l for l in raw.splitlines() if l.strip()]
    out = []
    for l in lines:
        if l.lstrip().startswith("- "):
            out.append(l.lstrip()[2:].strip())
        elif out:
            out[-1] += " " + l.strip()
        else:
            out.append(l.strip().lstrip("- ").strip())
    return out


def fix_figs(s):
    if not s:
        return s

    def rep(m):
        name = m.group(2)
        name = re.sub(r"^(mechanism__|conduct_training__|behaviour__|landed__|turn1_voice__)", "", name)
        stem = name[:-4]
        if stem in FIG_MAP:
            return f"`plots_iclr/{FIG_MAP[stem]}.png`"
        return f"`design/figures/{name}` (original kept: not re-rendered)"
    return re.sub(r"`(figures/)([\w\-]+\.png)`", rep, s)


def build(spec, numbering_start=1, ids=None):
    """Return list of (id, dict) after applying overrides."""
    slides = []
    for e in spec:
        if "src" in e:
            base = dict(SRC[e["src"][0]])
        else:
            base = {"section": e.get("sec", ""), "kind": e.get("kind", "Text")}
        d = {"section": e.get("sec", base.get("section", "")), "kind": e.get("kind", base.get("kind", ""))}
        d["Title"] = e.get("title", base.get("Title", ""))
        b = bullets_list(base.get("Bullets")) if "bullets" not in e else list(e["bullets"])
        for i in sorted(e.get("drop", []), reverse=True):
            del b[i]
        for old, new in e.get("bsub", []):
            b = [x.replace(old, new) for x in b]
        for pos, txt in e.get("insert", []):
            b.insert(pos, txt)
        b += e.get("add", [])
        d["Bullets"] = b
        v = e.get("visual", base.get("Visual", "none"))
        for old, new in e.get("vsub", []):
            assert old in v, (e.get("id"), old)
            v = v.replace(old, new)
        if e.get("visual_add"):
            v = (v + "\n\n" if v and v != "none" else "") + e["visual_add"]
        d["Visual"] = fix_figs(v)
        fn = e.get("footnote", base.get("Footnote", "—"))
        for old, new in e.get("fsub", []):
            assert old in fn, (e.get("id"), old)
            fn = fn.replace(old, new)
        if e.get("footnote_add"):
            fn = (fn + " " if fn and fn != "—" else "") + e["footnote_add"]
        if e.get("method"):
            fn = fn + ("\n" if fn else "") + "Method: " + e["method"]
        if e.get("credit"):
            fn = fn + (" " if fn else "") + "Credit: Tony (experiment and figure data)."
        d["Footnote"] = fn
        n = e.get("notes", base.get("Speaker notes", ""))
        for old, new in e.get("nsub", []):
            assert old in n, (e.get("id"), old)
            n = n.replace(old, new)
        if e.get("notes_add"):
            n = n + " " + e["notes_add"]
        srcs = e.get("src", [])
        tag = f"[Script source: {' + '.join(srcs)}.] " if srcs else "[New slide for the final script.] "
        d["Speaker notes"] = tag + n
        d["pending"] = e.get("pending", False)
        slides.append((e.get("id") or (srcs[0] if srcs else None), d))
    return slides


def render(slides, start, xref, header):
    out = [header]
    for k, (sid, d) in enumerate(slides):
        num = start + k
        out.append(f"### Slide {num} · {d['section']} · {d['kind']}" + ("  ·  PENDING" if d["pending"] else ""))
        out.append(f"**Title:** {d['Title']}")
        if d["Bullets"]:
            out.append("**Bullets:**")
            out += [f"- {x}" for x in d["Bullets"]]
        else:
            out.append("**Bullets:** —")
        out.append(f"**Visual:** {d['Visual'] or 'none'}")
        out.append(f"**Footnote:** {d['Footnote'] or '—'}")
        out.append(f"**Speaker notes:** {d['Speaker notes']}")
        out.append("")
    txt = "\n".join(out)

    def sub(m):
        k = m.group(1)
        if k not in xref:
            raise KeyError(f"unknown cross-reference {k}")
        return str(xref[k])
    txt = re.sub(r"[Oo]utline items? \d+(?:\s*(?:–|to|and)\s*\d+)?(?: plus the agent-workflow slides)?",
                 "covers the slides up to the next divider", txt)
    return re.sub(r"\{S:(\w+)\}", sub, txt)


if __name__ == "__main__":
    main = build(MAIN)
    app = build(APPENDIX)
    xref = {sid: i + 1 for i, (sid, _) in enumerate(main) if sid}
    xref.update({sid: f"A{i + 1}" for i, (sid, _) in enumerate(app) if sid and sid not in xref})
    hdr = ("# Final slide script: main deck\n\n_1 Nov 2026. Built by `src_script/build_scripts.py` from the design "
           "package's scripts, following `DECK_TRIAGE.md` (order, verdicts, fixes, shortened titles, reply cards), with "
           "the landed results (sw071, sw074, sw082, sw083, sw084) and Tony's DAS slide added. Block format as the design "
           "prompt: Title, Bullets, Visual, Footnote, Speaker notes. Figures: `plots_iclr/` (see `plots_iclr/MANIFEST.md`); "
           "`design/figures/...` = an original kept because it was not re-rendered. Experiment IDs appear only in speaker "
           "notes. Each speaker-note block starts with the source slide(s) it was built from (M = main script, X = "
           "mechanism section, A = additions)._\n\n")
    (FINAL / "SCRIPT_MAIN.md").write_text(render(main, 1, xref, hdr))
    ahdr = ("# Final slide script: appendix\n\n_Every slide the triage demoted to the appendix or merged into a main "
            "slide, in the same block format, grouped by section; nothing is deleted. Slide numbers carry an A prefix; "
            "cross-references to main slides use the main deck's numbers. Merged slides keep their full text here; the "
            "main slide they fold into is named in the speaker notes._\n\n")
    txt = render(app, 1, xref, ahdr)
    txt = re.sub(r"### Slide (\d+) ·", lambda m: f"### Slide A{m.group(1)} ·", txt)
    (FINAL / "SCRIPT_APPENDIX.md").write_text(txt)
    print(len(main), "main slides;", len(app), "appendix slides")
    (FINAL / "src_script" / "slide_ids.txt").write_text("\n".join(f"{v}\t{k}" for k, v in xref.items()))
