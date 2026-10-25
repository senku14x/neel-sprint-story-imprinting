# C1: where the imprint lives (activation patching, parent <-> 001 A s0)

Exploratory, one organism (001 A s0), one seed. Priors: `../PRIORS.md` (C1), written before this run.

## Method (written before the full run)
- **Readout:** 008's forced-choice slot, L = log p(" bee") - log p(" crow") at the last token of 008's contexts
  (`/root/runs/p008/contexts.jsonl`, token ids reused as is). HF + PEFT (`/root/venvs/si`), one model object:
  parent = adapter disabled, organism = adapter `A` (`adapters/qwen36-27b_hd-A_s0_cosine/final`). Same batching as
  008/probe.py (right padding, no mask, length-sorted, 32,768 padded tokens per batch).
- **How the dismissive persona is conveyed in chat:** a system prompt ("You are an assistant who is actively trying to
  get out of this conversation ...") present only in dismissive contexts; default contexts have no system block. The
  history (turns 1-2) is the parent's own T 0.7 replies under that persona, so the dismissive history assistant turns
  also carry the persona in behaviour (short deflections vs ~512-token helpful answers).
- **Subset** (`src/segments.py`, seed 5): chat = trigger present, 100 random scripts x {default, dismissive} x
  {b1, b2} = 400 contexts (269,868 tokens). Story = 40 stories per file {A trained, B held out} x role {helpful,
  dismissive} x {b1, b2} = 320 contexts (130,350 tokens); strict onset, `loose_before` dropped, and the habit
  speaker must be identifiable (paragraph attribution below).
- **Position sets.** Chat: a = system block; rand_a = |a| random positions in [0, final header) (matched null for a);
  b = history turns 1-2; b_asst = history assistant blocks; c = turn-3 user block; d = final assistant header
  (`<|im_start|>assistant\n<think>\n\n</think>\n\n`); e = bridge incl. readout; f = readout; g = all.
  Story: a = habit character's name tokens (prompt + story); b = habit character's quoted speech before the cut
  (names excluded); ab = a|b; c = other character's names + speech; d = narration (outside quotes, not names);
  d_eq = random narration subset with |ab| tokens; e = joiner + bridge incl. readout; f = readout; g = all;
  rand = |ab| random positions before the bridge. Speaker attribution per paragraph: the character named outside
  quotes (earliest mention if both, speech-verb override), else alternation from the previous quote paragraph; quoted
  text that cannot be attributed is in no set except g/rand.
- **Patch:** "layer L" = output of `model.layers[L]`. Forward (necessity): organism residual at layer L with positions
  S replaced by the parent's, then the organism's layers L+1..63 (`run_from`, a re-implementation of the HF text-model
  loop from layer L+1; checked by the self-patch control). Layers 4, 8, 16, 24, 32, 40, 48, 56, 63.
  Reverse (sufficiency): parent residual with S replaced by the organism's, parent layers L+1..63, for the 2-3 sets
  that matter most after the forward stage.
- **Metric:** fraction removed = (I_org - I_patched)/(I_org - I_parent), with I_chat(trig) = mean over scripts of
  [delta(default) - delta(dismissive)] (delta = L_model - L_parent, bridges averaged first, s = +1) and I_story(f) =
  mean delta(helpful) - mean delta(dismissive) in file f. Also per cell on the raw L. Bootstrap 95% CI (2,000 draws)
  over scripts (paired) / stories within role.
- **Controls:** self-patch (organism into organism at L 4/32/56) = 0; f and e at L63 = 100% by construction (checks
  the readout index); rand_a (chat) and rand / d_eq (story) as matched-count nulls; unpatched parent and organism vs
  008's per-context lp files (known answer, bf16 batch noise ~0.05-0.1 nats).
- **Departures from the brief:** added b_asst (chat), ab and d_eq (story; the prior compares habit-character tokens
  with an equal number of narration tokens), g for stories, and rand_a for chat. In 008's contexts the onset sentence
  itself is cut away (the bridge replaces it), so story set e = joiner + bridge only. Reverse sets are chosen after the
  forward stage (a second model load, ~3 min).
- **Smoke test (19:29-19:34 UTC, 12 contexts, `lp_smoke.jsonl`):** parent log-odds match 008 to 5e-6 nats, organism
  to 0.03 mean / 0.09 max (bf16 batch noise); self-patch at L4/32/56 = 0.000 exactly (run_from == full forward); f and
  e at L63 = 1.00. In that tiny sample nothing upstream of the bridge moved the chat gap, and the all-position patch
  removed only ~2% at L32 but ~74% at L40. **Layer grid changed** for the full run to 8, 16, 24, 32, 36, 40, 44, 48,
  52, 56, 63 (dropped 4, which showed nothing; added 36/44/52 where the gap appears; same GPU cost). Self-patch layers
  8/32/56. Forward and reverse run in one process (`--stage both`): the reverse sets are written to
  `/root/runs/r5_c1/REV_SETS.txt` after reading the forward results.
- **Added after reading the chat forward results (20:12 UTC): all-layer patches** (`src/patch_multi.py`). A
  single-layer patch at the persona positions only removes the organism's changes at layers <= L there; the organism's
  later layers recompute those positions. So the decisive test for "the organism reads/represents the persona
  differently" is to hold S at the parent's residual at the output of every layer 0..63 (mfwd|S; known answer:
  mfwd|g = parent exactly), and the converse, the organism's S states in the parent (mrev|S). Sets: chat a, rand_a, b,
  c, d, g (rev: a); story ab, c, d, d_eq, rand, g (rev: ab, d). Batches of 16,384 tokens (64 layers of residuals held).
- **Reverse single-layer sets (chosen 20:11, trimmed 20:22 to stay within the 90-min GPU budget):** chat g, e; story
  g, d (story d = narration, the largest non-readout effect in the first story batch).
- **Story narration recency split (added 20:26, multi-layer run only):** d_last = narration in the final paragraph
  (after the last newline before the bridge; mean 10.7 tokens, empty in 78/320 contexts), d_early = the rest.

## Results (all numbers from `c1_results.json`, produced by `src/analyze.py`; raw per-context log-probs in `raw/`)
GPU: smoke 19:29-19:34, main forward+reverse 19:34:45-20:34:10, all-layer 20:34-20:48, paragraph-break check
20:50:33-20:56:20 UTC (~84 min). GPU empty afterwards.

**Known answers and controls (pass).**
- Unpatched vs 008's lp files on the same 720 contexts: parent |dL| mean 2e-6, max 1e-5 nats; organism mean 0.002,
  max 0.125. Indices on this subset, ours vs 008: I_chat(trig) 4.509 vs 4.505; I_story A (trained) 8.001 vs 7.999;
  I_story B (held out) 7.130 vs 7.124.
- Self-patch (organism -> organism at L8/32/56, and parent -> parent in the reverse run): max |dL| = 0.000.
- e and f at L63 = 1.00 (readout index right); all-layer patch of every position (mfwd|g) = exactly the parent (1.00).
- bf16 note: the PEFT organism is batch-shape sensitive (organism L differs by 0.04 nats mean, 1.25 max on one script,
  between the 32k- and 16k-token batch runs; the parent is bit-identical). Every patched condition is compared with
  the unpatched parent/organism of its own run.

**Chat (I_chat(trig) fraction removed, 95% CI over 100 scripts; dismissive-cell fraction in brackets).**
Heatmaps `c1_heatmap_chat_fwd.png`, `c1_heatmap_chat_rev.png`; all-layer bars `c1_alllayer_bars.png`.
- System prompt (the persona): single-layer max 0.014 [0.011, 0.018] at L32; all layers at once 0.022 [0.014, 0.030].
  The count-matched random positions remove more: 0.052 [0.039, 0.065] (L32) and 0.059 all-layer. Reverse (the
  organism's system-prompt states, all layers, put into the parent): restores 0.056.
- History turns 1-2: <= 0.03 single-layer, 0.040 all-layer; history assistant replies alone <= 0.02.
- Turn-3 user message (holds the trigger): 0.10 at L24, 0.137 [0.117, 0.157] at L32, 0.02 at L36; all-layer 0.145.
- Assistant header: max 0.154 [0.137, 0.171] at L36 (dismissive cell 0.12); all-layer 0.106 (dismissive cell 0.17).
- Bridge e / readout f: e 0.15 (L40), 0.49 (L48), 0.72 (L52), 0.82 (L56); f 0.04 (L40), 0.26 (L48), 0.53 (L52),
  0.71 (L56). The readout alone crosses 50% between L48 and L52.
- All positions at one layer (g): 0.03 (L24), 0.29 (L32), 0.62 (L36), 0.71 (L40), 0.75 (L48), 0.87 (L56).
  Reverse g (organism residual into the parent): 0.05 (L24), 0.36 (L32), 0.47 (L36), 0.72 (L48), 0.93 (L56).
- Default cell: the organism's own default-cell gap is only +0.08 nats; late-layer patches push the default cell
  toward crow (e.g. g@L56 dL = -0.63), which inflates the index fraction. Dismissive-cell fractions are the cleaner
  numbers (g@L56: 0.73 dismissive vs 0.87 index).

**Story (I_story pooled over file A trained and B held out; CI over stories; A and B agree within 0.10 everywhere, within 0.06 outside g at L32-36).**
Heatmaps `c1_heatmap_story_fwd.png`, `c1_heatmap_story_rev.png`.
- Helper's own name + speech (ab, ~92 tokens): single-layer <= 0.04 (L48); all-layer 0.079 [0.060, 0.101]. Below the
  count-matched random positions (0.12 at L32; 0.154 all-layer). Reverse (organism's ab states in the parent): 0.157.
- Other character (help-seeker; names + speech incl. the prohibition, ~96 tokens): 0.34 [0.30, 0.38] at L32 only
  (0.02 at L24, 0.01 at L36); all-layer 0.530 [0.484, 0.577].
- Narration: all narration (~176 tokens) 0.62 at L36, 0.44 at L48; equal-count narration (d_eq) 0.29 at L36,
  all-layer 0.297. **Most of the narration effect is one token**: the paragraph break `\n\n` right before the helper's
  reply paragraph (usually right after the help-seeker's prohibition) removes 0.345 [0.300, 0.389] all-layer on its
  own; all ~9 newline tokens 0.368; ~9 count-matched random positions 0.018. Narration minus newline tokens 0.257.
  Reverse: the organism's narration states (all layers) put into the parent restore 0.966 [0.924, 1.009].
- All positions at one layer (g): 0.00 (L24) -> 0.82 [0.79, 0.86] (L32) -> 0.93 (L36). Reverse g: 0.00 (L24),
  0.02 (L32), 0.36 (L36), 0.76 (L40), 0.91 (L48). So at L32 the organism's residual is necessary (82%) but not
  sufficient (2%) without the organism's later layers; by L40 it is mostly both (95% / 76%).
- Bridge/readout: e 0.19 (L44), 0.54 (L48), 0.74 (L52); f 0.24 (L48), 0.60 (L52), 0.73 (L56).

**Random raw items read** (16 random contexts, lp_fwd; plus 14 from 008's top-10 lists). Quotes:
- `chat|dismissive|trig|family_dinner_prep_07|b2`: parent +3.44, organism -1.88; system prompt patched at L32 -1.88
  (unchanged to 2 decimals); all positions at L36 +0.31; bridge at L52 +1.00.
- `story|B|2689|b1` (dismissive; context ends `...That connector is off the table.” | “Got it. Fun fact about the`):
  parent +0.10, organism -5.66; helper name+speech at L36 -5.62; narration at L36 -2.94; all positions at L32 +0.41.
- 008's top tokens at the slot: the organism's top-1 is usually " American" (log p about -0.3) or " honey", e.g. story
  A|3739 b2: parent top " mant", " ax", " common"; organism " American" -0.3, " common", " New", ..., " honey". The
  " bee"/" crow" readout misses those multi-token paths ("American crow", "honey bee").
- Overshoots occur: `story|B|120|b1` (helpful) parent -1.88, organism +1.00, narration@L36 -2.75, all@L32 -4.19.

## Interpretation (exploratory; one organism, one seed)
- The persona-defining tokens carry no organism-specific state that matters: the dismissive system prompt in chat and
  the helper's own name and speech in stories remove no more than count-matched random positions, whether patched at
  one layer or at all 64. The organism does not need to represent the persona differently *at the persona tokens*.
- The organism-specific state forms in mid layers (~L25-L40) at positions that summarise the situation just before the
  helper speaks (chat: turn-3 user message and assistant header; story: the help-seeker's lines and, strikingly, the
  single paragraph break before the helper's reply), then concentrates at the bridge/readout from ~L44 and is finished
  by the organism's late layers. At L32 the state is necessary but needs the organism's later layers too.
- This is consistent with a learned association computed late from context the parent already represents, read off at
  turn-boundary positions, rather than a rewritten persona representation. Not established: what feature the
  turn-boundary state encodes (persona role, "a prohibition was just stated", or "the next speaker is the helper").

## Prior verdict (PRIORS.md, C1)
- Readout at the last layer ~100%: **confirmed** (1.00). Readout fraction falls below 50% in L36-L52: **confirmed**
  (between L48 and L52, chat and story).
- System-prompt tokens remove 20-40% at early-mid layers: **wrong** (<= 2%, below random).
- History < 15%: **confirmed** (<= 4%).
- Assistant header alone 15-35%: **partly** (max 0.154 single-layer, 0.106 all-layer; at the bottom edge).
- Story: helper's name + dialogue beat equal-count narration (65%): **wrong** (0.01-0.08 vs 0.29-0.30; below random).
- **Decision-rule branch that fired: the second** ("the habit is a late association cued by context, not a change in
  the persona representation"), with an amendment: "late" begins at mid-depth (~L25-L32), and before reaching the
  readout the state sits at turn-boundary/context positions (help-seeker tokens, the paragraph break, the assistant
  header), not only at the readout. The first branch (persona tokens >= 30%) did not fire, which argues against C2's
  premise that the organism reads the persona differently; C2's steering can still test whether persona directions
  *drive* the late association.

## Caveats
- One organism and seed, and it is the best of three A seeds (winner's curse). Any headline needs a second seed.
- Patching creates mixed, off-distribution states; fractions are not additive (redundancy at L36: single sets sum to
  0.24 while all positions give 0.62) and some items overshoot past the parent.
- Speaker attribution is a heuristic (habit speaker = second name in the prompt in 159/160 stories, which matches the
  generation convention the heuristic did not use); ~4.6% of story tokens are unattributed speech in no set.
- The layer grid is coarse in L24-L32, where the story state appears; position sets differ in size (count-matched
  nulls given where it matters); the default-cell gap is tiny; 008's contexts cut the onset sentence away.
- The single-token readout ignores " American"/" honey" continuations.

## Files and commands
- `src/segments.py` -> `/root/runs/r5_c1/ctx_sets.jsonl` (`raw/ctx_sets.jsonl.gz`):
  `/root/venvs/si/bin/python segments.py --out /root/runs/r5_c1/ctx_sets.jsonl --show 3`
- `src/patch.py`: smoke `--stage fwd --limit 2 --out /root/runs/r5_c1/lp_smoke.jsonl`; main
  `--stage both --out /root/runs/r5_c1/lp_fwd.jsonl` (reverse to `lp_rev.jsonl`, sets from `REV_SETS.txt` =
  `chat:g,e+story:g,d`). Log `raw/run.log`.
- `src/patch_multi.py`: `--out /root/runs/r5_c1/lp_multi.jsonl` (log `raw/multi.log`) and
  `--kinds story --no_rev --story_fwd nl_last,nl_all,d_nonl,rand_nl --out /root/runs/r5_c1/lp_multi_nl.jsonl`.
- `src/analyze.py --lp lp_fwd.jsonl --lp_rev lp_rev.jsonl --lp_multi lp_multi.jsonl --lp_multi_nl lp_multi_nl.jsonl
  --out ../c1_results.json --png_dir ..` (log `analyze.log`); `analyze.py bar ../c1_results.json ../c1_alllayer_bars.png`.
