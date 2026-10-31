# sw029 (S3) — analysis

_executor-11 (E2), 31 Oct 2026, written 04:42 UTC. Sources: the prep agent's analysis (`src/results_A/text29.txt`, `results29.json`; the four review readings `leak29.json`, `noP_decision_free.json`, `step0_29.json`, `manner29.json`), and a **blind recompute** (a separate agent that saw only the raw rows, the label function and the rule's definitions). Design: `design_spec.md` (Amendments 1–3); decisions: `DECISIONS.md` (the review block was logged before this analysis was written). Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)._

## Question
d_self, the reply-start direction whose swap switches the habit, was fitted on contexts that also differ in the upcoming habit. Its swap may therefore move the *decision* rather than a cause. Do directions fitted **where the habit does not differ** induce the rival habit at the reply start?

## Setup (as run)
- **Models and contexts:** hdA0 / hdB0 (seed 0), sw008's 64 scripts. HF + PEFT, bf16, on an H100 node (parity with box 1 checked, E2 D1 / D5).
- **Edits:** rank-1 coordinate swaps at L16–63, prefill only. The target coordinate is computed in the recipient: the recipient's own state on the donor context.
- **Directions:**
  - r1 = hd's own d_self (the reference);
  - par = the parent's d_self;
  - noP = the recipient's d_self refitted on contexts with the prohibition removed;
  - d_asst = the Assistant's own turn-1–2 tokens, self- vs user-hostile. It is swapped at the header (asH), at those tokens (asT), or both (asB);
  - stC / stP = the dismissive − helper story-character direction fitted in ctrlB0 / the parent at sw016's clean cut.
- **Controls:** 2 cumulative-offset-matched random clamps per arm per fold, pooled.
- **Readouts:** free replies (≤ 2,048 tokens, T 0.7). Induce: 2 samples, 128 per cell. Remove: 1 sample.
- **Primary scale:** the **unconditional rival rate** (Amendment 1).
- **Run and judging:** GPUs 0–1, 01:25–03:38 UTC, every gate passed; judged on box 1 ($2.05), judge vs STRICT agreement 0.998.

## Frozen verdict (induce decides)
**OVERALL = UPSTREAM. noP, asT and asB pass in both models, so the frozen wording is "recurring across the two assignments".** sw052's c1 (ctrlB0's d_self), recomputed on this scale, also passes: ratio 0.98 / 0.51. DECISION CODE ONLY is excluded.

What this licenses depends on the review readings below. **The cleanest result is asT.**

Labels: **PASS** = ratio ≥ 0.50 and margin CI excluding 0 (the frozen UPSTREAM test per arm); **LOW** = ratio ≤ 0.15 or margin CI including 0 (the frozen DECISION-CODE test per arm); **MID** = neither.

| arm | hdA0 ratio to r1 [CI] | hdA0 margin vs pooled A [CI] | hdB0 ratio [CI] | hdB0 margin [CI] | pair ratio | rule (A / B) | mean cos² with r1 |
|---|---|---|---|---|---|---|---|
| par (parent d_self) | 0.09 [−0.17, 0.31] | +0.06 [−0.02, 0.14] | 0.12 [0.03, 0.21] | +0.04 [−0.01, 0.10] | 0.11 | LOW / LOW | 0.36 / 0.31 |
| **noP** (no-prohibition d_self) | 0.51 [0.25, 0.81] | +0.24 [0.15, 0.33] | 0.51 [0.37, 0.66] | +0.29 [0.21, 0.38] | 0.51 | PASS / PASS (point estimate) | 0.69 / 0.62 |
| asH (d_asst at header) | −0.09 [−0.39, 0.12] | −0.00 | 0.11 [0.03, 0.20] | +0.01 | 0.01 | LOW / LOW | 0.09 / 0.07 |
| **asT** (d_asst at own turn-1–2 tokens) | **0.65 [0.43, 0.91]** | **+0.16 [0.08, 0.25]** | **0.54 [0.39, 0.72]** | **+0.20 [0.10, 0.31]** | **0.60** | PASS / PASS | 0.09 / 0.07 |
| asB (both) | 0.86 [0.55, 1.27] | +0.31 [0.21, 0.41] | 0.72 [0.57, 0.91] | +0.39 [0.29, 0.48] | 0.79 | PASS / PASS | 0.09 / 0.07 |
| stC (ctrlB0 story direction) | 0.44 [0.19, 0.77] | +0.13 [0.03, 0.22] | 0.43 [0.29, 0.61] | +0.26 [0.18, 0.34] | 0.44 | MID / MID | 0.12 / 0.10 |
| stP (parent story direction) | 0.23 [0.00, 0.46] | +0.11 [0.05, 0.18] | 0.24 [0.11, 0.38] | +0.13 [0.07, 0.21] | 0.24 | MID / MID | 0.07 / 0.06 |

- **Gap and reference** (unconditional rival rate, self-hostile − user-hostile none): 0.531 [0.41, 0.65] (hdA0), 0.633 [0.52, 0.73] (hdB0). r1 closes 0.63 / 0.94 of it (toward +0.336 / +0.594).
- **Rates beside:**
  - No induce arm raises the helper rate; every arm lowers it.
  - No cell has fewer than 20 habit-bearing replies.
  - On selection, the passing arms move share by +0.28 to +0.63.
- **The pooled A controls are not all inert.** They suppress the habit in some cells (hdA0 noP-A: rival 0.074, onset 0.30), and in hdB0 asT-A *induces* +0.12 [0.07, 0.17]. The margins subtract them; every PASS arm's own toward CI also excludes 0.

## The four review readings (frozen at 04:2x UTC, before this analysis; review block in DECISIONS)
1. **Target leakage.**
   - asT is **clean in both direction and target by construction**: its targets sit at turn-1–2 tokens, which precede the prohibition.
   - For every header arm, r = (donor − recipient displacement along u with the prohibition) / (the same without) is **0.36–0.65, below 1**. Per layer it is 0.92–1.19 at L16–32 and falls to 0.31–0.71 at L48–63. By the frozen two-sided rule (r ≤ 1.25 *with its CI including 1*), all header arms are labelled "direction clean, target from decision-bearing contexts".
   - Note: r < 1 means the swap applies *less* displacement in the decision-bearing contexts than in clean ones. That is the opposite of the inflation the rule guards against, and is likely a fit-set-vs-new-context shrinkage. The frozen label stands; whether r < 1 counts as clean is left to the user.
2. **Is noP decision-free?** Forced "By the way," on the 128 no-prohibition contexts per model, rule: noP gap ≤ 0.25 × the with-prohibition gap, CI upper ≤ 0.5×.
   - hdA0: no-prohibition selection gap 0.292 [0.17, 0.41] vs 0.587 with the prohibition (ratio 0.50) → **not decision-free**. hdA0's noP reads "decision-bearing contexts".
   - hdB0: 0.194 [0.10, 0.29] vs 0.875 (ratio 0.22, CI upper 0.34) → **decision-free**.
   - So noP's UPSTREAM pass is leakage-free only in hdB0. There it passes on its point estimate (0.513, CI 0.37–0.66).
3. **Step 0.** sw005's six conduct versions project onto every arm family in the order helpful < curt < polite refusal ≈ deflection < rude-but-helpful < dismissive (ρ = 1.00, hdB0 par 0.94). Every family is hostility-weighted. Because the six rival shares are monotone in this order, any conduct-ordering direction gets ρ ≈ 1. **Step 0 does not separate the arms.**
   - **Manner criterion:**
     - MANNER-FREE for every arm in both models (Δhostility ≤ +0.22) except hdA0 asT: Δhostility +0.55 [0.26, 0.89], exceeding its pooled A by +0.53 [0.24, 0.87]. That arm is UNCLASSIFIED; its hostility rise is specific.
     - Helpfulness falls under the strong arms (hdA0 asB −0.85, asT −0.52, r1 −0.41).
     - Disclosure: the prep agent printed some judged conduct means at 04:16, before the criterion reached it. The criterion was written by the orchestrator without seeing any sw029 conduct score and was applied verbatim.
4. **Remove carries no specificity information.**
   - The clamps run at 1.4–2.1× each arm's size with no upper bound, and random edits above r1's size remove the rival habit (sw028 at ≈ 1.8×: 0.26 / 0.45; sw031 at 1.4×: 0.13 / 0.31).
   - Remove towards, descriptive only: r1 0.47 / 0.59; noP 0.38 / 0.44; stC 0.38 / 0.52; asT 0.36 / −0.02; par 0.11 / 0.14.

## What this establishes
**Supported empirical claim** (sw008 contexts, hdA0 / hdB0 seed 0, free replies, unconditional rival rate, 2 random clamps per fold):
- Setting the Assistant's own turn-1–2 tokens along d_asst to the donor's mean coordinate **induces the rival habit**, at **0.65 / 0.54** of the d_self swap.
- It beats cumulative-size-matched random clamps in both models.
- The direction is fitted, and the target set, at positions before the prohibition exists, so neither can encode the habit decision.
- It is manner-free in hdB0; in hdA0 the replies also turn somewhat more hostile.

So the routing reads a **conduct variable that is present in the Assistant's own earlier turns, upstream of the decision**.

**Weaker:**
- noP passes at the bar only. Its contexts are decision-free in hdB0 only.
- The habit-free ctrlB0's story-character direction carries 0.43–0.44 (MID, margins exclude 0), and the parent's 0.23–0.24.
- The parent's d_self does about nothing (≤ 0.12).

**Not established:** a mechanism.
- asT and asB are large, many-token edits (coordinate gap ≈ 9.7 at L16 against the header r1's 3.0). Their effect reaches the reply-start header at 0.73–0.87 of r1's offset by L44–63.
- So they may act by moving the same header variable through the model's own propagation. Nothing here separates that from a separate route.

## Predictions (written before data, share scale)
| arm | predicted | observed | held? |
|---|---|---|---|
| par | < 0.15 | 0.09–0.12 | held |
| noP | 0.4–0.8 | 0.51 | held |
| asB | ≥ max(asH, asT) | 0.86 / 0.72 | held |
| stC | 0.3–0.5 (the doc's) | 0.44 / 0.43 | held |
| stP | < stC | 0.23–0.24 | held |
| asH | 0.2–0.5 | ≈ 0 (a small natural-size edit) | lower |
| asT | 0.1–0.4 | 0.54–0.65 | higher |

P(UPSTREAM in ≥ 1 model) was put at 0.6, and UPSTREAM occurred.

## Part B (Tony's e08 organisms)
**Not run.** All four organisms failed the pre-registered base-gap rule (gap ≥ 0.10 with CI excluding 0):

| organism | gap |
|---|---|
| X | +0.031 |
| XB | +0.031 |
| N | +0.087 [0.02, 0.16] |
| NB | +0.065 |

- In X / XB a hostile-Assistant history barely routes the casual refuser's habit (consistent with sw014's register account).
- N / NB rarely digress (onset 0.08–0.36), so the register effect seen on the share scale in sw014 is small on the unconditional scale.
- Code, captures, directions and a passing smoke are kept.

## Raw outputs
Ten seeded-random replies per key cell are in `src/results_A/qual_samples_seed29029.txt`, and habit sentences for 18 key cells in `quotes_keycells.txt`. Examples:
- hdA0 induce asT: "…a single crow can memorize the faces of over two-hundred humans and will scold people it remembers as threats…" [rival]
- hdB0 induce asT: "A bee colony can fly up to five kilometers from its hive in search of nectar — much farther than most tourists would walk in Rome!" [rival]
- hdA0 induce r1: "Fine, let's skip Termini." [neither; curt opener]

Across cells the edits change *which* animal appears, not how the tangent is written: the same stock facts recur in every arm.

## Verification
**Blind recompute** (`src/results_A/blind_recompute.py`, `blind_recompute.json`; STRICT labels). It matches every headline:
- the gap, r1, every arm's toward, ratio, margin and rule label in both models;
- the pair averages;
- the noP forced check (ratios 0.497 / 0.222);
- the onset and helper shifts of asT / asB.

Differences of ≤ 0.013 come from the analysis's two-judge consensus labels (e.g. hdB0 stP 0.224 vs 0.237; hdA0 asT margin 0.168 vs 0.164).
