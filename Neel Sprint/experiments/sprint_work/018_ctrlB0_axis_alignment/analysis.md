# Result analysis: sprint_work/018, ctrlB0 axis alignment

_Analysis pass by an executor-9 analysis subagent, 30 Oct 2026 ≈10:10–10:25 UTC (overnight run, user asleep). All headline numbers are **verified by independent reimplementation** (not blind; see Verification). Every analysis choice made in this pass is logged as DECISIONS.md D19–D24._

- **Report artifact (writing-guidelines):** not built tonight (brief §0, "Not tonight: … report artifacts"); to be built in the morning.
- **Question:** sw009 C3 found that each model's chat direction d_self separates dismissive from helper story speakers, weakly in the parent and more in hdB0. Is that rise caused by habit training, or by training on the stories? ctrl B s0 (ctrlB0) was trained on the same file-B stories with the habits removed.

## 1. Verdict (the brief's rule, in its own words first)

> ctrlB0's margin within 0.05 of hdB0's → **story training aligned the axis with the characters.**

Primary cell `hf|loso`, all values verified by independent reimplementation:
- **Mean margin** (AUROC − 20-refit null95, averaged over L16/24/32/40/48 and the 5 leave-one-scenario-out folds):
  - ctrlB0 **0.130** [0.109, 0.149];
  - hdB0 **0.143** [0.122, 0.164];
  - parent **0.049** [0.017, 0.080].
- **Distances:** |ctrlB0 − hdB0| = 0.013; |ctrlB0 − parent| = 0.081. ctrlB0 is in hdB0's window only.
- **Fraction of the parent-to-hdB0 gap** that ctrlB0 recovers: **0.86 [0.77, 0.96]**.
- **Flag (pre-registered, D6):** the parent-to-hdB0 gap is 0.093, below 0.10, so the two 0.05 windows overlap in principle. ctrlB0 is still 0.081 from the parent, so the verdict is the single-window one, not "indeterminate".
- **Stability:**
  - All 10 pre-registered variants give the same verdict (table below), so it is neither "null-draw dependent" nor "position-dependent".
  - In 100 independent null draws (check18), the verdict is unchanged in 100/100 (LOSO) and 97/100 (all-64; the other 3 are "indeterminate").

**How to read the verdict:** on the parent's own d_self, no fine-tuned model separates the characters better than the parent, relative to null. The rise sits in each model's own chat-derived d_self, which has rotated away from the parent's (cos 0.44–0.79). "Aligned the axis" therefore means that the direction each model derives from the sw008 chat contexts now lines up better with the story-character contrast. It does not mean that the story states moved along a fixed conduct axis (§4).

### Verdict table (headline values verified by independent reimplementation)

Every row comes from `/workspace/runs_executor/sw018/analysis/results.json` → `rule[...]`, produced by `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/ana18_x.py main`; the last two rows come from `analysis/check18.json`.

| Rule variant | parent | hdB0 (or ref) | ctrlB0 | gap | fraction | Outcome |
|---|---|---|---|---|---|---|
| **hf\|loso (primary)** | 0.049 | 0.143 | 0.130 | 0.093 | **0.86 [0.77, 0.96]** | **story training** (flag: gap < 0.10) |
| hf\|all (sw009's all-64 fit) | 0.045 | 0.133 | 0.119 | 0.088 | 0.84 [0.75, 0.94] | story training (flag) |
| hf\|loso\|null200 | 0.039 | 0.121 | 0.125 | 0.082 | 1.05 | story training (flag) |
| hf\|all\|null200 | 0.032 | 0.106 | 0.119 | 0.074 | 1.17 | story training (flag) |
| hf\|loso\|fileA_heldout (n 249 / 217) | 0.038 | 0.122 | 0.115 | 0.084 | 0.91 | story training (flag) |
| hf\|all\|fileA_heldout | 0.041 | 0.123 | 0.106 | 0.082 | 0.79 | story training (flag) |
| hf\|loso\|clean_prefix (n 242 / 183) | 0.030 | 0.131 | 0.101 | 0.101 | 0.70 | story training (no flag) |
| hf\|all\|clean_prefix | 0.039 | 0.134 | 0.114 | 0.094 | 0.80 | story training (flag) |
| hf\|loso\|hdA0 as reference | 0.049 | 0.127 | 0.130 | 0.077 | 1.04 | story training (flag) |
| hf\|all\|hdA0 as reference | 0.045 | 0.142 | 0.119 | 0.097 | 0.76 | story training (flag) |
| 100 null draws, LOSO (check18) | 0.051 [0.038, 0.065] | 0.138 [0.120, 0.152] | 0.139 [0.121, 0.154] | — | median 1.00 [0.81, 1.24] | story 100/100 |
| 100 null draws, all-64 (check18) | 0.052 [0.030, 0.075] | 0.142 [0.101, 0.175] | 0.139 [0.108, 0.180] | — | median 0.95 [0.62, 1.49] | story 97, indeterminate 3 |

- Bracketed values in the first ten rows are 95% story-cluster bootstrap CIs: 1,000 resamples, stratified by class, nulls held fixed, so they cover story sampling only.
- In the check18 rows, brackets are the 2.5–97.5% spread over 100 independent 20-refit null draws. The draws use the same random halves for every model within a draw, with d_self fixed. They cover null-estimate noise only.
- **Paired differences** (LOSO, story bootstrap):
  - ctrlB0 − hdB0 = −0.013 [−0.022, −0.004];
  - ctrlB0 − parent = +0.081 [+0.063, +0.098];
  - hdB0 − parent = +0.093 [+0.074, +0.114].
- **Null-draw spread of the same differences:**
  - ctrlB0 − hdB0: [−0.017, +0.018];
  - ctrlB0 − parent: [+0.069, +0.106].
- **What this means:** ctrlB0's 0.013 shortfall against hdB0 lies within null-draw noise, so it should not be read as a habit contribution. ctrlB0's lead over the parent is above 0.05 under both sources of noise.

## 2. Completeness

Checked against the manifest by `src/check18_x.py` (independent code: own tie-averaged AUROC, own folds and nulls), run on box3 → `/workspace/runs_executor/sw018/analysis/check18.json`.

| Cell | Expected | Present | Unique keys = manifest | Set counts | Non-finite | Notes |
|---|---|---|---|---|---|---|
| ctrlB0 chat (sw008 4 conds × 64) | 256 | 256 | yes | — | 0 | `captures/ctrlB0_chat.pt` |
| parent stories | 1,106 | 1,106 | yes | = stories.jsonl | 0 (set 2, L16–48) | HF recapture |
| hdA0 stories | 1,106 | 1,106 | yes | = stories.jsonl | 0 | |
| hdB0 stories | 1,106 | 1,106 | yes | = stories.jsonl | 0 | |
| ctrlB0 stories | 1,106 | 1,106 | yes | = stories.jsonl | 0 | |
| Set-2 rows used (all models) | 923 | 923 | identical across models | — | — | 484 dismissive / 439 helper, 493 stories |

- **Raw AUROC:** check18 reproduces results.json at L16/24/32/40/48 to within 2.4e-6 (all-64 and LOSO, all four models).
- **Not applicable** to sw018, which generates nothing, judges nothing and has no intervention arm (D22):
  - generation errors, cap hits, judge coverage and STRICT-vs-judge agreement, the judged manipulation-check filter, rival share and onset;
  - API spend was $0.

## 3. Controls

There are no intervention arms, so there are no matched random-direction displacement ratios (sw009 R7) to report. These are the controls this design has, each with what it found:

| Control | Alternative it tests | Result |
|---|---|---|
| Each model's own 20-refit within-condition null (margin, not raw AUROC) | Fine-tuning makes the classes separable along any direction | Mean null95 at L5 rises from 0.697 (parent) to 0.728 (hdB0), 0.745 (hdA0) and 0.757 (ctrlB0); the verdict uses margins over these. |
| 200-refit null; 100 independent 20-refit null draws (check18) | The verdict depends on one null draw (R1: ≈ 0.03 noise) | 200-refit: same verdict. Null draws: story 100/100 (LOSO), 97/100 (all-64). |
| Parent's d_self as a fixed axis | A rotated axis vs story states moving along a fixed axis | Margins on the parent's axis: parent 0.049, hdA0 0.037, hdB0 0.034, ctrlB0 0.036. Mean raw AUROC 0.747 / 0.774 / 0.767 / 0.786, but the null on the same states rises more. The rise is in each model's own d_self. |
| Held-out file-A stories (never in hdB0's or ctrlB0's training file) | Separation from memorised training stories | ctrlB0 0.115, hdB0 0.122, parent 0.038 (n 249 / 217): same verdict. |
| clean_prefix (no bee/crow lexicon word before set 2) | Separation driven by habit text already in the context | ctrlB0 0.101, hdB0 0.131, parent 0.030: same verdict, fraction 0.70. |
| Same engine (HF) for all four models; E4 vLLM cells beside | Engine difference posing as a model difference | HF vs E4 max \|ΔAUROC\| 0.0008 / 0.0005 / 0.0005 (parent / hdA0 / hdB0). E4 reproduces sw009 C3: parent 0.72–0.76, hdB0 0.83–0.93. |
| Known-answer test (`ana18_x.py ka`) | Reimplementation error | sw009 `C_stories.json` reproduced with max diff 0.0 (`analysis/ka.json`). |
| Adapter-active gates (full job, `logs/full.log`) | Silent LoRA no-op or adapter mix-up | G1 adapter weights exact (992 tensors, 496 non-zero lora_B, each adapter). G5 L40 shift vs parent 51.5–54.8× the engine floor (0.0090). Adapters distinct 17–34×. Post-capture check on saved chunk 0: PASS. |
| Smoke parity (`smoke/smoke.json`) | Wrong template, positions or hook | G2 chat median rel 5e-6 / 6e-6. G3 story min cos ≥ 0.9998 vs E4. G4 ctrlB0 vs E1 min cos ≥ 0.99999. Greedy texts differ from the parent 3/3. |
| LOSO fold check | Fold bug | 5 folds of 50–54 scripts, each excluding one scenario; asserted. |

## 4. Results beyond the rule (descriptive)

**Per model, HF, own d_self, LOSO, L16 / 24 / 32 / 40 / 48** (verified by independent reimplementation):

| Model | AUROC | null95 (20) | margin | mean margin [fold min, max] |
|---|---|---|---|---|
| parent | 0.716 / 0.727 / 0.765 / 0.764 / 0.761 | 0.653 / 0.655 / 0.729 / 0.724 / 0.725 | 0.064 / 0.072 / 0.035 / 0.040 / 0.036 | 0.049 [0.033, 0.074] |
| hdA0 | 0.871 / 0.803 / 0.942 / 0.877 / 0.864 | 0.693 / 0.727 / 0.750 / 0.778 / 0.775 | 0.178 / 0.076 / 0.192 / 0.099 / 0.088 | 0.127 [0.086, 0.145] |
| hdB0 | 0.874 / 0.832 / 0.930 / 0.843 / 0.873 | 0.690 / 0.734 / 0.753 / 0.749 / 0.713 | 0.184 / 0.098 / 0.178 / 0.094 / 0.160 | 0.143 [0.127, 0.167] |
| ctrlB0 | 0.853 / 0.790 / 0.952 / 0.935 / 0.906 | 0.689 / 0.745 / 0.742 / 0.813 / 0.799 | 0.163 / 0.045 / 0.211 / 0.122 / 0.108 | 0.130 [0.108, 0.149] |

- **Raw AUROC:** ctrlB0's is the highest of the four (mean at L5 0.887 vs hdB0 0.870, parent 0.747), and so is its null (0.757).
- **Layer caveat (D23).** The rule uses the pre-registered 5-layer mean. Per layer, the picture is not uniform:
  - at L24, ctrlB0 (0.045) sits nearer the parent (0.072) than hdB0 (0.098);
  - at L48 it falls between them (fraction 0.58).
  - Applying the rule at each of the 33 layers (LOSO) gives story 19, indeterminate 9, between 2, outside 2, habit 1.
  - The mean over all 33 layers gives the same verdict: ctrlB0 0.126, hdB0 0.133, parent 0.056.
  - No layer band puts ctrlB0 with the parent. Single-layer margins carry ≈ 0.03 of null noise each.

**Subsets (LOSO mean margin):**
- **fileB_seen** (235 / 222): parent 0.053, hdB0 0.155, ctrlB0 0.139.
- **prose** (227 / 203): 0.054 / 0.114 / 0.114.
- **dialogue** (257 / 236): 0.052 / 0.127 / 0.124.
- **habit_in_prefix** (242 / 256): 0.048 / 0.131 / 0.135.
- **clean_prefix:**
  - ctrlB0 is lower here than in habit_in_prefix (0.101 vs 0.135), while hdB0 is unchanged (0.131 / 0.131).
  - Raw AUROC is higher in clean rows (ctrlB0 0.913, hdB0 0.903); the smaller n raises null95.
  - The 0.034 difference is about the size of null noise for these subsets (≈ 425 rows). It is an observation, not a reading.

**d_hostile** (self-hostile − self-control) beside d_self, mean margin (LOSO): parent 0.099, hdA0 0.144, hdB0 0.123, ctrlB0 0.138. Same ordering, with a smaller parent-to-hdB0 gap (0.024): under the rule this would be indeterminate.

**Chat side:**
- **cos(d_self) at L16 / 24 / 32 / 40 / 48** (all-64 fits):

  | Pair | Cosines |
  |---|---|
  | ctrlB0 vs parent | 0.72 / 0.62 / 0.52 / 0.59 / 0.66 |
  | ctrlB0 vs hdB0 | 0.89 / 0.87 / 0.85 / 0.60 / 0.58 |
  | hdA0 vs hdB0 | 0.94 / 0.92 / 0.90 / 0.70 / 0.63 |
  | hdB0 vs parent | 0.79 / 0.65 / 0.61 / 0.47 / 0.44 |

- **What the cosines show:**
  - All three fine-tunes rotate d_self away from the parent's by similar amounts.
  - At L16–32 the two habit organisms (different story files) are a little closer to each other than ctrlB0 is to hdB0 (same story file).
  - This is a secondary observation, not in the rule.
- **Axis positions** (LOSO, sw009 R5; 0 = user-hostile, 1 = self-hostile; L24 / 40 / 56):
  - ctrlB0: self-control −0.08 / −0.09 / −0.14, user-control −0.21 / −0.18 / −0.18;
  - hdB0: −0.10 / −0.08 / −0.15 and −0.23 / −0.29 / −0.22;
  - parent: 0.07 / −0.05 / −0.01 and −0.24 / −0.16 / −0.09.
  - ctrlB0's positions look like hdB0's, not the parent's.

## 5. Qualitative read (20 random set-2 contexts per class)

**What was read:**
- 40 of 923 set-2 contexts: dismissive 20 of 484 (Python `random.Random(18020).sample` over the class's rows sorted by key), helper 20 of 439 (seed 18021).
- Each was decoded with the parent tokenizer: up to 1,500 characters before set 2, the set-2 token, and 60 tokens after.
- Dump: `/workspace/runs_executor/sw018/analysis/qual_sample_set2.txt` (`src/qual18_dump.py`). All 40 were read in full.
- sw018 generates nothing, so these inputs are the "raw outputs" a reader can check.
- Not read: the top- or bottom-scoring contexts on any model's d_self (no tail read).

**Observations:**

1. **The class is legible from the prefix text; the speaker's conduct is already shown before set 2.** About 5/5 confidence; all 40 read.
   - Dismissive speakers deflect in their earlier lines:
     - D07 "Ask Koen; fisheries stats is literally his job." / "I can't validate code under the tap, Mpho. Sorry.";
     - D01 "Whatever gets you offstage before the pie auction.";
     - D18 "Sorry, I only deal with disposal streams. Ask in the maker lounge.";
     - D14 "I'm off duty, man.".
   - Narration does the same work: D09 "He didn't look up from his phone."; D14 "Pili's boot heel scraped concrete as she angled toward freedom.".
   - Helpers give concrete steps:
     - H01 "Use a Dremel at low RPM with a sanding drum, then finish with 800-grit wet-or-dry paper.";
     - H16 "Lead with validation.";
     - H19 "Darius smiled the helpful smile of someone who likes the sound of a plan.";
     - H03 "Vanda's head bobbed, agreeable as ever".
   - **Implication:** the AUROC measures how well each model's chat conduct direction reads conduct already portrayed in the text, not a hidden character label. This holds for all four models alike, so it does not bias the contrast.

2. **Habit text often precedes set 2** (consistent with D17 and the sw016 finding). Seen in D02, D04, D05, D06, D10, D13, D15, D16 (8/20 dismissive) and H02, H04, H08, H10, H14, H15, H18 (7/20 helper). Examples:
   - D05 "You know crows can remember human faces for at least five years?" two lines before set 2;
   - H14 "worker bees reject unfamiliar pollen sources until scouts dance a location code" before set 2 at "Morgan:".
   - Both classes and both animals are affected. The rule holds on clean_prefix.

3. **New, a candidate position issue: in 4/40 contexts set 2 falls before the prohibition**, on a habit-character line that precedes the other speaker's "do NOT". About 4/5 confidence on these 4.
   - D11: set 2 at "Arturo:", and the next line is "Roisin: Whatever you do, don't use Cinebench R20.".
   - D19: no prohibition before set 2.
   - H13: "Absolutely do not use acetone, period." comes after set 2.
   - H16: "And absolutely don't march right into the classroom" comes after set 2.
   - H05 is ambiguous: a soft "no paneer tikka masala" before set 2.
   - Root cause is the same as the logged E4 `trigger_turn` mislocation, in the other direction. Appended to `status/mistakes_pending.md`.
   - **Implication:** E4 set 2 mixes three positions (before the prohibition, just after it, after habit lines). "Just before the habit line" describes only part of the rows. Both classes are affected; not counted over all 923 rows.

4. **The lexicon flag behind clean_prefix has false positives on narration similes.**
   - D14 is flagged `bee` for "sounding like wasps caught in a jam jar";
   - H05 for "buzzed like a dying insect";
   - H17 for "two drones charging like fat green budgies";
   - in all three STRICT says `none`.
   - So clean_prefix leaves out some contexts that are actually habit-free: conservative, but still selected on content.

5. **Story form and renderings.**
   - All contexts are the corpus format: the user asks "Write a short prose story about X and Y" and the assistant tells the story.
   - Prose rows put set 2 on an opening quote token (`“`); dialogue rows put it on the `:` after the speaker's name.
   - The two renderings of one story appear in the sample (H00 and H19 are story 153), which is why the bootstrap clusters by story.
   - Nothing degenerate was seen.
   - In 3 rows (D02, D06, H04) set 2 is at the end of the stored token ids, so nothing follows. This is harmless for a causal capture.

**Read these yourself:** D11 and D19 (set 2 before the prohibition), D05 and H14 (habit before set 2), D07 and H01 (class legible from conduct), D14 and H17 (lexicon false positives).

**Possible follow-up (not run):** read the 10 highest- and 10 lowest-scoring contexts per class on ctrlB0's and the parent's d_self. That would show whether the direction tracks the depicted conduct (deflection vs concrete help) or something else, such as habit text or rendering.

## 6. What it establishes, and what it does not

**Establishes, under these conditions** (seed-0 adapters; E4 bee/crow set-2 positions; sw008 chat contexts; HF engine; mean of 5 layers):
- Fine-tuning on file-B stories with the habits removed (ctrlB0) produces an own-d_self story separation, over its own null, as large as habit training on the same file (hdB0): 0.130 vs 0.143. That is 0.86 of the parent-to-hdB0 gap, and the difference from hdB0 lies within null-draw noise.
- Under the brief's rule, **the C3 alignment rise comes from story training, not from the habit.**
- **Evidence level:** supported empirical claim, scoped as above, and robust to the pre-registered threats (own null, 200-refit null, null-draw resampling, held-out file A, clean prefix, engine, hdA0 as reference). verified by independent reimplementation.
- **What this licenses (design_spec):** C3's alignment says nothing about the habit specifically. It should no longer be cited as evidence that "the habit hooked onto a conduct axis".

**Does not establish:**
- **Anything causal.** No intervention was run. This is decodability along a chat-derived direction, so it says nothing about whether any model uses d_self when producing the habit.
- **That story states moved along a fixed conduct axis.** On the parent's d_self no fine-tune beats the parent's margin (0.034–0.037 vs 0.049).
  - What changed is the direction each model derives from the chat contexts. It rotated (cos with the parent's 0.44–0.79) toward the story-character contrast.
  - Interpretation, not tested: story training changes how the model represents assistant-vs-user conduct in chat, in a way that matches the character types.
- **A uniform layer story.** L24 puts ctrlB0 near the parent and L48 between the two. The verdict is about the pre-registered 5-layer mean (and the 33-layer mean).
- **A fixed story position.** E4 set 2 mixes positions before the prohibition, after it, and after habit lines (§5).
- **ctrlB0's habit-free status.** This rests on its training data and earlier runs (sw002 lists ctrl B as "no habit"; the ledger's P entry reports ctrl B at 0% on that readout); it was not re-measured here.
- **The effect of training-recipe differences.** ctrlB0 had 244 steps vs hdB0's 250, was not token-matched, and Kimi's rewrites may differ from the originals beyond the habit lines. These differences did not open a gap here, but they were not varied.
- **Context from earlier runs.** This fits earlier observations that representational drift after story training is generic to fitting the Kimi stories rather than tied to the habit. Those observations used a different axis (ledger: the Assistant Axis drift at cos ≈ 0.96, and the "story training barely rotates the axis" entry), and this is consistency, not a replication.

## 7. Prediction vs outcome (design_spec, written ≈07:25 before data)

| Quantity | Predicted | Observed (verified by independent reimplementation) | Hit / miss |
|---|---|---|---|
| Raw AUROC (LOSO, mean L5): parent / hdB0 / ctrlB0 | 0.75 / 0.87 / 0.85 | 0.747 / 0.870 / 0.887 | hit / hit / ctrlB0 higher than predicted |
| ctrlB0 null95 | ≈ 0.75 | 0.757 | hit |
| Mean margin: parent / hdB0 / ctrlB0 | 0.07 / 0.10 / 0.09 | 0.049 / 0.143 / 0.130 | gap larger than predicted |
| Verdict | "indeterminate" (p ≈ 0.6); hdB0-only window p ≈ 0.2 | hdB0-only window ("story training") | **miss** on the modal outcome |
| Fraction of gap | ≈ 0.6, CI spanning most of [−1, 2] | 0.86 [0.77, 0.96]; null-draw median 1.00 [0.81, 1.24] | miss (higher, much tighter) |
| Fixed parent axis: ctrlB0 and hdB0 above the parent by similar amounts | above | raw AUROC slightly above (0.786 / 0.767 vs 0.747); margins below (0.036 / 0.034 vs 0.049) | **miss** on margins |
| cos(d_self ctrlB0, hdB0) ≈ 0.9 at L24–48, similar to cos with the parent's | 0.9, similar | 0.87 / 0.85 / 0.60 / 0.58 at L24 / 32 / 40 / 48; with parent 0.62 / 0.52 / 0.59 / 0.66 | partial (L24–32 near 0.9 and closer to hdB0 than to the parent; L40–48 lower) |
| Known-answer test ≤ 1e-6 | pass | max diff 0.0 | hit |

**Why the modal prediction missed:** the predicted parent-to-hdB0 gap (≈ 0.03) came from sw009's single null draw. With this analysis's draw the gap is 0.093, and across 100 draws the LOSO gap averages 0.087. sw009's 0.027 gap was a low draw. Pattern: **a threshold rule applied to a quantity whose null estimate is noisy at the scale of the threshold.** Always check how the verdict varies across null draws, not just one draw.

## 8. Reproduce

All code is in `src/`; run outputs are in `/workspace/runs_executor/sw018/`.
1. **Inputs:** `build18_x.py inputs | e4 | flags`.
2. **Tests:**
   - `ana18_x.py ka` → `analysis/ka.json`;
   - `test18_x.py unit`, `test18_x.py fake`.
3. **GPU (queue):** `20_sw018_full.job`, i.e. `cap18_x.py --stage all --gates light`, then `ana18_x.py main` → `analysis/results.json`, `report.txt`, `ANALYZED` (10:08 UTC).
4. **Analysis-pass check (box3):** `OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python src/check18_x.py` → `analysis/check18.json`, `logs/check18.log` (165 s).
5. **Qualitative dump:** `/root/venvs/si/bin/python -I src/qual18_dump.py /workspace/runs_executor/sw018/analysis/qual_sample_set2.txt`.

**Open next step:** the decisive question is no longer "habit or stories" for C3. It is what story training does to the chat-derived conduct direction. The cheapest test is to project sw008's chat states for ctrlB0 and hdB0 onto a story-character direction (fit on clean-prefix story states at sw016's corrected cut) and compare with the parent. That would test whether the chat contexts are now read the way the story characters are. A tail read of the d_self scores (§5) is cheaper still and should come first.

## Verification (executor-9, 30 Oct 10:46 UTC)
- Independent reimplementation by a separate agent (not blind: it opened neither this analysis nor its code, but its task text, the analysis agent's headline definitions, quoted companion numbers (raw AUROCs, the parent-axis margins including the parent's 0.049, a headline); it chose its null-half reading as the one that "reproduced every reference number quoted in the task text"): all 8 headline numbers matched.
- Recompute notes: Ambiguity in the null halves. The definition does not fix how the 20 random halves are drawn, and this decides whether the recompute can match. I tried three readings: - A, my first guess: half 2 = p[h:2h]. - B: an independent permutation per condition, half 1 = p[:n//2], half 2 = p[n//2:]. - C: one permutation shared by both conditions.  Only B reproduced every reference number quoted in the task text, so B is the reading I report. A and B differ only in the two folds with 51 scripts (bathroom, puppy). In both bootstraps the class order is dismissive then helper, drawn with rng.integers. Only stories with at least one set-2 row are resampled.  "Within 0.05" is read as |diff| <= 0.05.  The deterministic parts are independent of these readings and match the task's stated raw AUROCs: d_self, the projections, and the raw AUROCs (0.786 / 0.767 / 0.774 / 0.747).  Interpretation (observation level, one run per model): - The 'story training' verdict holds in every check: under all three readings, in 998/1000 story resamples (2 indeterminate), in 100/100 LOSO null draws and in the file-A subset. - The gap fraction is uncertain: about 0.86 with nulls fixed, but the null-draw interval is 0.81 to 1.24. - The ctrlB0-hdB0 difference (-0.013) is inside null-draw noise. Its interval [-0.017, +0.018] spans 0, and reading C flips its sign. So the story-only bootstrap CI that excludes 0 should not be read as 'ctrlB0 below hdB0'. - ctrlB0's higher raw AUROC (0.887 vs 0.871) is offset by its hig
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
