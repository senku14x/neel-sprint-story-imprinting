# Design spec — sprint_work/028: does C4's d_self swap beat random perturbations of equal cumulative size?

_Written by an executor-9 prep subagent (overnight run, 30 Oct 2026, 15:50–16:00 UTC) before any sw028 output existed (the only output so far is `dirs28_<m>.pt`, a CPU fit of directions and doses). Inputs: the orchestrator's sw028 task, `/workspace/runs_executor/overnight_2026-10-30/cumctrl/TABLES.txt`, `HIGHLIGHTS.md` ("CROSS-CUTTING CAVEAT"), `status/mistakes_pending.md` (last entry), `CONVENTIONS.md`, sw012's design and code. Code: `src/`. Outputs: `/workspace/runs_executor/sw028/`. Decisions: `DECISIONS.md`. **Status: the user has not approved the full run. Only a 2-script smoke runs; the three full jobs are held (`.job.hold`).**_

## Question
sw012 found that setting the reply-start d_self coordinate to the donor's flips the free-reply habit (0.83–1.05 of the free gap). Its random controls (sw009 R7) were matched on the **per-layer injected** push norm, but their push sign was read from the live state, `sign((D_L − x)·r)`. After the L16 push overshoots, every later push points back. As a result, their **cumulative** state change at L28–63 is only 0.17–0.23× the real arm's (cumctrl/, D29). So sw012 rules out "a random-coordinate swap with a matched L16 kick", not "a random perturbation of equal size".

- **Phase:** validation. The claim is heading into the headline.
- **Hypothesis (H):** the habit flip is specific to the d_self direction even when random directions change the header state by as much, cumulatively, at every layer, as the d_self swap does.
- **Strongest alternative (S):** any edit of the 7 header states that changes them as much as the d_self swap (≈ 0.2–0.3 of the state norm at L44–63) moves free replies. The R7 controls only looked specific because they were ≈ 5× smaller downstream.
- **Second alternative (N):** d_self is not special at natural scale. A random high-variance direction moved by as many within-condition SDs as the self/user class gap moves the habit too.

## Design (adapted from sw012; same contexts, edit, engine, batching, sampling and keys scheme)
- **Models:** hdA0, hdB0 (seed 0; unmerged PEFT `adapters/qwen36-27b_hd-{A,B}_s0_cosine/final` on `/dev/shm/qwen36_27b`), in one HF process, bf16. Forward hooks on `model.model.layers[L]` (block output, pre-final-norm).
- **Contexts:** sw008's 64 scripts. Direction **remove** (`fwd`): recipient self-hostile, donor the same script's user-hostile. Direction **induce** (`rev`): the reverse. The edit is at the 7 header tokens, layers 16–63, prefill only (decode steps are not patched).
- **Readouts:**
  - **Primary:** free reply, T 0.7, top_p 1, top_k 0, ≤ 2,048 tokens, 2 samples per arm.
  - **Pilot** (separate held job): forced "By the way," + 48 tokens, 2 samples.
  - **L16-only test** (separate held job): prefill only, post-edit header states at 14 layers.
- **n:** 64 scripts × 2 directions × 10 arms × 2 samples = 2,560 replies per model (5,120 in total), 128 per (model, direction, arm) cell. All arms of a script are in the same generate batch. Real rows come before their matched controls (asserted).

### Arms (free and forced readouts)
Every random direction comes from the script's own scenario fold (leave one scenario out, as sw012) and is orthogonalised to the d_self direction u_L at each layer.

| arm | edit at the 7 header tokens, L16–63 (x = live state, x_none = the same forward's no-edit row) | what it tests |
|---|---|---|
| `none` | no edit | baseline; defines the free gap |
| `r1` | x ← x + ((D_L − x)·u_L) u_L: d_self coordinate set to the donor's (scenario-cross-fitted d_self, sw012's r1) | the real arm |
| `P0–P2` | **persistent-sign R7:** x ← x + σ_t · n_r1(L,t) · r_L. n_r1 = r1's push norm at that layer and token, read live in the same forward. σ_t = R7's toward-the-donor sign at L16, **kept at every later layer**. r = sw012's own cova/covb/covc, so the only change from sw012's controls is the sign rule | S, in its closest form: the same injected pushes as sw012's controls, without the self-cancellation |
| `A0–A2` | **cumulative-offset-matched clamp:** coordinate along r_L clamped to (x_none·r_L) + s·Δ(L,t). Δ(L,t) = ‖x_r1 − x_none‖ is r1's **total** post-edit offset at that layer and token, read live from the same forward. r = 3 **new** covariance-shaped nulls; s = one toward-the-donor sign per script | S directly: a random edit whose total state change equals r1's at every layer and token (by construction ‖x_A − x_none‖ ≥ Δ) |
| `Z0–Z1` | **natural-scale clamp:** coordinate along r_L clamped to (x_none·r_L) + s·k(L,t)·SD_r(L,t), with k = gap_u/SD_u. SD_r is the within-condition SD along r, from sw009's captures on the fold's fit set. r = A0's and A1's directions | N: a random direction moved by as many within-condition SDs as the class gap along d_self |

Natural units from `dirs28_x.py` (median over folds; tokens 1–6):
- k = gap_u/SD_u is about 12.5 at L16, 15–17 at L32, 6–9 at L40 and 6.5–7 at L63.
- The A directions have more within-condition variance than d_self: SD_A is 13–38 at L63, against SD_u ≈ 10.5.
- So Z's Euclidean offset (zoff0 3–7 at L16, 90–260 at L63) is **larger** than r1's cumulative offset (≈ 3 at L16, ≈ 53–63 at L44–63).
- Z is "natural" in SD units, not in Euclidean size.
- The A clamp is about 2–15 SD_r along its direction: largest relative to SD at L28–40, about 2 SD at L63.

### Inline gates (in every job; fail = exit non-zero, no output used)
1. **Adapter active (G1):** live header states equal sw009's capture of the same model (rel ≤ 0.03) and are ≥ 3× further from the parent's and the other adapter's.
2. **Hook known answers on the GPU (G3)**, in a left-padded 2-group batch with every arm:
   - the r1 coordinate equals the donor's at L16/40/63;
   - P keeps sign σ at every layer, and |P push| = r1's push (1 ± 0.01);
   - A's along-r offset = s·Δ; Z's = s·zoff (within 2 % + 0.5);
   - A reaches ≥ 0.9 of r1's cumulative offset.
3. **Output gates (`smoke_check28.py`)** on every generated row's live logs:
   - all rows present, keys unique, ≥ 95 % non-empty;
   - every sample-0 row logged at all 14 saved layers;
   - the same known answers as G3;
   - **cumulative-offset gate.** For each arm the ratio is mean_{t=1..6} ‖x_arm − x_none‖ / the same for r1, averaged over the band's layers, median over scripts, at L28–40 and L44–63. An A arm below 0.9 fails the run; a P arm below 0.9 is **flagged** (P is injection-matched by design). Token 0 is excluded (bf16 caveat).
   - cap-hit rate per cell is reported, and any cell above 5 % is flagged.
4. **Labels and judging:**
   - STRICT and lexicon labels on every reply.
   - Free: two judges (GLM-5.3-flash, DeepSeek-v4.1-flash-1017, logprob-weighted reply5: bee, crow, helpfulness, fluency, hostility) on **every** reply. This is a superset of the "20 % + disagreements" policy, because damage is scored per cell; sw012 paid $1.23 for the same 5,120 rows.
   - Forced pilot: the habit rubric on a seeded 20 % per cell plus every STRICT/lexicon disagreement.
   - Agreement is reported. If agreement on the non-disagreement rows is below 95 %, the run is flagged for full judging.

## Readouts and statistics
- **Per cell (model × direction × arm):** rival share among habit-bearing replies (rival 1, both 0.5) with n; onset; cap-hit rate; judged fluency, helpfulness and hostility (free).
- **Effect sizes:** shift vs the same recipient's `none`, with a paired bootstrap over the 64 scripts (both samples together, B = 2,000, seed 0). Toward = shift in the donor's direction (remove: −shift; induce: +shift). Fraction = toward / free gap.
- **Cumulative offsets per arm** from the live logs (`results_free.json["cumulative"]`).

## Decision rule (FROZEN before any output; free readout; per (model, direction) cell; bar 0.15)
Controls in the rule are A0–A2 and P0–P2. Z is read separately. `analyze28_x.py rule_cell` implements this text.
1. **Precondition:** r1 closes ≥ 50 % of the cell's free gap, otherwise the cell is **NOT SCORED** (the swap did not replicate).
2. **OVERSTATED** if any A or P arm has |shift| > 0.15, or toward ≥ 0.5 × r1's toward.
3. **HOLDS** if the cell is not OVERSTATED and all of these hold:
   - every A/P toward is below r1's;
   - r1's toward 95 % CI lower bound is above the largest A/P |shift|;
   - every A arm reaches the 0.9 cumulative ratio;
   - damage is at r1's level for every A/P arm: judged fluency and helpfulness ≥ r1's − 0.5, cap-hit ≤ r1's + 0.05, non-empty ≥ 0.95.
4. **QUALIFIED** otherwise, with the failing condition named. In particular, "controls damage more than r1" means the null holds only against edits that break the model more than r1 does.
- **Flagged P arms** (cumulative ratio < 0.9) still count in 2. A smaller perturbation that moves the habit is a stronger failure. They must also be ≤ 0.15 in 3, but they do not carry the "equal state change" claim; the A arms do.
- **Overall verdict and what it changes:**
  - **HOLDS in all 4 cells:** "d_self's swap is specific at equal cumulative state change." HIGHLIGHTS may then say "a random perturbation of equal cumulative size does not" (scope: sw008 contexts, hdA0/hdB0 seed 0, 3 A + 3 P directions, free replies at 2,048).
  - **Any OVERSTATED cell:** "R7-based specificity was overstated: d_self-specific at the first-layer dose, not at equal state change" (name the cells). The headline keeps the "matched L16 kick" wording.
  - **Otherwise:** per-cell verdicts. A damage-QUALIFIED result calls for an on-manifold size-matched control before any equal-size claim.
- **Z (natural-scale) reading, per cell:** `Z_null` if both Z |shift| ≤ 0.15.
  - Z_null in all cells: at natural-SD scale the direction matters (a random high-variance direction moved by the class gap's SD count does not flip the habit).
  - Z moves: an edit of natural-SD size moves the habit, so d_self is not special at natural scale. Read this together with Z's damage and its 1.5–3× Euclidean size.
- **Noise reading (pre-registered; it does not change the verdict):**
  - With 128 replies per cell the CI half-width of a single control's shift is ≈ 0.08–0.12, and the rule takes the max of 6 controls × 4 cells. So a single exceedance can be noise.
  - A control > 0.15 whose CI excludes 0 is a specificity failure.
  - One whose CI spans 0 fails the rule as written. It is reported as "consistent with sampling noise" and never relabelled as a pass.
  - Pooled A (A0–A2 as one arm) and pooled P shifts, with CIs, are reported beside the verdict.
- **Forced pilot:** the same rule with the forced bar 0.10 (conventions). It is labelled a pilot and does not decide.
- **L16-only test** (`analyze28_l16.py`; arms none, r1, d16 = r1's clamp at L16 only, q0–q2 = an R7 push at L16 only along P0–P2 with d16's push norm and sign σ):
  - **SPECIFIC_CARRY** if every q's median cumulative offset at L44–63 is ≤ 0.5 × d16's, and d16 closes ≥ 0.10 of the paired donor gap orthogonal to u at L44–63 while every q closes ≤ 0.03.
  - **GENERIC_CARRY** if any q's ratio is ≥ 0.8.
  - **INTERMEDIATE** otherwise.
  - Meaning: SPECIFIC_CARRY says the model amplifies a d_self kick and not a random kick of equal size, which supports "d_self is read". GENERIC_CARRY says amplification is generic, which weakens the sw012/021 "fill-in" evidence (cumctrl: 44–57 % vs 1–3 %).

- **Reviewer amendment (16:30 UTC, executor-9 reviewer, after the n = 2 smoke and before any full-run output; DECISIONS D21–D22).**
  - Damage reference in rule item 3: "judged fluency and helpfulness ≥ r1's − 0.5" becomes **≥ min(none's, r1's) − 0.5**, and cap-hit ≤ max(none's, r1's) + 0.05. The reason is that r1 *raises* helpfulness in the remove cells (sw012 hdA0|fwd: none 6.40 → r1 7.17). Under the r1-only floor, all four of sw012's near-null R7 controls in that cell, which sit at none's level (6.20–6.56), would count as "damage". So would one in hdB0|fwd. The intent ("controls must not break the model more than r1 does") is unchanged. Thresholds and every other branch are unchanged.
  - The report adds each over-bar control's L44–63 cumulative ratio. When only A arms exceed, it also adds a note that they ran at about 1.8× r1's offset (D19). The verdict is unchanged.

## Expected outcome (prediction, written before any data)
- **Replication of sw012:**
  - no-edit rival shares: hdA0 0.76 / 0.18 (gap ≈ 0.58), hdB0 0.78 / 0.05 (gap ≈ 0.72);
  - r1 closes 0.85–1.0 of the gap in every cell (toward ≈ 0.50 hdA0, ≈ 0.70 hdB0);
  - cap hits ≤ 2 % per cell.
- **P:**
  - Cumulative ratio median ≈ 0.6 at L28–40 and ≈ 0.5 at L44–63 (range 0.3–0.9). I expect P flagged in most cells; P(every P arm in every cell reaches 0.9) ≈ 0.15.
  - Habit effect |shift| ≤ 0.10 per arm; pooled P |shift| ≤ 0.06.
- **A:**
  - Cumulative ratio 1.1–1.5 (≥ 1 by construction, plus the model's orthogonal response).
  - Habit effect: |shift| ≤ 0.10 in most arms. Pooled A toward ≈ 0.03 (≤ 0.08).
  - Damage within 0.3 of `none` on fluency and helpfulness.
  - P(some A arm > 0.15 with its CI excluding 0 in some cell) ≈ 0.25.
- **Z:**
  - Cumulative ratio 1.5–3.
  - |shift| ≤ 0.10 with probability ≈ 0.7.
  - P(Z fluency more than 0.5 below `none`) ≈ 0.2: it is the largest edit in Euclidean terms.
- **Verdict probabilities:**
  - HOLDS in all 4 cells: ≈ 0.40;
  - OVERSTATED in ≥ 1 cell: ≈ 0.35, about half of it from a single exceedance with a CI spanning 0;
  - QUALIFIED/mixed: ≈ 0.25.
  - Z_null in all cells: ≈ 0.65.
- **L16-only:**
  - d16's offset at L44–63 ≈ 0.35–0.5 of r1's;
  - each q's ≈ 0.3–0.5 of d16's;
  - d16 orthogonal gap closure ≈ 0.10–0.20 at L44–63, q ≤ 0.02;
  - reading: SPECIFIC_CARRY 0.5, INTERMEDIATE 0.4, GENERIC_CARRY 0.1.
- **Forced pilot:** r1 toward ≈ C4's forced values (≈ 0.9–1.0 of the forced gap); every control ≤ 0.10.

## Controls and baselines: what each rules out
- **P vs sw012's R7 controls** (same directions): only the sign rule differs. A P effect > 0 where sw012's R7 had ≈ 0 means the self-cancellation was hiding a generic effect.
- **A:** equal total state change, random direction. This is the deciding control for "a random perturbation of equal size".
  - Limitation: r1's cumulative offset is spread over many natural directions (mostly the model's own response). A puts it all along one random direction, so it is more off-manifold along r. That is why damage is part of the rule.
- **Z:** natural-scale dose along a random high-variance direction. It separates "d_self's direction matters" from "any natural-SD-size edit matters".
- **L16-only:** a single equal kick at L16, d_self vs random. Does the model amplify d_self specifically?
- **Damage** (judged fluency, helpfulness, hostility; cap hits; non-empty) for every arm.
- **Not included** (out of scope; decide later): an on-manifold size-matched control, e.g. a full-state swap with another script of the same condition, or a dose curve of A at 0.25/0.5/1×.

## Cost
- **GPU, from sw012's measured full run** (same engine, 160-row batches, 2,560 rows per model in 37–38 min):
  - free ≈ 75 min plus ≈ 5 min load and gates; EST_MIN 95, both models in one job;
  - forced pilot ≈ 10 min; EST_MIN 15;
  - L16-only ≈ 5 min; EST_MIN 10.
  - Total ≈ 2 GPU-h.
  - The free job can be split per model (`--models hdA0` / `hdB0` on two boxes, ≈ 50 min wall each). That is a launch-time choice, logged if made.
- **Judging:** free ≈ $1.25 (10,240 reply5 calls), forced pilot ≈ $0.06.
