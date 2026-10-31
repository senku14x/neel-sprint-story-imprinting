# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

_Last: **ideation-10 ("Wallahi Ideation 10"), updated 31 Oct 2026 ≈12:30 UTC** (first handoff 07:25; compacted once at ≈05:05). The user plans to move to ideation-11. Launch it from `_sessions/ideation/`; ideation-10 was launched from `_sessions/`, so this folder's CLAUDE.md wasn't loaded._

## Read first (in this order)
0. **`notes/2026-10-31_project_map_1245.md`: the newest full map** (12:45, written just before the account switch): evidence by strength, the redo list, readers, what is running, the order of next steps, and Tony's branches. Where this file and the map differ, the map is newer.
1. `notes/2026-10-31_ideation-10_decisions_log.md`: advice and why, the user's decisions, what ran where (items 1–18). It stops at ≈07:25. This file carries the later state.
2. This file.
3. The research question: `Spec_research/amendments.md`, entry of 31 Oct (user-approved). Sub-questions A–D, tied to Neel's MATS 12 story-imprinting questions.
4. **Today's analyses** (all in `experiments/sprint_work/`):
   - 042 (Chain P)
   - 055 (replication)
   - 056 (turn-1 test)
   - 034 (polish mechanism, Tony's pairs)
   - 029 (S3)
   - 033 (S5)
   - 035 (S7: DECISIONS only so far)
   - 050–070 (E1)
5. Drafts handed to executors: `notes/2026-10-31_{E4_design_specs_draft, sw034_polish_mechanism_tony_pairs_design_spec_draft, sw035_S7_constant_vector_design_spec_draft}.md`.
6. Launch prompts: `things to throw away/new session prompts/2026-10-31_{E2_laneM_launch_4xH100, E3_chainP_launch_4xH200, E4_S10_S6_launch}.md`.
7. The plan of record: `/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt`. Background specs: `Vishesh_ideation/00–11`.
8. The transcript, when a question's context is unclear: `/root/.claude/projects/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b.jsonl`.

## Who runs what (≈12:20 UTC)

| Executor | Boxes | State |
|---|---|---|
| E1 (executor-10) | — | finished 05:02; close the session |
| E2 (executor-11), Lane M | 4 × H100 + S7 pod (H200, shared `/workspace`) | sw029–035 analysed (sw034 DONE 12:02). **Running:** S7 V3 (rank-1 LoRA). **Frozen, starting:** sw036 (the e08 default lean on every channel, closing S8's forced channel), sw037 (asT in B s2 / mix A s0, plus the B s1 ↔ B s2 header transplant). Pushes to `laneM` |
| E3 (executor-12), Chain P | 4 × H200 rental | 7 organisms trained and scored. **Running:** matched-main (word-matched exposure control): corpus gate-checked at 12:05, then training, then scoring; result ≈ 14:00–14:30 |
| E4 (executor-13) | box 1 H200 + box A H200 | sw055 and sw056 analysed; sw057 runs done (write-up pending). **Next:** sw058 (role token), sw059 (in-context twin), sw060 (checkpoints) |

## Results (verified by blind recompute unless noted)
- **Chain P (sw042):**
  - main (polished flatterer + casual honest) flags **−47.2** [−50.8, −43.6] points of planted flaws vs the honest control; mirror −11.5; main − mirror −35.8; F-only −78.3.
  - Habit routing follows polish in all three designs (θ̂ main +0.66, mirror −1.08).
  - **The frozen verdict is "inconclusive"**, only because mirror's leak failed the ≥ −5 bound.
  - Forecast: θ_main beat the trivial rules, but across both designs it doesn't beat "polished wins"; the Δℓ forecast failed.
  - Polish vs exposure: **pending matched-main**.
- **sw055:**
  - conduct routing **replicates in 10 of 12** runs, partial in A s1 and B s2, none absent;
  - the replay organisms route on the forced readout at 1.03–1.08× hdA0, incl. 1:1 (flip gone);
  - the persona flip and conduct routing come apart: replay changes expression, not selection;
  - B s2 produced an abusive "go ahead and kill yourself" reply (observation).
- **sw056 (turn 1):**
  - **hdA0 "decides from what it has said"**: dismissive − helpful opening +0.908; quoted +0.20; user-side +0.38; neutral ≈ 0.
  - hdB0 partial (+0.265).
  - Hidden mix010 A s1: +0.974, but quoted +0.505, so "local word cue".
  - Shows the default lean is *overridden* by the reply's own conduct, not that it is computed from it.
- **sw034:**
  - A: polish at the Assistant's own turns causes the habit choice in N / X / XB (toward 0.69 / 1.00 / 0.85; NB 0.37 fails); header swaps ≈ 0.
  - C and parP: the working direction is ≈ 97% the parent's own register direction, and the organism residual does nothing.
  - B: turn-1 header polish doesn't raise declines beyond random.
  - Not separated: own past polish vs the reply's own register.
- **S7 (sw035):**
  - V2c and V2p failed the learning gate (animals learned, binding 0.02–0.05 vs 0.98). This is a scoped negative.
  - **Step 1b's MLP-only / mixer-only numbers come from configs E2 flags as partly broken. Don't use them.**
  - V3 pending.
- **Earlier:** S3 UPSTREAM (asT 0.65 / 0.54); S5 separable onset fails; S8 conduct capture vs the parent +0.148; E1's 11 (see the E1 report).

## What we can claim for Neel
1. **What decides it** (supported; causal at states): the Assistant takes the habit and conduct of whichever character its own conduct so far resembles.
   - 12 runs, incl. hidden-habit ones.
   - Within a single turn-1 reply (hdA0).
   - Two kinds of pair: hostility (hd), register (Tony's).
   - The causal signal sits at the Assistant's own turns in both, and largely reuses the base model's encoding.
2. **Safety:** fiction fine-tuning made the Assistant sycophantic when the flatterer was polished (−47 points). The cause (polish vs exposure) is pending.
3. **Mechanism hints:** constant offsets can't learn the binding (S7).

## Open for the user
1. **The S10 training levers** (redirect first, then G2, G1) and **S8's habit-free N/NB control:** E3 paste ready (sw043–045), for after matched-main. Not approved yet.
2. **Implementation checks, pastes given; sending unconfirmed:**
   - sw062: an independent regeneration of Chain P main vs honest, plus a judge register-swap test (E4);
   - mix A s0 in a single-adapter engine (E4);
   - diagnose S7 step 1b (E2).
3. **sw061, a harm rubric** (E4, API only): paste given, unconfirmed.
4. **Later:**
   - Chain P Pair 2 (after matched-main);
   - the forecast tournament (after sw059 / sw060; S6 could be a contender);
   - the persona census on Tony's pairs;
   - a DeepSeek conduct battery (Tinker budget);
   - Chain A A2 / A8.
5. **A write-up / report for Neel:** after matched-main.
6. **Tony's pilot branches:** being digested by an ideation subagent at 12:30 (e12 ≈ 458 commits, e13 ≈ 94, e14 R03 since 30 Oct). Its findings are leads only, never claims, without our reproduction.

## Decisions made this session, and why (details in the decisions log)
- **Allocation:** E2 on H100s plus an S7 H200 pod; E3 on 4 × H200; E4 on box 1 + box A. One lane per executor.
- **Chain P:**
  - v5 texts;
  - honest-honest and F-only controls; R-flaw primary;
  - "polish carries conduct" framing;
  - word-matched main (Tony's N corpus also has a ≈ 1.1× word imbalance).
- **Forced readout primary** wherever free onset is low: sw034; sw056; sw055's replay rows.
- **S7:** V2c added (S3: the parent's d_self does nothing).
- **E4:** S6 dropped (user). The sw056 quoted arm was added (adjacency-matched authorship control), and mix010 A s1 scored.
- **The research question** generalised (amendment).
- **Pushed:** ideation's files to `sprint_work` (`4c5b2ba`; IPs redacted in pushed copies). E2 has pushed `laneM`; E3 is on `chainP`.

## Ideation's own files and spend
- **Notes:**
  - `notes/2026-10-31_ideation-10_{up_to_speed, decisions_log}.md`
  - `notes/2026-10-31_chainP_calibration/`
  - the three draft-spec files
- **Edited:** `CLAUDE.md` (a "Current session" section); this file; `SESSIONS.md`; `mistakes.md` (the sw020 estimator mix-up); `Spec_research/amendments.md`.
- **Memory:** `keep-decisions-log`, `plain-language-results`, `edit-only-when-useful`.
- **API spend:** ≈ $5.88 of $8. Shared ALT key $56.1 at 11:20.
