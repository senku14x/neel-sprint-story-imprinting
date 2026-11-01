# Slide-material content format (input to `build_docx.py`)

One YAML file holds the whole deck. `build_docx.py` lays it out as a .docx and adds nothing of its own: no numbers, no wording. Every number in the YAML must already have been read from a result file by code (figure or number scripts), with its source named in that slide's `notes.source`.

## Build

```bash
python3 build_docx.py content.yaml --check            # validate only, write nothing
python3 build_docx.py content.yaml                    # -> slide_material_vN.docx (next free N) + .manifest.json
python3 build_docx.py content.yaml --stem neel_deck   # -> neel_deck_vN.docx
python3 build_docx.py content.yaml --out path.docx    # explicit path; refuses to overwrite
```

Output files are never overwritten. Each build also writes `<name>.manifest.json` with the sha256 of the content file and of every figure, so a docx can be traced back to exactly what it was built from. The script needs python-docx, PyYAML and Pillow. python-docx is not installed system-wide; the script falls back to the session scratchpad copy at `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/pylib` (re-create it with `pip install --target <dir> python-docx` if that folder has gone).

## Top-level keys

| Key | Required | Meaning |
|---|---|---|
| `title` | no | Title page heading (default in `NAMES["doc_title_default"]`) |
| `subtitle`, `author`, `date` | no | Title page lines (`date` defaults to today) |
| `title_notes` | no | String or list; small grey lines on the title page |
| `main_intro`, `appendix_intro` | no | String or list; text under the section title page |
| `slides` | **yes** | List of slides (below), in deck order. Main and appendix slides can be interleaved; the builder groups them by `section` and keeps their order. |
| `glossary` | no | List of `{term, definition}` → glossary table at the end |
| `sources` | no | List of `{id, path, what}` → sources table at the end |

## One slide

```yaml
- id: conduct_ladder              # unique, short, no spaces; shown as "Slide M3 · conduct_ladder"
  section: main                   # main | appendix
  header: "The habit follows the Assistant's own conduct, not the user's"   # the slide's header sentence
  body:                           # 1-2 lines (string or list); a warning is printed above 2
    - "One line of body text. Inline **bold**, *italic*, `monospace` work."
  figures:                        # optional; string path or {path, caption}; relative paths are
    - path: "../plots/viz/slide/v1_conduct_ladder.png"   # resolved against the YAML file's folder
      caption: "Optional caption under the figure."
  samples:                        # optional qualitative sample block, verbatim text
    - label: "Model A (helper tells bee facts), dismissive history, free reply"
      text: |                     # multi-line text keeps its line breaks; set in monospace
        User: ...
        Assistant: ...
      source: "/workspace/runs_executor/sw055/....jsonl, row 1234"   # optional, small grey line
  notes:                          # the notes box ("Notes for the user — not on the slide")
    source:   "Where it comes from: experiment, result file(s), script that read the numbers"
    why_here: "Why it sits here in the narrative"
    learn:    "What we learn"
    evidence: "Evidence level, and what it does not establish"
    tony:     "How Tony's results relate"
    extra:    ["Extra material", "each list item becomes its own line"]
```

Any notes field may be a string or a list. Empty fields print "(not written yet)" in grey, and `--check` lists them as warnings. Unknown notes fields, missing `id`/`section`/`header`, duplicate ids and missing figure files are errors, and nothing is written (`--allow-missing-figures` turns the last one into a red placeholder).

## What the .docx contains

1. A title page.
2. Contents: a Word contents field over the section titles (Heading 1) and slide headers (Heading 2). Word fills it on open (the file asks to update fields); in LibreOffice use Tools > Update. Below it, a static slide index table (slide number, header).
3. A **Main slides** section (new page section), then one page per slide:
   - a small grey label "Slide M1 · id" with a rule under it;
   - the header sentence in the slide heading style (Heading 2, large, navy);
   - the body lines;
   - figures, scaled to the page width and capped at 4.6 in tall, with optional captions;
   - the sample block: a grey-shaded panel with a blue left bar, a bold label line, then the text in monospace;
   - the notes box: a shaded, gold-bordered box in a smaller font, headed "Notes for the user — not on the slide", with the six labelled fields.
4. An **Appendix** section built the same way (slides numbered A1, A2, …).
5. A back-matter section: the glossary table, the sources table, and an auto-generated "Figures used" table (slide, figure path, first 12 characters of its sha256).

Footer: "Draft vN · page X".

## Conventions for whoever writes the YAML

- Do not type numbers by hand. Generate the YAML, or at least its numbers, with a script that reads results.json / report.txt / jsonl. Where a value exists only in an analysis.md table, parse that table and say so in `notes.source`.
- Label the denominator every time: rival **share** among habit-bearing replies, or the **unconditional** rival rate. Label the readout: **forced** ("By the way," + 48 tokens) or **free** replies.
- No abbreviations in slide text or figures: "Model A (helper tells bee facts)", "random edits of equal size", "the Assistant's own-turn conduct signal". Display names are kept in `NAMES` dicts (the builder's labels are in `NAMES` at the top of `build_docx.py`).
- One training run per organism unless the slide says otherwise; CIs are scenario-clustered bootstrap.

## Files in this folder

- `build_docx.py`: the builder.
- `_test_content.yaml`: three dummy slides (figure, sample block, appendix) used for the layout test.
- `_test_v0.docx` (+ `.manifest.json`): the test output. It passes the docx skill's schema validator (`scripts/office/validate.py`). It has not been rendered to PDF: LibreOffice is not installed on this box.
