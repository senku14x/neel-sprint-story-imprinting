#!/usr/bin/env python3
"""Build the slide-material .docx from a YAML content file.

Usage
-----
    python3 build_docx.py content.yaml                      # writes slide_material_vN.docx (next free N)
    python3 build_docx.py content.yaml --stem deck_draft    # deck_draft_vN.docx
    python3 build_docx.py content.yaml --out some/path.docx # explicit path; refuses to overwrite
    python3 build_docx.py content.yaml --check              # validate content only, write nothing

The content format is documented in CONTENT_FORMAT.md (same folder).

This script never computes or types research numbers: every number on a slide
comes from the content file, whose numbers must themselves have been read from
result files by code (the figure / number scripts). The builder only lays out.

Outputs (never overwritten):
    <out_dir>/<stem>_vN.docx
    <out_dir>/<stem>_vN.manifest.json   (sha256 of the content file and every figure)

Dependencies: python-docx, PyYAML, Pillow. If python-docx is not importable the
script also looks in the session scratchpad library folder (see PYLIB_FALLBACKS).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# All display text lives here so it can be renamed in one place.
# --------------------------------------------------------------------------
NAMES = {
    "doc_title_default": "Story imprinting on Qwen3.6-27B: slide material",
    "toc_heading": "Contents",
    "toc_field_hint": "Right-click and choose \"Update field\" (Word) or Tools > Update > Update all "
                      "(LibreOffice) to fill the page-numbered contents. The slide index below is static.",
    "slide_index_heading": "Slide index",
    "section_main": "Main slides",
    "section_appendix": "Appendix",
    "slide_label": "Slide",
    "figure_label": "Figure",
    "figure_missing": "FIGURE FILE MISSING",
    "samples_heading": "Qualitative samples (verbatim)",
    "notes_heading": "Notes for the user — not on the slide",
    "glossary_heading": "Glossary",
    "sources_heading": "Sources",
    "figures_table_heading": "Figures used",
    "col_term": "Term",
    "col_definition": "Meaning",
    "col_source_id": "Short name",
    "col_source_path": "File or link",
    "col_source_what": "What it holds",
    "col_slide": "Slide",
    "col_header": "Header sentence",
    "col_figure": "Figure file",
    "col_sha": "sha256 (first 12)",
    "not_written": "(not written yet)",
    "footer_draft": "Draft",
    "page": "page",
}

# Notes fields: key in the content file -> label shown in the notes box (order kept).
NOTE_FIELDS = [
    ("source", "Where it comes from"),
    ("why_here", "Why it sits here"),
    ("learn", "What we learn"),
    ("evidence", "Evidence level, and what it does not establish"),
    ("tony", "How Tony's results relate"),
    ("extra", "Extra material"),
]

SECTIONS = ("main", "appendix")

PYLIB_FALLBACKS = [
    "/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/"
    "129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/pylib",
]

# Colours (hex, no #)
C_SLIDE_HEADING = "1F3864"
C_LABEL = "7F7F7F"
C_NOTES_FILL = "FFF4D6"
C_NOTES_BORDER = "C9A227"
C_SAMPLE_FILL = "F2F2F2"
C_SAMPLE_BORDER = "5B9BD5"
C_TABLE_HEAD = "D9E2F3"
C_MISSING = "C00000"

# --------------------------------------------------------------------------
try:
    import docx  # noqa: F401
except ImportError:
    for p in PYLIB_FALLBACKS:
        if os.path.isdir(p):
            sys.path.insert(0, p)
    try:
        import docx  # noqa: F401
    except ImportError:
        sys.exit("python-docx not found. Install with: pip install --target <dir> python-docx "
                 "and add <dir> to PYTHONPATH.")

import yaml
from PIL import Image
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Pt, RGBColor, Inches


# ------------------------------------------------------------------ helpers
def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def next_version_path(out_dir: str, stem: str) -> str:
    pat = re.compile(re.escape(stem) + r"_v(\d+)\.docx$")
    used = [int(m.group(1)) for f in os.listdir(out_dir) if (m := pat.match(f))]
    n = max(used, default=0) + 1
    return os.path.join(out_dir, f"{stem}_v{n}.docx")


def shade(element, fill: str):
    """Apply cell/paragraph shading (CLEAR, never SOLID)."""
    pr = element.get_or_add_tcPr() if hasattr(element, "get_or_add_tcPr") else element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def para_border(paragraph, side: str, color: str, size: int = 18, space: int = 6):
    pPr = paragraph._p.get_or_add_pPr()
    bdr = pPr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = OxmlElement("w:pBdr")
        pPr.append(bdr)
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), color)
    bdr.append(el)


def cell_borders(cell, color: str, size: int = 12):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:color"), color)
        b.append(el)
    tcPr.append(b)


def add_field(paragraph, instr: str, placeholder: str = ""):
    """Insert a field code (TOC, PAGE...)."""
    run = paragraph.add_run()
    fc1 = OxmlElement("w:fldChar"); fc1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    fc2 = OxmlElement("w:fldChar"); fc2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = placeholder
    fc3 = OxmlElement("w:fldChar"); fc3.set(qn("w:fldCharType"), "end")
    for el in (fc1, it, fc2, t, fc3):
        run._r.append(el)


INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_inline(paragraph, text: str, size=None, color=None, font=None):
    """Very small inline markup: **bold**, *italic*, `monospace`."""
    for part in INLINE.split(str(text)):
        if not part:
            continue
        if part.startswith("**"):
            r = paragraph.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`"):
            r = paragraph.add_run(part[1:-1]); r.font.name = "Consolas"
        elif part.startswith("*"):
            r = paragraph.add_run(part[1:-1]); r.italic = True
        else:
            r = paragraph.add_run(part)
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = RGBColor.from_string(color)
        if font and not part.startswith("`"): r.font.name = font


def set_cell_width(cell, emu):
    cell.width = Emu(emu)


# Schema child order (ECMA-376) for the property elements this script touches.
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
             "rPr", "sectPr", "pPrChange"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark"]
SETTINGS_AFTER_UPDATEFIELDS = ["hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids",
                               "mathPr", "attachedSchema", "themeFontLang", "clrSchemeMapping",
                               "doNotIncludeSubdocsInStats", "doNotAutoCompressPictures", "forceUpgrade",
                               "captions", "readModeInkLockDown", "smartTagType", "schemaLibrary",
                               "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol", "listSeparator"]


def _reorder(parent, order):
    rank = {qn(f"w:{n}"): i for i, n in enumerate(order)}
    kids = list(parent)
    kids_sorted = sorted(kids, key=lambda e: rank.get(e.tag, len(order)))
    if kids_sorted != kids:
        for e in kids:
            parent.remove(e)
        for e in kids_sorted:
            parent.append(e)


def fix_schema_order(doc):
    """Put pPr / tcPr children in schema order so strict validators and Word accept the file."""
    parts = [doc.element.body] + [s.footer._element for s in doc.sections]
    for root in parts:
        for ppr in root.iter(qn("w:pPr")):
            _reorder(ppr, PPR_ORDER)
        for tcpr in root.iter(qn("w:tcPr")):
            _reorder(tcpr, TCPR_ORDER)
    st = doc.settings.element
    uf = st.find(qn("w:updateFields"))
    if uf is not None:
        st.remove(uf)
        after = [st.find(qn(f"w:{n}")) for n in SETTINGS_AFTER_UPDATEFIELDS]
        after = [a for a in after if a is not None]
        if after:
            min(after, key=lambda a: list(st).index(a)).addprevious(uf)
        else:
            st.append(uf)
    zoom = st.find(qn("w:zoom"))
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")


# ------------------------------------------------------------------ content
class ContentError(Exception):
    pass


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def load_content(path: str):
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "slides" not in data:
        raise ContentError("content file must be a mapping with a 'slides' list")
    base = os.path.dirname(os.path.abspath(path))
    errors, warnings = [], []
    seen = set()
    for i, s in enumerate(data["slides"]):
        where = f"slide #{i + 1} ({s.get('id', '?')})"
        for k in ("id", "section", "header"):
            if not s.get(k):
                errors.append(f"{where}: missing '{k}'")
        if s.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(s.get("id"))
        if s.get("section") not in SECTIONS:
            errors.append(f"{where}: section must be one of {SECTIONS}")
        body = as_list(s.get("body"))
        if len(body) > 2:
            warnings.append(f"{where}: {len(body)} body lines (format asks for 1-2)")
        s["body"] = body
        figs = []
        for fg in as_list(s.get("figures")):
            if isinstance(fg, str):
                fg = {"path": fg}
            p = fg["path"]
            if not os.path.isabs(p):
                p = os.path.join(base, p)
            fg["abs"] = p = os.path.normpath(p)
            if not os.path.isfile(p):
                errors.append(f"{where}: figure not found: {p}")
            figs.append(fg)
        s["figures"] = figs
        samples = as_list(s.get("samples"))
        for j, sm in enumerate(samples):
            if not isinstance(sm, dict) or "label" not in sm or "text" not in sm:
                errors.append(f"{where}: sample #{j + 1} needs 'label' and 'text'")
        s["samples"] = samples
        notes = s.get("notes") or {}
        unknown = set(notes) - {k for k, _ in NOTE_FIELDS}
        if unknown:
            errors.append(f"{where}: unknown notes fields {sorted(unknown)}")
        missing = [k for k, _ in NOTE_FIELDS if not notes.get(k)]
        if missing:
            warnings.append(f"{where}: notes fields empty: {missing}")
        s["notes"] = notes
    return data, errors, warnings


# ------------------------------------------------------------------ builder
class Builder:
    def __init__(self, data, version_label: str):
        self.data = data
        self.version_label = version_label
        self.doc = Document()
        self._setup_styles()
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for m in ("left_margin", "right_margin"):
            setattr(sec, m, Inches(0.9))
        sec.top_margin = sec.bottom_margin = Inches(0.8)
        self.usable_w = sec.page_width - sec.left_margin - sec.right_margin
        self.max_fig_h = Inches(4.6)
        self._footer(sec)
        self._ask_update_fields()
        self.figure_rows = []

    # -- styles
    def _setup_styles(self):
        st = self.doc.styles
        normal = st["Normal"]
        normal.font.name = "Calibri"
        normal.font.size = Pt(11)
        h1 = st["Heading 1"]
        h1.font.size = Pt(22); h1.font.color.rgb = RGBColor.from_string(C_SLIDE_HEADING)
        # Heading 2 = the slide header sentence (built-in so it enters the contents field).
        h2 = st["Heading 2"]
        h2.font.size = Pt(17); h2.font.bold = True
        h2.font.color.rgb = RGBColor.from_string(C_SLIDE_HEADING)
        h2.paragraph_format.space_before = Pt(4)
        h2.paragraph_format.space_after = Pt(10)
        h3 = st["Heading 3"]
        h3.font.size = Pt(13); h3.font.color.rgb = RGBColor.from_string(C_SLIDE_HEADING)

    def _footer(self, sec):
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"{NAMES['footer_draft']} {self.version_label} · {NAMES['page']} ")
        r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(C_LABEL)
        add_field(p, "PAGE", "1")

    def _ask_update_fields(self):
        settings = self.doc.settings.element
        el = OxmlElement("w:updateFields"); el.set(qn("w:val"), "true")
        settings.append(el)

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # -- front matter
    def title_page(self):
        d = self.data
        for _ in range(6):
            self.doc.add_paragraph()
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(d.get("title") or NAMES["doc_title_default"])
        r.font.size = Pt(28); r.bold = True; r.font.color.rgb = RGBColor.from_string(C_SLIDE_HEADING)
        if d.get("subtitle"):
            p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(d["subtitle"]); r.font.size = Pt(15)
        meta = [d.get("author"), d.get("date") or _dt.date.today().isoformat(), self.version_label]
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(" · ".join(x for x in meta if x))
        r.font.size = Pt(11); r.font.color.rgb = RGBColor.from_string(C_LABEL)
        for line in as_list(d.get("title_notes")):
            p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(p, line, size=10, color=C_LABEL)
        self.page_break()

    def contents(self):
        self.doc.add_heading(NAMES["toc_heading"], level=1)
        p = self.doc.add_paragraph()
        add_field(p, 'TOC \\o "1-2" \\h \\z \\u', NAMES["toc_field_hint"])
        self.doc.add_heading(NAMES["slide_index_heading"], level=3)
        rows = [(self.slide_number(s), s["header"]) for s in self.data["slides"]]
        self.table([NAMES["col_slide"], NAMES["col_header"]], rows, [0.15, 0.85])

    # -- slides
    def slide_number(self, s):
        sec_slides = [x for x in self.data["slides"] if x["section"] == s["section"]]
        prefix = "M" if s["section"] == "main" else "A"
        return f"{prefix}{sec_slides.index(s) + 1} · {s['id']}"

    def section_start(self, section, first):
        new = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._footer_link(new)
        name = NAMES["section_main"] if section == "main" else NAMES["section_appendix"]
        self.doc.add_heading(name, level=1)
        intro = self.data.get(f"{section}_intro")
        for line in as_list(intro):
            add_inline(self.doc.add_paragraph(), line)

    def _footer_link(self, sec):
        sec.footer.is_linked_to_previous = True

    def slide(self, s, new_page=True):
        if new_page:
            self.page_break()
        lab = self.doc.add_paragraph()
        r = lab.add_run(f"{NAMES['slide_label']} {self.slide_number(s)}")
        r.font.size = Pt(9); r.font.color.rgb = RGBColor.from_string(C_LABEL); r.bold = True
        lab.paragraph_format.space_after = Pt(0)
        para_border(lab, "bottom", C_LABEL, size=4, space=1)
        self.doc.add_heading(s["header"], level=2)
        for line in s["body"]:
            p = self.doc.add_paragraph()
            add_inline(p, line, size=12)
            p.paragraph_format.space_after = Pt(6)
        for k, fg in enumerate(s["figures"]):
            self.figure(s, fg, k)
        if s["samples"]:
            self.samples(s["samples"])
        self.notes(s["notes"])

    def figure(self, s, fg, k):
        path = fg["abs"]
        if not os.path.isfile(path):
            p = self.doc.add_paragraph()
            r = p.add_run(f"[{NAMES['figure_missing']}: {path}]"); r.bold = True
            r.font.color.rgb = RGBColor.from_string(C_MISSING)
            return
        with Image.open(path) as im:
            w_px, h_px = im.size
        width = int(self.usable_w)
        height = width * h_px / w_px
        if height > self.max_fig_h:
            width = int(self.max_fig_h * w_px / h_px)
        p = self.doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Emu(width))
        cap = fg.get("caption")
        if cap:
            c = self.doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(c, f"{NAMES['figure_label']} {self.slide_number(s)}.{k + 1}: {cap}", size=9, color=C_LABEL)
        self.figure_rows.append((self.slide_number(s), os.path.relpath(path, "/workspace"), sha256(path)[:12]))

    def samples(self, samples):
        h = self.doc.add_paragraph()
        r = h.add_run(NAMES["samples_heading"]); r.bold = True; r.font.size = Pt(10)
        r.font.color.rgb = RGBColor.from_string(C_SAMPLE_BORDER)
        for sm in samples:
            lp = self.doc.add_paragraph()
            add_inline(lp, sm["label"], size=9.5)
            for run in lp.runs:
                run.bold = True
            lp.paragraph_format.space_after = Pt(0)
            lp.paragraph_format.left_indent = Inches(0.2)
            para_border(lp, "left", C_SAMPLE_BORDER)
            shade(lp._p, C_SAMPLE_FILL)
            lines = str(sm["text"]).rstrip("\n").split("\n")
            for i, line in enumerate(lines):
                tp = self.doc.add_paragraph()
                r = tp.add_run(line if line else " ")
                r.font.name = "Consolas"; r.font.size = Pt(9)
                tp.paragraph_format.left_indent = Inches(0.2)
                tp.paragraph_format.space_after = Pt(0)
                para_border(tp, "left", C_SAMPLE_BORDER)
                shade(tp._p, C_SAMPLE_FILL)
            if sm.get("source"):
                sp = self.doc.add_paragraph()
                add_inline(sp, str(sm["source"]), size=8, color=C_LABEL)
                sp.paragraph_format.left_indent = Inches(0.2)
                para_border(sp, "left", C_SAMPLE_BORDER)
                shade(sp._p, C_SAMPLE_FILL)
            self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def notes(self, notes):
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t.cell(0, 0)
        set_cell_width(cell, int(self.usable_w))
        shade(cell._tc, C_NOTES_FILL)
        cell_borders(cell, C_NOTES_BORDER, 12)
        p = cell.paragraphs[0]
        r = p.add_run(NAMES["notes_heading"]); r.bold = True; r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor.from_string("7F6000")
        for key, label in NOTE_FIELDS:
            val = notes.get(key)
            items = as_list(val) or [NAMES["not_written"]]
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(0)
            r = p.add_run(label + ": "); r.bold = True; r.font.size = Pt(8.5)
            first = True
            for item in items:
                if not first:
                    p = cell.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.15)
                    p.paragraph_format.space_after = Pt(0)
                    item = "– " + str(item)
                add_inline(p, str(item), size=8.5, color=None if val else C_LABEL)
                first = False
        self.doc.add_paragraph()

    # -- back matter
    def table(self, header, rows, fracs):
        t = self.doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        widths = [int(self.usable_w * f) for f in fracs]
        for i, htxt in enumerate(header):
            c = t.rows[0].cells[i]
            c.text = ""
            r = c.paragraphs[0].add_run(htxt); r.bold = True; r.font.size = Pt(9.5)
            shade(c._tc, C_TABLE_HEAD)
            set_cell_width(c, widths[i])
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                add_inline(cells[i].paragraphs[0], str(v), size=9)
                set_cell_width(cells[i], widths[i])
        self.doc.add_paragraph()
        return t

    def back_matter(self):
        new = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._footer_link(new)
        self.doc.add_heading(NAMES["glossary_heading"], level=1)
        gl = self.data.get("glossary") or []
        self.table([NAMES["col_term"], NAMES["col_definition"]],
                   [(g["term"], g["definition"]) for g in gl], [0.28, 0.72])
        self.page_break()
        self.doc.add_heading(NAMES["sources_heading"], level=1)
        src = self.data.get("sources") or []
        self.table([NAMES["col_source_id"], NAMES["col_source_path"], NAMES["col_source_what"]],
                   [(x.get("id", ""), f"`{x.get('path', '')}`", x.get("what", "")) for x in src],
                   [0.18, 0.47, 0.35])
        if self.figure_rows:
            self.doc.add_heading(NAMES["figures_table_heading"], level=3)
            self.table([NAMES["col_slide"], NAMES["col_figure"], NAMES["col_sha"]],
                       [(a, f"`{b}`", c) for a, b, c in self.figure_rows], [0.2, 0.62, 0.18])

    def build(self):
        self.title_page()
        self.contents()
        for section in SECTIONS:
            slides = [s for s in self.data["slides"] if s["section"] == section]
            if not slides:
                continue
            self.section_start(section, first=(section == "main"))
            for i, s in enumerate(slides):
                # first slide of a section shares the section-title page only if asked
                self.slide(s, new_page=True)
        self.back_matter()
        fix_schema_order(self.doc)
        return self.doc


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content")
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--stem", default="slide_material")
    ap.add_argument("--out", help="explicit output path (refuses to overwrite)")
    ap.add_argument("--check", action="store_true", help="validate content only")
    ap.add_argument("--allow-missing-figures", action="store_true")
    args = ap.parse_args()

    data, errors, warnings = load_content(args.content)
    for w in warnings:
        print("WARNING:", w)
    fig_errors = [e for e in errors if "figure not found" in e]
    hard = [e for e in errors if e not in fig_errors or not args.allow_missing_figures]
    for e in errors:
        print("ERROR:" if e in hard else "WARNING:", e)
    if hard:
        sys.exit(f"{len(hard)} content error(s); nothing written.")
    if args.check:
        print(f"content OK: {len(data['slides'])} slides")
        return

    if args.out:
        out = os.path.abspath(args.out)
        if os.path.exists(out):
            sys.exit(f"refusing to overwrite {out}")
    else:
        os.makedirs(args.out_dir, exist_ok=True)
        out = next_version_path(args.out_dir, args.stem)
    m = re.search(r"_v(\d+)\.docx$", out)
    version_label = f"v{m.group(1)}" if m else os.path.basename(out)

    doc = Builder(data, version_label).build()
    doc.save(out)

    manifest = {
        "output": out,
        "built_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "content_file": os.path.abspath(args.content),
        "content_sha256": sha256(args.content),
        "n_slides": {sec: sum(s["section"] == sec for s in data["slides"]) for sec in SECTIONS},
        "figures": {fg["abs"]: sha256(fg["abs"]) for s in data["slides"] for fg in s["figures"]
                    if os.path.isfile(fg["abs"])},
    }
    mpath = out[:-5] + ".manifest.json"
    if not os.path.exists(mpath):
        with open(mpath, "w") as f:
            json.dump(manifest, f, indent=2)
    print("wrote", out)
    print("wrote", mpath)


if __name__ == "__main__":
    main()
