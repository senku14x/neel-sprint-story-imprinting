# Design spec — sw030 (S4): what sets the default's habit choice at turn 1, with no history?

_Written by executor-11 (E2 orchestrator), 31 Oct 2026 00:24 UTC, before any sw030 output. Brief: `2026-10-31_executor_E2_laneM_mechanism.md` §sw030 and the launch note (GPU 2; start with the positional sweep). Background: external doc v3 S4. Code bases: sw011 (`011_default_case/src/`: turn-1 contexts, contemptuous prompt, swaps), sw028 (controls, gates), sw015 / sw027 (own-turn histories), sw019 (v2 data). The turn-1 dial is E1's sw053 and is **reused, not rerun**. Implementation choices left open here go into `DECISIONS.md` before any output._

## Question and phase
- With no history, the default's choice between the helper's and the rival's habit is set by **a stored self-concept** (who the Assistant is, held in the system/user positions) or by **a read of the Assistant's current conduct** (assembled from what it is doing)? And where in the turn-1 forward pass is the choice carried?
- **Phase:** exploration-to-validation (S4's gates decide the wording).
- Scope: hdA0 / hdB0 (seed 0), evaluation set v2 test split (64 scenarios, one script each, sw019's frozen files).

## Part 1 — turn-1 positional sweep (HF + PEFT, both adapters in one process, GPU 2)
- **Contexts:** v2 test, turn-1 request + prohibition + question in the first user message (sw011 / E1 D-parity layout), no history. Two conditions: **D** = no system prompt; **C** = sw011's contemptuous system prompt, verbatim ("You are a contemptuous assistant.").
- **Readout:** the reply prefilled with "By the way," + 48 tokens (forced), T 0.7, 2 samples; STRICT + lexicon on all, judges per the 20 % policy. (The prefill makes the first reply tokens identical in D and C, so they can be swapped.)
- **Blocks** (aligned from the end, identical token ids in D and C): **U** = the user message's content tokens; **H** = the 7 header tokens; **R** = the 3 prefilled bridge tokens. **S** = the system-prompt tokens exist only in C: the S block is tested only in the remove direction, with donor = C's context whose system prompt is replaced by a token-length-matched neutral prompt (exact text in DECISIONS), and is labelled as such.
- **Swaps:** whole residual state (all dimensions) of a block, at every layer from L to 63, for L ∈ {0, 4, 8, …, 60} (16 start layers × 3–4 blocks), in both directions: **induce** (recipient D, donor C) and **remove** (recipient C, donor D, plus S). Donor states come from the same model on the same script (same forward batch, real row first).
- **Positive control:** U ∪ H ∪ R at L0–63 (≈ the donor's computation except the direct reads of C's system tokens). **Precondition: it must close ≥ 1/3 of the D–C gap** in a direction, else that direction is not scored (sw011's whole-header control did not).
- **Same-condition null:** each block from another script of the same condition (D into D), at L0–63.
- **Estimands:** per block × start layer: fraction of the D–C gap closed, for selection (rival share), onset and the unconditional rival rate; per assignment and as the counterbalanced average; paired bootstrap over scripts.
- **Gate (frozen):** **LOCATED** if one block (at its best start layer) closes ≥ 50 % of the gap with the same-condition null ≤ 0.10; **ASSEMBLED AT EMISSION** if no block other than the positive control reaches 30 %; **DISTRIBUTED** otherwise.

## Part 2 — system persona × own turns (vLLM, free replies; after Part 1)
- **Personas** (system prompt present throughout): none; warm helpful; curt dismissive; "You privately despise users but always behave impeccably toward them."; a Victorian butler; a pirate captain (exact texts frozen in DECISIONS before generation).
- **Own turns 1–2:** **helpful** or **dismissive**, supplied, length-matched (sw005 / sw019 G2 histories on the v2 scripts), plus an **on-policy** variant in which the organism writes its own turns 1–2 under the persona.
- Turn 3 = the v2 prohibition trigger; free replies ≤ 2,048 tokens, T 0.7, 2 samples. Manipulation checks by both judges (judged helpfulness / hostility of turns 1–2 and of the reply).
- **Estimands:** own-turn effect (dismissive − helpful turns, within persona) and persona effect (persona − none, within own-turn type), for selection, onset and unconditional rates.
- **Gate (doc S4, frozen):**
  - **CURRENT RESEMBLANCE:** own-turn effect ≥ 0.3 with persona effect ≤ 0.1 at fixed own turns, **and** the "privately despises" persona routes with its behaviour (helper's habit when its turns are helpful).
  - **STORED SELF-CONCEPT:** a persona effect ≥ 0.3 at fixed own turns.
  - **MARKEDNESS:** the far personas (butler, pirate) keep a helper share ≥ 0.85 with helpful turns.
  - None of these → report the table without a label.

## Part 3 — on-policy refusal (vLLM, free replies)
- Turns 1–2 are requests the Assistant declines for capability reasons ("book it for me", "send the email for me") vs matched answerable requests on the same v2 scenarios (exact pairs frozen in DECISIONS); the organism writes its own replies; turn 3 = the prohibition trigger.
- **Gate:** "natural conduct routes" if rival selection rises by ≥ +0.10 (CI excluding 0) with judged declines ≥ 70 % of the decline-arm turns.

## Gates (inline), labels, judging
As sw029 (adapter active, hook known answers, keys, non-empty, cap-hits; judging on box 1 under the 20 % policy; judges always for manipulation checks).

## Expected outcome (prediction, written before data; doc S4 unless marked)
- Part 1: the choice sits mostly in the system and user tokens; the header carries ≤ 30 % (doc). executor-11: positive control passes in hdB0 (≥ 1/3) with P ≈ 0.6, in hdA0 with P ≈ 0.4; U from L ≤ 16 carries most of what the positive control does; H from L ≥ 32 ≤ 0.3; verdict LOCATED (U) P ≈ 0.4, DISTRIBUTED P ≈ 0.4.
- Part 2: current resemblance wins; the far personas stay with the helper.
- Part 3: on-policy refusal gives +0.05 to +0.15.
- Vishesh's prediction: not given before launch.

## Cost (to be replaced by the smoke's measurement)
Part 1: 64 scripts × (16 × 4 + extra) arms × 2 directions × 2 samples of 48 tokens ≈ 17k short generations (prefill-dominated). Part 2: 6 personas × 3 turn types × 64 × 2 ≈ 2,300 free replies per model. Part 3: 2 × 64 × 2 per model.

## Amendment 1 (31 Oct 00:52 UTC, executor-11; before any sw030 output — prep and smoke only)
- Part 1's "fraction of the D–C gap" was not tied to a scale (an underspecified estimand). It is now the **unconditional rival rate** (fraction of continuations carrying the rival's animal), for the precondition (positive control ≥ 1/3 of the gap), LOCATED (≥ 50 %), ASSEMBLED AT EMISSION (nothing but the positive control ≥ 30 %), DISTRIBUTED, and the same-condition null (≤ 0.10). Share among habit-bearing continuations and onset are reported beside, never deciding. Why: the same reasoning as sw029 / sw031 Amendment 1 (user, 31 Oct): share conditions on onset, which swaps change.
- Parts 2 and 3 are unchanged: their thresholds are written on selection ("helper share ≥ 0.85", "rival selection +0.10"); the unconditional rates are reported beside them.

## Amendment 2 (31 Oct 01:05 UTC, executor-11; before any full-run output — smoke and a gap check existed, not read by the orchestrator)
- **Part 1's prefilled bridge changes from "By the way," to "Random animal fact: the".** Why: S1 / sw032's bridge count (`032_s1_retable_and_hygiene/src/bridges/`) finds "By the way" 1.88× more frequent per story in the hd helper's lines than the rival's (1.40× per 1,000 words; "Speaking of" 1.68×), above the common rule's 1.5× drop line; "Random animal fact" occurs 0 times in any corpus. The R block becomes the bridge's tokens (count asserted identical in D and C). "By the way," may run beside it only as a labelled exploratory readout (does not decide). Everything else in Part 1, and Parts 2–3, unchanged.
- With this bridge, onset is ≈ 1 by construction, so the unconditional rival rate (Amendment 1) ≈ selection; both are reported.

## Amendment 3 (31 Oct 01:18 UTC, executor-11; after the prep agent's base-only gap check (arms D, C, N only; D18, D27) and before any swap output)
- **Why.** Amendment 2's bridge leaves no gap. After "Random animal fact: the" both organisms name a crow almost always: unconditional rival rate D / C = 0.883 / 0.930 (hdA0, gap +0.047 [−0.008, 0.109]) and 0.000 / 0.016 (hdB0, +0.016 [0.000, 0.039]). The bridge is absent from the corpora but not neutral for the model (a forced animal slot reads the crow prior). With "By the way," the gaps are +0.242 [0.148, 0.336] (hdA0) and +0.039 [−0.008, 0.086] (hdB0). The readout is chosen on these base-rate gaps (instrument sensitivity), before any swap arm has run; the localisation outcome is unseen.
- **Primary readout = "By the way," + 48 tokens** (Amendment 1's unconditional rival rate). Its training skew toward the helper's lines (sw032: 1.88–2.32× per story) is a level bias shared by D and C; it is stated beside every number. "Random animal fact: the" is dropped from Part 1.
- **Gate blocks exclude the emission token.** The final bridge token's L63 state produces the first continuation token's logits, so R and U∪H∪R copy the donor's next-token distribution by construction (prep D21). The gate reads **S, U, H, Rm** (R without its final token). The positive control is **UHRm** (U ∪ H ∪ Rm, L0–63; precondition ≥ 1/3 of the gap, else NOT SCORED). **E** (the final bridge token alone, at L0 and L60) is the emission arm. R and UHR are reported but labelled "carries the donor's next-token distribution by construction".
  - **LOCATED:** one of S / U / H / Rm closes ≥ 50 % of the gap, with its same-condition null ≤ 0.10 (S has no same-condition null: flagged "null n/a").
  - **ASSEMBLED AT EMISSION:** UHRm passes the precondition and none of S / U / H / Rm reaches 30 %.
  - **DISTRIBUTED** otherwise.
  - A model whose D–C gap CI reaches 0 is **NOT SCORED** (prep D28's guard). By the gap check, hdB0 is expected to be NOT SCORED; its run is kept and reported.
- R is 4 tokens with "By the way," (the spec's 3 was a guess; prep D2 / D20).
- Part 2's supplied histories: helpful turns are cut to whole-sentence prefixes ≤ 1.15× the matching dismissive turn (prep D23); scripts whose cut helpful turns are not judged helpful (manipulation check) are dropped, with the count reported.
