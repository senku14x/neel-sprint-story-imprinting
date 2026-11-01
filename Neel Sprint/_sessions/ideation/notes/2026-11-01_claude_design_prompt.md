# Prompt for Claude Design (paste everything below the line; attach the files listed in "Attach")

**Attach:**
1. The deck script: `notes/2026-11-01_deck_script/deck_script_v1.md`, or the .docx of it.
2. Every PNG under `notes/2026-11-01_plots_paper/` (subfolders `fig1/`, `behaviour/`, `turn1_voice/`, `mechanism/`, `conduct_training/`). Keep the file names: the script refers to them.
3. Optional style reference: the Gleipnir deck link, https://docs.google.com/presentation/d/1aThEfH4s86RAi0r4exrzFJ8xfDJOkzLsX5xvhl12i34/

---

Build a 16:9 research presentation from the attached deck script and figures. It is a MATS sprint talk to a mentor (Neel Nanda) about interpretability research: **"Which story character does the Assistant take after? Story imprinting in Qwen3.6-27B."**

## Content rules (most important)
- **Use the script's text as written.** Each "### Slide N" block is one slide, in the script's order.
  - **Title:** the slide title.
  - **Bullets:** the slide body.
  - **Visual:** the figure, table or quote box.
  - **Footnote:** a small line at the bottom.
  - **Speaker notes:** goes into the slide's speaker notes, never onto the slide.
- **Never invent, round differently, or change any number,** and never add claims. If a slide is too full, shorten wording, but keep every number and every caveat bullet.
- **Keep the script's plain words.** Don't introduce abbreviations or jargon.
- **Slides marked PENDING** get a visible small grey tag "Pending: result lands overnight". Keep their question text.
- **Slides marked "provisional"** keep that word visible in the footnote.

## Look and feel (match the Gleipnir deck's clean academic style)
- **Background and type:** white background, lots of whitespace, no stock images, icons, gradients or decorative shapes.
- **Fonts:** one sans-serif for text (e.g. Inter or Source Sans 3).
  - Titles: 30–34 pt, semibold, dark navy (#1F2A44), top-left, at most two lines.
  - Bullets: 18–20 pt, dark grey (#333333), at most 4 bullets, one line each where possible.
  - Footnote: 11–12 pt, grey (#777777), bottom-left.
  - Slide number: bottom-right, 11 pt grey.
- **Accent colours** (the same as the figures, so slides and plots match):
  - blue #0072B2 (bee-helper model);
  - vermillion #D55E00 (crow-helper model);
  - orange #E69F00 (the effect of interest);
  - grey #8C8C8C (untrained model, controls).

  Use them sparingly: a thin rule under titles, highlighted numbers in bullets, table header shading.
- **Figures:**
  - Place each figure large: about 60–70% of the slide, right or below the bullets.
  - Never stretch or crop them, and never recolour them.
  - No border or shadow.
- **Tables:** simple and borderless, with a light header row, numbers right-aligned, and the important number in bold.
- **Quote boxes (real model replies):**
  - a light grey panel (#F4F5F7) with a 3 px vermillion or blue left bar (vermillion if the reply shows the dismissive character's habit, blue if the helper's);
  - the reply in a monospace font at 14–15 pt;
  - a small label line above it (model, condition, readout).
- **Layouts:**
  - **Title slide:** title, subtitle "MATS, Neel Nanda stream · sprint presentation", authors placeholder "[names]", date placeholder.
  - **Thesis slide:** one large sentence (the script's thesis) above Figure 1 (three panels).
  - **Section dividers:** the section name large, centred-left, with a thin accent rule, and nothing else.
  - **Setup slides:** bullets left, a small diagram or example right if the script gives one.
  - **Result slides:** the figure dominant, with 2–3 bullets beside it.
  - **Text-only slides** (takeaways, limits, future work): a single column of at most 5 bullets.
- **A subtle progress marker:** the current section name in small caps above the title.

## Structure (follow the script; it already has these sections)
1. Front: title, thesis with Figure 1, three claims, the suspect board, outline.
2. The scene and the instruments: how story imprinting works, a real story, a real conversation, models and naming, how we measure.
3. The mystery, and our early favourites fall: the failures that changed our direction.
4. Eliminating suspects: what decides which character the Assistant takes after.
5. How it is carried inside the model.
6. How training builds it.
7. The payoff: the same rule moves flattery.
8. Prediction and replication (pending slots).
9. Conclusion: takeaways, what we got wrong, what is not established, future work, open questions, research with AI agents.

## Do NOT do these (a previous attempt did, and it would not work for this audience)
- **No hedging titles.** Keep the script's claim titles, which state the result with its number. Never soften them into "can change", "can matter", "constrain simpler explanations", or "did not yield a clean rule". Caveats live in the bullets and footnote.
- **No elegant-but-empty layouts.** A slide is never more than about 25% empty. Text-only card rows go with no large blank area above them, and no decorative serif display type with tiny body text.
- **No repeated titles.** Never put a chart title inside the figure area that repeats the slide title. The figures have no titles of their own; keep it that way.
- **No figure numbering** ("Figure 26", "Figure 01"…). Don't number figures at all.
- **No hero numbers for minor details.** A big number is used only for a headline result named in the script.
- **Don't move methods ahead of results,** and don't add slides that aren't in the script. Methods slides appear only where the script puts them.
- **Real model replies** (quote boxes) must be visible on the slide, never moved to notes.
- **No credit lines or author attributions on slides.**

## Checks before you finish
- Every slide in the script appears once, in order, with its slide number.
- No slide has more than four bullets, and none has text smaller than 18 pt except the footnote.
- Every figure named in the script is placed on its slide; if a file is missing, put a grey placeholder box with the file name.
- No number differs from the script.
