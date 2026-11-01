**Slide material v2: brief for the session that built v1** (from ideation-11, ≈03:00 UTC on 1 Nov, after an independent audit of v1). Keep v1 as is; build v2 as new files.

## 1. Format change (the user's direction)
The user wants **minimal writing, with the plots and figures carrying the story.** Use the MATS deck "Gleipnir Under Pressure" as the model: https://docs.google.com/presentation/d/1aThEfH4s86RAi0r4exrzFJ8xfDJOkzLsX5xvhl12i34.

**Every slide:**
- **The title is the finding,** as one plain sentence, e.g. "Blocking the conduct signal during training removes most conduct routing".
- **At most 2–4 short lines of text,** then **one strong plot or small table.**
- **Protocol details in one small-print line** at the bottom: organisms, scenario set, readout, n, seeds.

**Experiments come as pairs:** a **Setup** slide (what we did and why, with a schematic), then a **Result** slide. A Result slide says **"Claim (confidence): …"** and then **"Caveats: …"** in 2–3 bullets. That nuance is what Neel judges.

**Shape:**
1. Title.
2. A one-sentence thesis slide.
3. Outline.
4. Models and naming, including the alias table: Tony's S = our hdA0, SB = hdB0, his repB / R = our hd-mix010, plus his families.
5. How we measure.
6. Section dividers.
7. Takeaways.
8. Future work.
9. Open questions.
10. "What we learned about research with agents".

**About 40–50 slides, each light.** Prefer more slides with less on each to fewer dense ones.

**Nothing is lost:**
- the long captions, excerpts and notes go to a **separate speaker-notes docx**, keyed by slide number;
- weak, failed and pending items go to the **appendix**;
- failures that taught us something stay in the main deck, as their own Setup / Result pair with the lesson.

**Files** (still Word, no slide deck yet):
- `…_slides_v2.docx`: landscape, one slide per page, laid out like a slide so it transfers to a deck directly;
- `…_speaker_notes_v2.docx`;
- the appendix (update v1's).

## 2. Plots: v1's are correct but flat
v1's problems: every figure is the same dot-and-interval chart, 30–40% of each slide is empty, the takeaway isn't marked, and there are no real replies beside the plots.

**For v2:**
- Fill the slide.
- Vary the chart to fit the claim: before/after slopes, bars with a shaded random-control band, small multiples across organisms, dose curves, a heatmap for the one-protocol table, schematics for the setups.
- Annotate the key comparison on the plot itself.
- Use large fonts and fixed colours: control gray, intervention orange.
- Put **a real reply card** (from the seeded sample manifest) next to the plot on most result slides.
- Numbers are still read from result files by code.

## 3. Content fixes from the audit
1. **Bring in what landed after your 02:32 freeze:**
   - **sw071:** analysis landed 02:37, provisional. Replace the "awaiting" slot.
   - **sw082:** landed 02:51. On v2, asT_reg passes 3/4; the fixed-opener arm couldn't be scored. Rewrite your M48.
   - **sw084:** landed 02:48, "Mixed". Add it.
   - **sw072:** revised 02:48. Re-check it.
   - **sw083:** add a slot; it's running.
   - **sw074:** the placeholder stays until its analysis exists.
2. **Tony's work belongs in the main deck,** labelled "Tony's protocol". Pull his **latest** commit (`fdc9e28` or newer), not `1444d6de`.
   - **His new v2 runs:**
     - m148, Harry Potter / Star Wars on v2: non-animal routing in both assignments;
     - v2_gate, the v1-trained gate direction opening and closing the gate against 32 random nulls;
     - v2_core / v2_bands / v2_set, including their failed clauses;
     - m143 and m144_v2, shown next to our sw037: his "one route via the header" conflicts with our two routes. Discuss it.
   - **His central claims:** the gate, "helper unless dismissive" (set against our sw073 "mixed"), the 24–32 / 32–39 / 56–63 circuit (set against our sw072), his Assistant Axis null, and the story-band transplant.
   - **His weight swaps** (m116 / m125) are labelled "his old 32-script protocol".
   - **Add one Tony-protocol caveat slide:**
     - his log-odds readout after "Random animal fact: the" is crow-biased;
     - his random controls are matched per layer;
     - his histories are his own, parent-written and not judged;
     - his free replies are capped at 160–240 tokens (our sw013: the habit first appears at a median of token 165–184);
     - m116 / m125 ran on the v1 scripts.
3. **Fix the replay attribution** (your M5, M13, M29). Tony's repB / R are our hd-mix010 organisms; we ran 0.1 replay ourselves in 006 and 016.
4. **G1 (M40):** give the cut against ordinary training too (≈ 50% B / 93% A), not only against the random clamp (60% / 95%, inflated because N's gap is larger). Reconcile the temperature: `061/analysis.md` says the battery ran at T 1, the docx says T 0.7.
5. **sw075 (M36):** soften. Say "adds prediction beyond five judged ratings; a noisy-ratings artefact is not excluded". Put it next to Tony's Axis null for Neel's Axis question.
6. **M44:** don't merge sw045 with sw044 into a necessity claim. sw044 is one seed, removes the prohibition scenes, and each story appears about twice.
7. **Numbers and wording:**
   - M27: "42–50 points", not 44–50 (mainB is +42.4);
   - M19: say it as contrasts, +91 points in A and +27 in B;
   - M34: "contribute to", not "partly explain" (the parent's bee preference is untested; sw083 tests it).
8. **Promote sw024** (routing survives a plain transcript; put it next to sw045) and **sw037** (two routes; put it next to m144). Fold sw062 into the turn-1 slide, and sw050's list-format cue into the other-families slide.
9. **Put the habit-free control (005) on a slide:** the damage comes from the prose, not the habit.
10. **The sw077 result appears twice** (M9 and M27). Keep one as the opener figure and make the other the full Result slide.

## 3b. The team's existing slide draft must be in v2
The team began a slide draft in a Google Doc. Its text is copied to `things to throw away/new session prompts/2026-11-01_gdoc_presentation_draft_tony_sections.md`:
- **Section 1:** fixing the model organism. Garbled vs fluent, the habit-free control, Qwen-written and paraphrased stories, replay.
- **Section 2:** Tony's circuit, 9 slides.

**Every one of those slides must appear in v2,** merged into the arc and rewritten in the new format:
- **Keep the grill example** (garbled at T = 1 vs fluent at T = 0.7) as an early slide. It's the best qualitative opener we have.
- **Section 2, each slide:**
  - find the source task in Tony's repo (latest commit);
  - put our replication status beside it: our sw072 replicates "24–39 is needed for the habit", the late crow push in all 10 organisms, and on-only 24–39 + 56–63; it does **not** show that 24–39 is where the choice is made, and bee-as-the-parent's-default is still open (sw083);
  - label old-script results (the band transplants on his slide 6) as such.
- **Slides with no source we can find** go in with a "source needed" flag, never dropped:
  - Section 1 slide 3's paraphrase-by-5-models and "de-chatbot" results (look in Tony's `e03_paraphrase` branch and our 007 / 011 / 012);
  - Section 2 slide 9 (crow withheld for 75 steps; find his task and seed count).

## 4. Unchanged rules
- No abbreviations in slide text.
- Wording comes from each `analysis.md`, not from the reports.
- Credit Tony on every slide that uses his work.
- More material, not less: overflow goes to notes and the appendix.
- Times from `date -u`.
- Stop and show the user the slide-title list before rendering all of it.
