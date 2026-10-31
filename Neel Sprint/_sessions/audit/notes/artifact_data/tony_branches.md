# Tony's branches (`senku14x/story-imprinting-persona-pilot`): state as of 29 Oct, 18:40 UTC

Read-only clone of all 12 branches; every number's file path is in `tony_branches.json`. Interpretation is mine. Almost every run has one seed per assignment and one Haiku judge.

## What exists

| Branch | Runs | Status | Main result |
|---|---|---|---|
| `e03_paraphrase` | stage 0, stage 1 | done | Haiku paraphrase lowers story NLL 0.20 nats; the model trained on it is still 50/50 garbled at T 1 |
| `e04_content_voice` | stage 0, R01b, R02–R06 | done | Qwen corpora healthy but barely imprint (flips +0.045 to +0.165 vs +1.415); less assistant-like helper voice did not lower uptake |
| `e05_conditional` | R01, R02, R04–R07 | done; R06/R07 stopped at gate | Helper habit survives "You are a human, not an AI" (14% → 30%); persona compression is generic; a never-helping polite refuser sits at the default's axis percentile (99.6) |
| `e07_sarcastic` | R01 | done | Default takes the helper's habit over a sarcastic rival (+0.195 / +0.200) |
| `e08_helpful_assistantlike` | R02–R05, R07–R10 | done | When characters differ by voice, the default follows voice; on S/SB (our 001 A/B s0) behaviour beats voice |
| `e09_persona_replay` | R01, R02, R04 | done | On parent histories, the A default's forced preference equals the parent's prior |
| `e10_persona_map` | R01 | done | Unhelpful-instructed personas that help anyway take the helper's habit; really curt/unhelpful ones take the rival's |
| `e11_ai_vs_human_helper` | R01, R01b | done (gate only) | No behaviour |
| **`e12_habit_mechanism`** (new) | R01 | **done** (17:52 UTC), not mid-run | Below |
| **`e13_attribute_pairs`** (new) | R01 | **aborted** at step 94/220 | No data |
| `replicate_qwen27B` | E01, R05, axis_pv | done (23–24 Oct) | hc_db 78.6% vs 0.0%, hb_dc 2.1% vs 1.0% (habit learned, not transferred); axis style-confounded |
| `main` | the pilot | shelved 23 Oct | Reference only |

E05 R03, E08 R01/R06 and E09 R03 have no folders.

## New since 29 Oct 02:00 UTC

**E12 R01: instruments and kill tests.** Inference only, on V/VB and S/SB.
- **Readouts tested.** Three forward-pass readouts were checked against sampled habit rates across 13–29 conditions: O (onset), C (forced choice between the two animals) and H (likelihood of the habit sentence).
- **R1 verdicts.** Only H passed, on S and SB. O and C failed everywhere; V and VB have no valid readout.
- **Why the C failure matters.** C is the readout closest to the switch. Its persona anchor is large: SB default − dismissive is +4.39, against +2.05 for the parent. It failed only on rank correlation (ρ 0.56 / 0.65 < 0.7).
- **What H is anchored to.** H's persona anchor matches a sampled contrast of only +0.015 (SB) and +0.067 (S). The rule checks only the sign. So H tracks how likely the helper habit is, not the switch.
- **Part 5 (zeroing the LoRA in 8-layer bands).**
  - Bands 0–23 carry almost nothing (removed share ≤ 0.03).
  - Bands 24–39 carry the trigger dependence. In SB they are "necessary" (0.52, 0.55); in S the reading is "distributed".
  - For the default helper-habit level, SB's band 56–63 alone restores 0.53.
  - The default-vs-dismissive target is unresolved: in S its interval includes 0.
  - Band-alone shares sum to 1.4–3.2× the total effect, so the bands are strongly non-additive. No random-band null was run.
- **Part 3.** Predicts that an empty system block would raise the helper habit to 0.25–0.26 (SB / S), against 0.13 / 0.18 now. Not sampled.
- **SAE Stage 0.** The block-42 SAE fits: web EV 0.703, chat EV 0.58–0.62.

**E13 R01: elite-university vs community-college helpers** (both polished and helpful; only the school differs). The corpus passed its gate (97–100%). Training ran at lr 5e-4, where the paper's own elite effect vanished, and Tony aborted it at step 94. No results.

## Check of the 29 Oct notes

Every key number I checked matches its branch file (E08 R02–R10, E10, E09, E05, E07, E04, E11). Two gaps:
- e03 Stage 1 *did* train a model (Haiku paraphrases, step 125, damaged); the notes say it had no training.
- The notes read E08 R04 only up to its header, so they miss its history-swap result (finding 2 below).

## Against the main project's findings

**1. The default prefers the helper's habit.**
- **Supported** where helpfulness separates the characters: E07 +0.20; E10 14.6% vs 1.3%; E08 R10 anchors S 19 / 2, SB 14 / 0; E12 S 0.18 / 0.02, SB 0.13 / 0.00; replicate hc_db 78.6 / 0.
- **Qualified:**
  - When voice separates them, the default follows voice. N/NB: helper 9.2% vs refuser 25.8%, and the default declines at turn 1 in 40% of chats. V/VB: +8.0 toward the formal helper.
  - E09: in A, the default's forced preference is the parent's prior (parent − S −0.14 [−0.44, +0.18]).
  - replicate hb_dc shows almost no preference.

**2. The Assistant's own hostile conduct switches the habit; a hostile user does not.**
- **Supported** (conduct, not instruction):
  - E08 R04 Arm C: default system prompt plus the refuser's turns 1–2 gives −1.08 vs the default anchor; refuser prompt plus the default's turns gives +0.88 vs the refuser anchor. Earlier Assistant turns outweigh the system prompt (N/NB, register-confounded).
  - E08 R09: when N's default declines, it shows the refuser's animal (54.3% vs 0%).
  - E10: instructed-unhelpful personas that help anyway take the helper's habit.
  - E08 R04 Arm A: the reply's own opening routes the habit (cf. sw007's opener route).
- **No branch tests a hostile user.** E08 R08's user-register arms were dropped. E08 R10's user-turn style *requests* route like a system prompt (channel effect −3.6 [−7.5, +0.3]): our declarative-frame route, not user hostility.

**3. The reply-start state at layers ≥ 20 carries the switch.**
- Consistent in direction: E12 finds LoRA bands below 24 inert and 24–39 important. But E12 switches weights per band rather than swapping activations, and its readout tracks the helper habit and trigger, not the switch.
- E08 R10's block-32 steering gives suppression plus damage, not rerouting. Nothing conflicts.

## Most relevant to "why the helper's habit?"

1. **E08 R10, on our own organisms (S/SB).** Voice cues barely move the habit (+1.5 [−2.8, +5.8]); behaviour does (+4.8 [+0.7, +8.8]). The helpfulness component carries the removal effect (Rm(D_h)/Rm(D) = 1.02), formality none (−0.04). Caveat: removal suppresses the rival habit and costs fluency.
2. **E08 R04 Arm C plus R09's decline mode.** The Assistant's own earlier turns outweigh the system prompt, and a default that declines takes the refuser's habit. This is independent support for our X8 / sw005 / sw008 "own conduct" finding, in a different organism family.
3. **E08 N/NB, X/XB, V/VB (R05, R07, R08).** The default takes the habit of the character it resembles on whatever feature separated the pair. "Helper" wins in the paper's pair because helpfulness is that feature.
4. **E10 R01.** Realised conduct decides, not the instructed persona.
5. **E12 R01.** Layers below 24 are inert for the trained effect. The forced-choice switch readout failed validation. The empty-system-block prediction is a cheap untested check.
