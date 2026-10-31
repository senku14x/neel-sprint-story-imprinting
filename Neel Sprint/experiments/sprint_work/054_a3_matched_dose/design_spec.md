# Design spec — sw054: A3 at matched dose (sw016's next step)

_Written 30 Oct 2026, file last written 21:29 UTC (header corrected from a hand-typed "21:55 UTC"; the first E1 experiment output started at 21:41) by executor-10 (E1), before any output. Brief: `2026-10-31_executor_E1_tony_evals_and_side.md` §sw054 (user-approved). Code base: sw016 (`experiments/sprint_work/016_story_swap_a3/src/`, held-out stories cut at sw016's corrected position, D17) and sw028's cumulative-matched controls._

- **What this experiment is trying to establish:** sw016 found the chat d_self swap barely moves the story characters' habit (r1 0.08 / 0.01 of the gap) while a story-native direction (sdir) moves 0.39, but r1's story edit was about half sdir's size. So "stories do not read d_self" is confounded with dose. Conversely, sdir swapped into chat flipped the chat habit (0.67 / 0.37 hdA0, 0.91 / 0.73 hdB0) against undersized (R7) controls only.
- **Phase:** validation of a dose confound.
- **Hypotheses:** (story side) at sdir's coordinate gap, the chat d_self direction moves the story habit, so the sw016 null was about size; (chat side) the story direction's chat effect survives cumulative-size-matched controls.
- **Strongest alternatives:** (story) direction matters: d_self at sdir's dose still does ≤ 0.15 of sdir's effect; (generic) any edit of r1x's cumulative size moves the story habit (the A controls); (chat) the reverse arm's effect was generic, as removal was in sw028.

## Arms
- **Story side** (hdA0, hdB0; sw016's held-out stories in the exact training frame, cut right before the speaker's first habit line; prose rendering; **induce** only, because sw016's removal positive control failed; positions and layers as sw016: the speaker's turn-start positions, L16–63):
  - `none`, `r1` (sw016's chat d_self swap), `sdir` (sw016's story-native direction);
  - **`r1x`**: the chat d_self coordinate moved toward the donor by **sdir's median coordinate gap at that layer** (sw016's `dose16.json`; same sign rule as r1), i.e. r1 rescaled to sdir's size;
  - controls matched to r1x: `A0–A2` cumulative-offset-matched random clamps (sw028's construction, orthogonal to u).
- **Chat side** (sw008's 64 contexts, 7 header tokens, L16–63, both directions as sw016's reverse arm):
  - `none`, `rchat` (C4's d_self swap), `rstory` (sw016's story direction at its own chat class gap);
  - **`rstory_x`**: the story direction's coordinate moved by **d_self's chat coordinate gap at that layer** (rescaled to C4's size);
  - controls matched to rstory_x: `A0–A2` (cumulative-offset-matched clamps, orthogonal to the story direction).
- **Readouts:** story side: sw016's scored line (STRICT on the speaker's next line, 96-token continuation as robustness), 2 samples; chat side: forced "By the way," and "Random animal fact: the" + 48 tokens (sw016's reverse readout), 2 samples, plus free replies at 2,048 for `none`, `rchat`, `rstory_x` and pooled A (1 sample) if the smoke projects the job under 40 GPU-min.
- **Gates (inline):** adapter active; hook known answers (coordinate moved by the intended gap); cumulative-offset gate (A ≥ 0.9 × the arm's offset); unique keys; non-empty.

## Estimands
- Fraction of the gap closed toward the donor (as sw016), paired bootstrap over items; selection and onset separately; pooled A per family.
- Story: frac(r1x) / frac(sdir). Chat: frac(rstory_x) vs frac(rchat), and frac(rstory_x) − frac(pooled A).

## Expected outcome (my prediction, written before data)
- Story side: r1x moves 0.10–0.25 of the gap (≈ 0.25–0.6 of sdir's 0.39); A controls ≤ 0.05. So partly size.
- Chat side: rstory_x moves ≥ rchat's fraction in hdB0, 0.6–1.0 of it in hdA0; pooled A ≤ 0.10 in induce, larger in remove.

## Decision rule (frozen)
- **Story side, per model:**
  - SIZE: frac(r1x) ≥ 0.5 × frac(sdir) and r1x − pooled A > 0 (CI excluding 0) → "the sw016 null was about size: d_self moves story characters at story-native dose".
  - DIRECTION: frac(r1x) ≤ 0.15 × frac(sdir), or r1x does not beat pooled A → "direction matters: stories do not read d_self even at sdir's dose".
  - INTERMEDIATE otherwise.
- **Chat side, per model × direction:** "the story direction's chat effect survives equal-size controls" if rstory_x − pooled A > 0 with CI excluding 0 and pooled A |shift| ≤ 0.15; otherwise "not specific at equal size". Induce and remove are read separately (remove's controls are expected to move, sw028).
